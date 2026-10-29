export const PERIOD_OPTIONS = [
  { value: 'morning', label: '上午' },
  { value: 'afternoon', label: '下午' },
  { value: 'evening', label: '晚上' }
]

export const DEFAULT_PERIOD = 'morning'

export function periodLabel(value) {
  const item = PERIOD_OPTIONS.find(p => p.value === value)
  return item ? item.label : ''
}
