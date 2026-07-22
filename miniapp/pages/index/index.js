const { http, BASE_URL } = require('../../utils/request')
const auth = require('../../utils/auth')
const { uploadImage } = require('../../utils/upload')

Page({
  data: {
    baseUrl: BASE_URL,
    connected: false,
    isLoggedIn: false,
    techStack: [
      { name: 'FastAPI', desc: '高性能异步 Web 框架' },
      { name: 'SQLAlchemy 2.0', desc: '异步 ORM 数据库操作' },
      { name: 'Pydantic v2', desc: '数据校验与序列化' },
      { name: 'JWT', desc: '无状态令牌认证' },
      { name: 'bcrypt', desc: '安全密码哈希' },
      { name: 'SQLite', desc: '轻量级数据库（可切换 MySQL）' }
    ]
  },

  onShow() {
    this.setData({ isLoggedIn: auth.isLoggedIn() })
    this.checkBackendHealth()
  },

  /** 检查后端健康状态 */
  async checkBackendHealth() {
    try {
      await http.get('/health', {}, { loading: false, auth: false })
      this.setData({ connected: true })
    } catch (err) {
      this.setData({ connected: false })
    }
  },

  /** 跳转个人中心 */
  goProfile() {
    wx.switchTab({ url: '/pages/profile/profile' })
  },

  /** 上传图片 */
  async goUpload() {
    if (!auth.isLoggedIn()) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/login/login' })
      }, 500)
      return
    }

    try {
      const result = await uploadImage()
      wx.showModal({
        title: '上传成功',
        content: `文件: ${result.filename}\n大小: ${(result.file_size / 1024).toFixed(1)}KB\nURL: ${result.file_url}`,
        showCancel: false
      })
    } catch (err) {
      // 用户取消或上传失败
    }
  },

  /** 跳转登录 */
  goLogin() {
    if (auth.isLoggedIn()) {
      wx.showToast({ title: '已登录', icon: 'success' })
    } else {
      wx.navigateTo({ url: '/pages/login/login' })
    }
  },

  /** 检查后端连接 */
  checkBackend() {
    wx.showLoading({ title: '检测中...' })
    this.checkBackendHealth().then(() => {
      wx.hideLoading()
      if (this.data.connected) {
        wx.showToast({ title: '后端连接正常', icon: 'success' })
      } else {
        wx.showToast({ title: '后端连接失败', icon: 'none' })
      }
    })
  }
})