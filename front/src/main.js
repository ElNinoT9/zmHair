import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

import { Button, Tabbar, TabbarItem, NavBar, Cell, CellGroup, List, Tag, Empty, Toast, Dialog, Field, Form, Calendar, Popup, Badge, PullRefresh, Icon, Divider, NoticeBar, Tabs, Tab, Loading } from 'vant'
import 'vant/lib/index.css'

import '@/styles/global.scss'

Vue.use(ElementUI, { size: 'medium' })

Vue.use(Button).use(Tabbar).use(TabbarItem).use(NavBar).use(Cell).use(CellGroup)
  .use(List).use(Tag).use(Empty).use(Toast).use(Dialog).use(Field).use(Form)
  .use(Calendar).use(Popup).use(Badge).use(PullRefresh).use(Icon).use(Divider).use(NoticeBar).use(Tabs).use(Tab).use(Loading)

Vue.config.productionTip = false

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
