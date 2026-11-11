import Vue from 'vue'
import Vuex from 'vuex'
import { quickLogin } from '@/utils/auth'
import { ROLE_WAIXIE, canSwitchMobileView } from '@/constants/userRole'

Vue.use(Vuex)

const TOKEN_KEY = 'zmhair_token'
const USER_KEY = 'zmhair_user'
const SAVED_EMPLOYEE_KEY = 'zmhair_saved_employee_id'
const MOBILE_VIEW_KEY_PREFIX = 'zmhair_mobile_view_'

function resolveMobileViewMode(user) {
  if (!user) return 'employee'
  if (user.role === ROLE_WAIXIE) return 'barber'
  if (!user.is_barber) return 'employee'
  const saved = localStorage.getItem(MOBILE_VIEW_KEY_PREFIX + user.employee_id)
  if (saved === 'employee' || saved === 'barber') return saved
  return 'barber'
}

const storedUser = JSON.parse(localStorage.getItem(USER_KEY) || 'null')

export default new Vuex.Store({
  state: {
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: storedUser,
    mobileViewMode: resolveMobileViewMode(storedUser),
    autoLoginPending: false
  },
  mutations: {
    SET_TOKEN(state, token) {
      state.token = token
      if (token) {
        localStorage.setItem(TOKEN_KEY, token)
      } else {
        localStorage.removeItem(TOKEN_KEY)
      }
    },
    SET_USER(state, user) {
      state.user = user
      if (user) {
        localStorage.setItem(USER_KEY, JSON.stringify(user))
      } else {
        localStorage.removeItem(USER_KEY)
      }
    },
    SET_AUTO_LOGIN_PENDING(state, pending) {
      state.autoLoginPending = pending
    },
    SET_MOBILE_VIEW_MODE(state, mode) {
      const next = mode === 'barber' ? 'barber' : 'employee'
      state.mobileViewMode = next
      const eid = state.user && state.user.employee_id
      if (eid) {
        localStorage.setItem(MOBILE_VIEW_KEY_PREFIX + eid, next)
      }
    }
  },
  actions: {
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      commit('SET_MOBILE_VIEW_MODE', resolveMobileViewMode(user))
      if (user && user.employee_id) {
        localStorage.setItem(SAVED_EMPLOYEE_KEY, user.employee_id)
      }
    },
    logout({ commit }) {
      commit('SET_TOKEN', '')
      commit('SET_USER', null)
      commit('SET_MOBILE_VIEW_MODE', 'employee')
      localStorage.removeItem(SAVED_EMPLOYEE_KEY)
    },
    setMobileViewMode({ commit, getters, state }, mode) {
      if (!canSwitchMobileView(state.user)) return
      if (mode === 'barber' && !state.user.is_barber) return
      commit('SET_MOBILE_VIEW_MODE', mode)
    },
    async autoLogin({ commit, dispatch, state }) {
      const savedId = localStorage.getItem(SAVED_EMPLOYEE_KEY)
      if (!savedId) return false
      if (state.token && state.user && state.user.employee_id === savedId) {
        return true
      }

      commit('SET_AUTO_LOGIN_PENDING', true)
      try {
        const res = await quickLogin(savedId)
        const payload = res.data
        if (payload.code !== 0) {
          dispatch('logout')
          return false
        }
        await dispatch('login', {
          token: payload.data.token,
          user: payload.data.user
        })
        return true
      } catch (e) {
        dispatch('logout')
        return false
      } finally {
        commit('SET_AUTO_LOGIN_PENDING', false)
      }
    }
  },
  getters: {
    isAdmin: state => state.user && state.user.role === 'admin',
    isWaixie: state => !!(state.user && state.user.role === ROLE_WAIXIE),
    isBarberCapable: state => canSwitchMobileView(state.user),
    isBarber: state => {
      const user = state.user
      if (!user) return false
      if (user.role === ROLE_WAIXIE) return true
      return !!(user.is_barber && state.mobileViewMode === 'barber')
    },
    defaultMobileRoute: (_state, getters) => (getters.isBarber ? '/m/barber' : '/m/book'),
    isLoggedIn: state => !!state.token,
    savedEmployeeId: () => localStorage.getItem(SAVED_EMPLOYEE_KEY) || ''
  }
})
