"""用户 Excel 导入/导出/模板"""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from openpyxl import Workbook, load_workbook
from sqlalchemy.orm import Session

from app.models.models import User
from app.services.employee_import import parse_employee_id_from_cell

USER_SHEET_HEADERS = ['工号', '姓名', '角色', '理发师', '状态']

ROLE_LABEL = {'admin': '管理员', 'employee': '员工'}
ROLE_PARSE = {'管理员': 'admin', 'admin': 'admin', '员工': 'employee', 'employee': 'employee'}


def _bool_label(value: bool) -> str:
    return '是' if value else '否'


def _parse_bool(raw) -> bool | None:
    if raw is None or str(raw).strip() == '':
        return None
    s = str(raw).strip().lower()
    if s in ('是', 'yes', 'true', '1', 'y', '正常'):
        return True
    if s in ('否', 'no', 'false', '0', 'n', '停用'):
        return False
    return None


def _parse_role(raw) -> str | None:
    if raw is None or str(raw).strip() == '':
        return None
    key = str(raw).strip().lower()
    if key in ROLE_PARSE:
        return ROLE_PARSE[key]
    return ROLE_PARSE.get(str(raw).strip())


def user_row_to_cells(user: User) -> list:
    return [
        user.employee_id,
        user.name,
        ROLE_LABEL.get(user.role, user.role),
        _bool_label(user.is_barber),
        '正常' if user.is_active else '停用',
    ]


def build_users_workbook(users: list[User]) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = '用户列表'
    ws.append(USER_SHEET_HEADERS)
    for user in users:
        ws.append(user_row_to_cells(user))
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def build_template_workbook() -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = '导入模板'
    ws.append(USER_SHEET_HEADERS)
    ws.append(['094001', '张三', '员工', '否', '正常'])
    ws.append(['094002', '李四', '员工', '是', '正常'])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


@dataclass
class ParsedUserRow:
    line: int
    employee_id: str
    name: str
    role: str
    is_barber: bool
    is_active: bool


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] | None = None

    def to_dict(self):
        return {
            'created': self.created,
            'updated': self.updated,
            'skipped': self.skipped,
            'errors': self.errors or [],
        }


def _header_map(first_row: list) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for idx, cell in enumerate(first_row):
        key = str(cell).strip() if cell is not None else ''
        if key:
            mapping[key] = idx
    return mapping


def _cell(row: tuple, col_map: dict[str, int], *names: str):
    for name in names:
        if name in col_map:
            idx = col_map[name]
            if idx < len(row):
                return row[idx]
    return None


def parse_users_from_excel(content: bytes) -> tuple[list[ParsedUserRow], list[str]]:
    try:
        wb = load_workbook(BytesIO(content), read_only=True, data_only=True)
    except Exception as exc:
        return [], [f'无法读取 Excel，请使用 .xlsx 模板：{exc}']
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    try:
        header_row = next(rows_iter)
    except StopIteration:
        return [], ['Excel 文件为空']

    col_map = _header_map(list(header_row))
    if '工号' not in col_map or '姓名' not in col_map:
        return [], ['缺少必填列：工号、姓名']

    parsed: list[ParsedUserRow] = []
    errors: list[str] = []

    for line_no, row in enumerate(rows_iter, start=2):
        if not row or all(c is None or str(c).strip() == '' for c in row):
            continue

        raw_id = _cell(row, col_map, '工号')
        raw_name = _cell(row, col_map, '姓名')
        employee_id = parse_employee_id_from_cell(raw_id)
        name = str(raw_name or '').strip()

        if not employee_id or not name:
            errors.append(f'第 {line_no} 行：工号或姓名为空，已跳过')
            continue

        role_raw = _cell(row, col_map, '角色')
        role = _parse_role(role_raw) or 'employee'

        barber_raw = _cell(row, col_map, '理发师')
        is_barber = _parse_bool(barber_raw)
        if is_barber is None:
            is_barber = False

        active_raw = _cell(row, col_map, '状态')
        is_active = _parse_bool(active_raw)
        if is_active is None:
            is_active = True

        parsed.append(
            ParsedUserRow(
                line=line_no,
                employee_id=employee_id,
                name=name,
                role=role,
                is_barber=is_barber,
                is_active=is_active,
            )
        )

    wb.close()
    return parsed, errors


def import_users_from_rows(db: Session, rows: list[ParsedUserRow], mode: str) -> ImportResult:
    if mode not in ('update', 'overwrite'):
        mode = 'update'

    result = ImportResult(errors=[])
    seen_ids: set[str] = set()

    for row in rows:
        if row.employee_id in seen_ids:
            result.errors.append(f'第 {row.line} 行：工号 {row.employee_id} 在文件中重复，已跳过')
            result.skipped += 1
            continue
        seen_ids.add(row.employee_id)

        if row.employee_id == 'admin' and row.role != 'admin':
            result.errors.append(f'第 {row.line} 行：不能修改 admin 账号角色，已跳过')
            result.skipped += 1
            continue

        user = db.query(User).filter_by(employee_id=row.employee_id).first()

        if user:
            if user.role == 'admin' and row.role != 'admin':
                result.errors.append(f'第 {row.line} 行：不能修改管理员账号，已跳过')
                result.skipped += 1
                continue

            user.name = row.name
            if mode == 'overwrite':
                user.role = row.role
                user.is_barber = row.is_barber
                user.is_active = row.is_active
            result.updated += 1
        else:
            if row.role == 'admin':
                result.errors.append(f'第 {row.line} 行：不能通过导入新建管理员，已跳过')
                result.skipped += 1
                continue
            user = User(
                employee_id=row.employee_id,
                name=row.name,
                role=row.role,
                is_barber=row.is_barber,
                is_active=row.is_active,
            )
            user.set_password(row.employee_id)
            db.add(user)
            result.created += 1

    db.commit()
    return result
