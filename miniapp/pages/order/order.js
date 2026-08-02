const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    orders: [],
    page: 1,
    pageSize: 20,
    total: 0,
    loading: false,
    noMore: false,
    currentTab: -1,
    tabs: [
      { key: -1, label: '全部' },
      { key: 0, label: '待付款' },
      { key: 1, label: '已付款' },
      { key: 2, label: '已完成' },
      { key: 3, label: '已取消' }
    ],
    statusMap: { 0: '待付款', 1: '已付款', 2: '已完成', 3: '已取消' }
  },

  onShow() {
    if (!auth.isLoggedIn()) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 500)
      return
    }
    this.setData({ orders: [], page: 1, noMore: false })
    this.loadOrders()
  },

  async loadOrders() {
    if (this.data.loading || this.data.noMore) return
    this.setData({ loading: true })

    try {
      const params = { page: this.data.page, page_size: this.data.pageSize }
      if (this.data.currentTab >= 0) params.status = this.data.currentTab

      const data = await http.get('/api/order/list', params, { auth: true, loading: false })
      const items = data.items.map(order => {
        order.total_amount_text = (order.total_amount / 100).toFixed(2)
        if (order.items) {
          order.items = order.items.map(oi => {
            oi.price_text = (oi.price / 100).toFixed(2)
            return oi
          })
        }
        // 解析地址快照
        if (order.address_snapshot) {
          try {
            order.address_info = JSON.parse(order.address_snapshot)
          } catch (e) { order.address_info = null }
        }
        return order
      })
      const orders = [...this.data.orders, ...items]
      this.setData({
        orders,
        total: data.total,
        page: this.data.page + 1,
        noMore: orders.length >= data.total
      })
    } catch (err) {
    } finally {
      this.setData({ loading: false })
    }
  },

  onTabChange(e) {
    const key = Number(e.currentTarget.dataset.key)
    this.setData({ currentTab: key, orders: [], page: 1, noMore: false })
    this.loadOrders()
  },

  onReachBottom() {
    this.loadOrders()
  },

  async onPayOrder(e) {
    const orderId = e.currentTarget.dataset.id
    try {
      await http.post('/api/payment/mock-pay', { order_id: orderId }, { auth: true })
      wx.showToast({ title: '支付成功', icon: 'success' })
      this.setData({ orders: [], page: 1, noMore: false })
      this.loadOrders()
    } catch (err) {}
  },

  async onCancelOrder(e) {
    const orderId = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定取消该订单吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.delete(`/api/order/${orderId}`, {}, { auth: true })
            wx.showToast({ title: '已取消', icon: 'success' })
            this.setData({ orders: [], page: 1, noMore: false })
            this.loadOrders()
          } catch (err) {}
        }
      }
    })
  },

  goProductDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  }
})