from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

STATUS_TEXT = {
    'pending': '待确认',
    'confirmed': '已确认',
    'completed': '已完成',
    'cancelled': '已取消',
}

TIME_PERIODS = {
    'morning': '上午',
    'afternoon': '下午',
    'evening': '晚上',
}

DEFAULT_TIME_PERIOD = 'morning'
VALID_TIME_PERIODS = set(TIME_PERIODS.keys())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(16), default='employee')
    is_barber: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_time_period: Mapped[str] = mapped_column(String(16), default=DEFAULT_TIME_PERIOD)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'name': self.name,
            'role': self.role,
            'is_barber': self.is_barber,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


class BarberSchedule(Base):
    __tablename__ = 'barber_schedules'
    __table_args__ = (UniqueConstraint('barber_id', 'service_date', name='uq_barber_date'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    barber_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    service_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    barber = relationship('User', backref='schedules')

    def to_dict(self):
        return {
            'id': self.id,
            'barber_id': self.barber_id,
            'barber_name': self.barber.name if self.barber else '',
            'service_date': self.service_date.strftime('%Y-%m-%d'),
        }


class Appointment(Base):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    barber_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    appointment_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default='pending')
    time_period: Mapped[str] = mapped_column(String(16), default='')
    remark: Mapped[str] = mapped_column(String(256), default='')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    employee = relationship('User', foreign_keys=[employee_id], backref='appointments_as_employee')
    barber = relationship('User', foreign_keys=[barber_id], backref='appointments_as_barber')

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'employee_name': self.employee.name if self.employee else '',
            'employee_no': self.employee.employee_id if self.employee else '',
            'barber_id': self.barber_id,
            'barber_name': self.barber.name if self.barber else '',
            'appointment_date': self.appointment_date.strftime('%Y-%m-%d'),
            'status': self.status,
            'status_text': STATUS_TEXT.get(self.status, self.status),
            'time_period': self.time_period or '',
            'time_period_text': TIME_PERIODS.get(self.time_period, '') if self.time_period else '',
            'remark': self.remark,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


class Notification(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(String(512), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_id: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    user = relationship('User', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'is_read': self.is_read,
            'related_id': self.related_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


class SystemConfig(Base):
    __tablename__ = 'system_config'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    config_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    config_value: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(String(128), default='')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'description': self.description,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
