import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'

Vue.use(VueRouter)

const originalPush = VueRouter.prototype.push
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => {
    if (err.name !== 'NavigationDuplicated' && !err.message.includes('Navigation cancelled')) {
      return Promise.reject(err)
    }
  })
}

const originalReplace = VueRouter.prototype.replace
VueRouter.prototype.replace = function replace(location) {
  return originalReplace.call(this, location).catch(err => {
    if (err.name !== 'NavigationDuplicated' && !err.message.includes('Navigation cancelled')) {
      return Promise.reject(err)
    }
  })
}

const AdminLayout = () => import('@/views/admin/Layout.vue')
const MobileLayout = () => import('@/views/mobile/Layout.vue')

const routes = [
  { path: '/', redirect: '/m/book' },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true },
    redirect: '/admin/dashboard',
    children: [
      { path: 'dashboard', name: 'Dashboard', component: () => import('@/views/admin/Dashboard.vue'), meta: { title: '工作台' } },
      { path: 'users', name: 'Users', component: () => import('@/views/admin/Users.vue'), meta: { title: '用户管理' } },
      { path: 'appointments', name: 'Appointments', component: () => import('@/views/admin/Appointments.vue'), meta: { title: '预约台账' } },
      { path: 'config', name: 'Config', component: () => import('@/views/admin/Config.vue'), meta: { title: '系统配置' } }
    ]
  },
  {
    path: '/m/login',
    name: 'MobileLogin',
    component: () => import('@/views/mobile/Login.vue'),
    meta: { guest: true, mobileGuest: true }
  },
  {
    path: '/m',
    component: MobileLayout,
    meta: { requiresAuth: true },
    redirect: '/m/book',
    children: [
      { path: 'home', name: 'MobileHome', component: () => import('@/views/mobile/Home.vue'), meta: { title: '首页' } },
      { path: 'book', name: 'MobileBook', component: () => import('@/views/mobile/Book.vue'), meta: { title: '预约理发' } },
      { path: 'my', name: 'MobileMy', component: () => import('@/views/mobile/MyAppointments.vue'), meta: { title: '我的预约' } },
      { path: 'barber', name: 'BarberHome', component: () => import('@/views/mobile/BarberHome.vue'), meta: { title: '理发师', requiresBarber: true } },
      { path: 'barber/schedule', name: 'BarberSchedule', component: () => import('@/views/mobile/BarberSchedule.vue'), meta: { title: '排班设置', requiresBarber: true } },
      { path: 'barber/orders', name: 'BarberOrders', component: () => import('@/views/mobile/BarberOrders.vue'), meta: { title: '预约订单', requiresBarber: true } },
      { path: 'notifications', name: 'Notifications', component: () => import('@/views/mobile/Notifications.vue'), meta: { title: '消息通知' } }
    ]
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

async function ensureMobileLogin() {
  if (store.getters.isLoggedIn) return true
  return store.dispatch('autoLogin')
}

router.beforeEach(async (to, from, next) => {
  const isLoggedIn = store.getters.isLoggedIn
  const isAdmin = store.getters.isAdmin
  const isBarber = store.getters.isBarber

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const requiresBarber = to.matched.some(record => record.meta.requiresBarber)
  const isGuest = to.matched.some(record => record.meta.guest)
  const isMobileGuest = to.matched.some(record => record.meta.mobileGuest)

  if (isMobileGuest && !isLoggedIn) {
    const ok = await ensureMobileLogin()
    if (ok) {
      next(store.getters.isBarber ? '/m/barber' : '/m/book')
      return
    }
  }

  if (isGuest) {
    if (isLoggedIn && to.path === '/m/login' && !isAdmin) {
      next(store.getters.isBarber ? '/m/barber' : '/m/book')
      return
    }
    if (isLoggedIn && to.path === '/admin/login' && isAdmin) {
      next('/admin/dashboard')
      return
    }
    next()
    return
  }

  if (requiresAdmin) {
    if (!isLoggedIn) {
      next('/admin/login')
      return
    }
    if (!isAdmin) {
      next(store.getters.isBarber ? '/m/barber' : '/m/book')
      return
    }
  }

  if (requiresAuth) {
    if (!isLoggedIn) {
      const ok = await ensureMobileLogin()
      if (!ok) {
        next('/m/login')
        return
      }
    }
    if (requiresBarber && !store.getters.isBarber) {
      next('/m/book')
      return
    }
  }

  next()
})

export default router
