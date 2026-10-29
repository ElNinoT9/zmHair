import Vue from 'vue'
import Vuex from 'vuex'
import { quickLogin } from '@/utils/auth'

Vue.use(Vuex)

const TOKEN_KEY = 'zmhair_token'
const USER_KEY = 'zmhair_user'
const SAVED_EMPLOYEE_KEY = 'zmhair_saved_employee_id'

export default new Vuex.Store({
  state: {
    token: localStorage.getItem(TOKEN_KEY) || '',
    user: JSON.parse(localStorage.getItem(USER_KEY) || 'null'),
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
    }
  },
  actions: {
    login({ commit }, { token, user }) {
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
      if (user && user.employee_id) {
        localStorage.setItem(SAVED_EMPLOYEE_KEY, user.employee_id)
      }
    },
    logout({ commit }) {
      commit('SET_TOKEN', '')
      commit('SET_USER', null)
      localStorage.removeItem(SAVED_EMPLOYEE_KEY)
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
    isBarber: state => state.user && state.user.is_barber,
    isLoggedIn: state => !!state.token,
    savedEmployeeId: () => localStorage.getItem(SAVED_EMPLOYEE_KEY) || ''
  }
})
