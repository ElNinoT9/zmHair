from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.models import Appointment, BarberSchedule, Notification, SystemConfig, User
from app.models.models import DEFAULT_TIME_PERIOD, TIME_PERIODS, VALID_TIME_PERIODS
from app.schemas.common import AppointmentCreateRequest, AppointmentStatusRequest, ScheduleUpdateRequest
from app.utils.response import ApiException

router = APIRouter(prefix='/mobile', tags=['移动端'])


def get_config_value(db: Session, key: str, default: str = '') -> str:
    config = db.query(SystemConfig).filter_by(config_key=key).first()
    return config.config_value if config else default


@router.get('/barbers')
def list_barbers(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    barbers = db.query(User).filter_by(is_barber=True, is_active=True).all()
    return {'code': 0, 'data': [b.to_dict() for b in barbers]}


@router.get('/barbers/{barber_id}/dates')
def get_barber_dates(
    barber_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    barber = db.query(User).filter_by(id=barber_id, is_barber=True, is_active=True).first()
    if not barber:
        raise ApiException(404, '理发师不存在')

    today = datetime.now().date()
    schedules = (
        db.query(BarberSchedule)
        .filter(BarberSchedule.barber_id == barber_id, BarberSchedule.service_date >= today)
        .order_by(BarberSchedule.service_date)
        .all()
    )
    return {'code': 0, 'data': [s.to_dict() for s in schedules]}


@router.post('/appointments')
def create_appointment(
    body: AppointmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment_date_str = body.appointment_date.strip()
    if not body.barber_id or not appointment_date_str:
        raise ApiException(400, '请选择理发师和预约日期')

    try:
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ApiException(400, '日期格式错误')

    if appointment_date < datetime.now().date():
        raise ApiException(400, '不能预约过去的日期')

    barber = db.query(User).filter_by(id=body.barber_id, is_barber=True, is_active=True).first()
    if not barber:
        raise ApiException(404, '理发师不存在')

    schedule = db.query(BarberSchedule).filter_by(
        barber_id=body.barber_id, service_date=appointment_date
    ).first()
    if not schedule:
        raise ApiException(400, '该日期理发师未开放预约')

    existing = db.query(Appointment).filter_by(
        employee_id=current_user.id,
        barber_id=body.barber_id,
        appointment_date=appointment_date,
        status='pending',
    ).first()
    if existing:
        raise ApiException(400, '您已有该日期的待确认预约')

    confirmed = db.query(Appointment).filter_by(
        employee_id=current_user.id,
        barber_id=body.barber_id,
        appointment_date=appointment_date,
        status='confirmed',
    ).first()
    if confirmed:
        raise ApiException(400, '您已有该日期的已确认预约')

    appointment = Appointment(
        employee_id=current_user.id,
        barber_id=body.barber_id,
        appointment_date=appointment_date,
        remark=body.remark.strip(),
        status='pending',
    )
    db.add(appointment)
    db.flush()

    db.add(Notification(
        user_id=body.barber_id,
        title='新预约通知',
        content=f'{current_user.name}（{current_user.employee_id}）预约了 {appointment_date_str} 的理发服务',
        related_id=appointment.id,
    ))
    db.commit()
    db.refresh(appointment)
    return {'code': 0, 'message': '预约成功，请等待理发师确认', 'data': appointment.to_dict()}


@router.get('/my-appointments')
def my_appointments(
    status: str = Query(default=''),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Appointment).filter_by(employee_id=current_user.id)
    if status.strip():
        query = query.filter_by(status=status.strip())
    appointments = query.order_by(Appointment.appointment_date.desc()).all()
    return {'code': 0, 'data': [a.to_dict() for a in appointments]}


@router.post('/my-appointments/{apt_id}/cancel')
def cancel_appointment(
    apt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter_by(id=apt_id, employee_id=current_user.id).first()
    if not appointment:
        raise ApiException(404, '预约不存在')
    if appointment.status in ('completed', 'cancelled'):
        raise ApiException(400, '该预约无法取消')

    appointment.status = 'cancelled'
    db.commit()
    return {'code': 0, 'message': '已取消预约'}


@router.get('/barber/schedules')
def get_my_schedules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_barber:
        raise ApiException(403, '无理发师权限')

    today = datetime.now().date()
    schedules = (
        db.query(BarberSchedule)
        .filter(BarberSchedule.barber_id == current_user.id, BarberSchedule.service_date >= today)
        .order_by(BarberSchedule.service_date)
        .all()
    )
    return {'code': 0, 'data': [s.to_dict() for s in schedules]}


@router.post('/barber/schedules')
def set_schedules(
    body: ScheduleUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_barber:
        raise ApiException(403, '无理发师权限')

    min_days = int(get_config_value(db, 'schedule_min_days', '7'))
    max_days = int(get_config_value(db, 'schedule_max_days', '14'))

    today = datetime.now().date()
    min_date = today + timedelta(days=1)
    max_date = today + timedelta(days=max_days)

    valid_dates = []
    for d in body.dates:
        try:
            date_obj = datetime.strptime(d, '%Y-%m-%d').date()
            if date_obj < min_date or date_obj > max_date:
                continue
            valid_dates.append(date_obj)
        except ValueError:
            continue

    db.query(BarberSchedule).filter(
        BarberSchedule.barber_id == current_user.id,
        BarberSchedule.service_date >= today,
    ).delete()

    for date_obj in valid_dates:
        db.add(BarberSchedule(barber_id=current_user.id, service_date=date_obj))

    db.commit()
    return {'code': 0, 'message': f'已设置 {len(valid_dates)} 个可服务日期'}


@router.get('/barber/appointments')
def barber_appointments(
    status: str = Query(default=''),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_barber:
        raise ApiException(403, '无理发师权限')

    query = db.query(Appointment).filter_by(barber_id=current_user.id)
    if status.strip():
        query = query.filter_by(status=status.strip())
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.created_at.desc()).all()
    return {'code': 0, 'data': [a.to_dict() for a in appointments]}


@router.get('/barber/last-period')
def get_barber_last_period(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user.is_barber:
        raise ApiException(403, '无理发师权限')
    period = current_user.last_time_period or DEFAULT_TIME_PERIOD
    if period not in VALID_TIME_PERIODS:
        period = DEFAULT_TIME_PERIOD
    return {
        'code': 0,
        'data': {
            'time_period': period,
            'time_period_text': TIME_PERIODS[period],
            'options': [{'value': k, 'label': v} for k, v in TIME_PERIODS.items()],
        },
    }


@router.put('/barber/appointments/{apt_id}/status')
def update_appointment_status(
    apt_id: int,
    body: AppointmentStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_barber:
        raise ApiException(403, '无理发师权限')

    appointment = db.query(Appointment).filter_by(id=apt_id, barber_id=current_user.id).first()
    if not appointment:
        raise ApiException(404, '预约不存在')
    if body.status not in ('confirmed', 'completed', 'cancelled'):
        raise ApiException(400, '无效的状态')

    if body.status == 'confirmed':
        period = (body.time_period or '').strip() or current_user.last_time_period or DEFAULT_TIME_PERIOD
        if period not in VALID_TIME_PERIODS:
            raise ApiException(400, '请选择预约时段')
        appointment.time_period = period
        current_user.last_time_period = period
        employee = appointment.employee
        period_text = TIME_PERIODS[period]
        db.add(Notification(
            user_id=appointment.employee_id,
            title='预约已确认',
            content=(
                f'{current_user.name} 已确认您 {appointment.appointment_date.strftime("%Y-%m-%d")} '
                f'的预约，安排时段：{period_text}'
            ),
            related_id=appointment.id,
        ))

    appointment.status = body.status
    db.commit()
    db.refresh(appointment)
    return {'code': 0, 'message': '状态已更新', 'data': appointment.to_dict()}


@router.get('/notifications')
def get_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifications = (
        db.query(Notification)
        .filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread = db.query(Notification).filter_by(user_id=current_user.id, is_read=False).count()
    return {
        'code': 0,
        'data': {
            'list': [n.to_dict() for n in notifications],
            'unread_count': unread,
        },
    }


@router.post('/notifications/{notif_id}/read')
def mark_notification_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter_by(id=notif_id, user_id=current_user.id).first()
    if notification:
        notification.is_read = True
        db.commit()
    return {'code': 0, 'message': '已标记已读'}


@router.post('/notifications/read-all')
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.commit()
    return {'code': 0, 'message': '全部已读'}


@router.get('/config/public')
def public_config(db: Session = Depends(get_db)):
    configs = db.query(SystemConfig).all()
    return {'code': 0, 'data': {c.config_key: c.config_value for c in configs}}
