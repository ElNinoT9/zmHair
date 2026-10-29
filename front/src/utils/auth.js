import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000
})

export function quickLogin(employeeId) {
  return api.post('/auth/quick-login', { employee_id: employeeId })
}

export function lookupEmployee(employeeId) {
  return api.get('/auth/lookup', { params: { employee_id: employeeId } })
}
