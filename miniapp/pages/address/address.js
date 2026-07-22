const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    addresses: [],
    loading: false
  },

  onShow() {
    if (!auth.isLoggedIn()) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 500)
      return
    }
    this.loadAddresses()
  },

  async loadAddresses() {
    this.setData({ loading: true })
    try {
      const data = await http.get('/api/address/list', {}, { auth: true, loading: false })
      this.setData({ addresses: data })
    } catch (err) {
    } finally {
      this.setData({ loading: false })
    }
  },

  async setDefault(e) {
    const id = e.currentTarget.dataset.id
    try {
      await http.put(`/api/address/${id}/default`, {}, { auth: true })
      wx.showToast({ title: '设置成功', icon: 'success' })
      this.loadAddresses()
    } catch (err) {}
  },

  deleteAddress(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '提示',
      content: '确定删除该地址吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.delete(`/api/address/${id}`, {}, { auth: true })
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadAddresses()
          } catch (err) {}
        }
      }
    })
  },

  goAdd() {
    wx.navigateTo({ url: '/pages/address/edit' })
  },

  goEdit(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/address/edit?id=${id}` })
  }
})