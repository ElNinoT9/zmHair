"""用户角色常量与保存时策略。"""

VALID_USER_ROLES = frozenset({'admin', 'employee', 'waixie'})


def apply_role_policy(user) -> None:
    """外协账号固定为理发师，仅使用理发师前台。"""
    if user.role == 'waixie':
        user.is_barber = True
