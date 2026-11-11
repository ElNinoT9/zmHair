export const ROLE_WAIXIE = 'waixie'

const ROLE_LABELS = {
  admin: '管理员',
  employee: '员工',
  waixie: '外协'
}

export function roleLabel(role) {
  return ROLE_LABELS[role] || role || '员工'
}

export function roleTagType(role) {
  if (role === 'admin') return 'danger'
  if (role === 'waixie') return 'warning'
  return 'info'
}

/** 是否显示移动端「员工 / 理发师」切换（仅内部员工且兼理发师） */
export function canSwitchMobileView(user) {
  return !!(user && user.is_barber && user.role === 'employee')
}

export function isWaixie(user) {
  return !!(user && user.role === ROLE_WAIXIE)
}

export function isAdminUser(user) {
  return !!(user && user.role === 'admin')
}

/** 用户管理表格「角色」列（管理员单独展示，此处显示 —） */
export function businessRoleLabel(user) {
  if (!user || user.role === 'admin') return '—'
  return roleLabel(user.role)
}

export function businessRoleTagType(user) {
  if (!user || user.role === 'admin') return 'info'
  return roleTagType(user.role)
}
