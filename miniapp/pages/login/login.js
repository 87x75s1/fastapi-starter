const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    phone: '',
    password: '',
    loading: false
  },

  onPhoneInput(e) {
    this.setData({ phone: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  async onLogin() {
    const { phone, password } = this.data

    // 前端校验
    if (!phone) {
      wx.showToast({ title: '请输入手机号', icon: 'none' })
      return
    }
    if (phone.length !== 11) {
      wx.showToast({ title: '手机号格式不正确', icon: 'none' })
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

    this.setData({ loading: true })

    try {
      const data = await http.post('/api/user/login', { phone, password })
      // 保存登录信息
      auth.saveLogin(data.token, data.user)
      wx.showToast({ title: '登录成功', icon: 'success' })

      setTimeout(() => {
        // 返回上一页或跳转到首页
        const pages = getCurrentPages()
        if (pages.length > 1) {
          wx.navigateBack()
        } else {
          wx.switchTab({ url: '/pages/index/index' })
        }
      }, 1000)
    } catch (err) {
      // 错误已在 request 中提示
    } finally {
      this.setData({ loading: false })
    }
  },

  goRegister() {
    wx.navigateTo({ url: '/pages/register/register' })
  }
})