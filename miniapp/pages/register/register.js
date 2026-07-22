const { http } = require('../../utils/request')

Page({
  data: {
    phone: '',
    password: '',
    confirmPassword: '',
    loading: false
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  onConfirmPasswordInput(e) {
    this.setData({ confirmPassword: e.detail.value })
  },

  async onRegister() {
    const { phone, password, confirmPassword } = this.data

    // 前端校验
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }
    if (phone.length !== 11 || !phone.startsWith('1')) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!password) {
      wx.showToast({ title: '请输入密码', icon: 'none' })
      return
    }
    if (password.length < 6) {
      wx.showToast({ title: '密码至少6位', icon: 'none' })
      return
    }
    if (password !== confirmPassword) {
      wx.showToast({ title: '两次密码不一致', icon: 'none' })
      return
    }

    this.setData({ loading: true })

    try {
      await http.post('/api/user/register', { phone, password })
      wx.showToast({ title: '注册成功', icon: 'success' })

      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' })
      }, 1000)
    } catch (err) {
      // 错误已在 request 中提示
    } finally {
      this.setData({ loading: false })
    }
  },

  goLogin() {
    wx.navigateTo({ url: '/pages/login/login' })
  }
})