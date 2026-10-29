from pydantic import BaseModel


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class QuickLoginRequest(BaseModel):
    employee_id: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserCreateRequest(BaseModel):
    employee_id: str
    name: str
    role: str = 'employee'
    is_barber: bool = False
    password: str | None = None


class UserUpdateRequest(BaseModel):
    name: str | None = None
    role: str | None = None
    is_barber: bool | None = None
    is_active: bool | None = None
    password: str | None = None


class ConfigUpdateRequest(BaseModel):
    configs: list[dict]


class AppointmentCreateRequest(BaseModel):
    barber_id: int
    appointment_date: str
    remark: str = ''


class ScheduleUpdateRequest(BaseModel):
    dates: list[str]


class AppointmentStatusRequest(BaseModel):
    status: str
    time_period: str | None = None
