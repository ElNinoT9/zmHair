<template>
  <div class="notifications-page">
    <van-nav-bar title="消息通知" left-arrow @click-left="$router.back()">
      <template #right>
        <span class="read-all" @click="markAllRead" v-if="unreadCount">全部已读</span>
      </template>
    </van-nav-bar>

    <van-pull-refresh v-model="refreshing" @refresh="loadData">
      <van-empty v-if="!list.length" description="暂无消息" />
      <div
        v-for="item in list"
        :key="item.id"
        class="notif-item"
        :class="{ unread: !item.is_read }"
        @click="markRead(item)"
      >
        <div class="notif-title">{{ item.title }}</div>
        <div class="notif-content">{{ item.content }}</div>
        <div class="notif-time">{{ item.created_at }}</div>
      </div>
    </van-pull-refresh>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'Notifications',
  data() {
    return {
      list: [],
      unreadCount: 0,
      refreshing: false
    }
  },
  created() { this.loadData() },
  methods: {
    async loadData() {
      const res = await request.get('/mobile/notifications')
      this.list = res.data.list
      this.unreadCount = res.data.unread_count
      this.refreshing = false
    },
    async markRead(item) {
      if (!item.is_read) {
        await request.post(`/mobile/notifications/${item.id}/read`)
        item.is_read = true
        this.unreadCount = Math.max(0, this.unreadCount - 1)
      }
    },
    async markAllRead() {
      await request.post('/mobile/notifications/read-all')
      this.loadData()
    }
  }
}
</script>

<style lang="scss" scoped>
.read-all { font-size: 13px; color: #409EFF; }

.notif-item {
  margin: 8px 16px;
  background: #fff;
  border-radius: 8px;
  padding: 14px 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  &.unread {
    border-left: 3px solid #409EFF;
    background: #f0f7ff;
  }
}

.notif-title { font-size: 15px; font-weight: 500; margin-bottom: 6px; }
.notif-content { font-size: 13px; color: #606266; line-height: 1.5; }
.notif-time { font-size: 12px; color: #C0C4CC; margin-top: 8px; }
</style>
