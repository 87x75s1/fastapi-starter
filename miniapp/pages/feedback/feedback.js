const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    feedbacks: [],
    content: '',
    contact: '',
    page: 1,
    pageSize: 20,
    noMore: false,
    loading: false
  },

  onShow() {
    if (!auth.isLoggedIn()) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 500)
      return
    }
    this.setData({ feedbacks: [], page: 1, noMore: false })
    this.loadFeedbacks()
  },

  async loadFeedbacks() {
    if (this.data.loading || this.data.noMore) return
    this.setData({ loading: true })
    try {
      const data = await http.get('/api/feedback/list', {
        page: this.data.page, page_size: this.data.pageSize
      }, { auth: true, loading: false })
      const feedbacks = [...this.data.feedbacks, ...data.items]
      this.setData({
        feedbacks,
        page: this.data.page + 1,
        noMore: feedbacks.length >= data.total
      })
    } catch (err) {
    } finally {
      this.setData({ loading: false })
    }
  },

  onContentInput(e) { this.setData({ content: e.detail.value }) },
  onContactInput(e) { this.setData({ contact: e.detail.value }) },

  async onSubmit() {
    const { content, contact } = this.data
    if (!content.trim()) {
      wx.showToast({ title: '请输入反馈内容', icon: 'none' })
      return
    }
    try {
      await http.post('/api/feedback/create', { content, contact }, { auth: true })
      wx.showToast({ title: '提交成功', icon: 'success' })
      this.setData({ content: '', contact: '' })
      this.setData({ feedbacks: [], page: 1, noMore: false })
      this.loadFeedbacks()
    } catch (err) {}
  },

  onReachBottom() { this.loadFeedbacks() }
})