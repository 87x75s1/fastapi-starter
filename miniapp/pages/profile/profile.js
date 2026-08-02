const { http } = require('../../utils/request')
const auth = require('../../utils/auth')
const { uploadImage } = require('../../utils/upload')

Page({
  data: {
    statusBarHeight: 20,
    navBarHeight: 44,
    isLoggedIn: false,
    userInfo: null,
    nickname: '',
    genderOptions: ['未知', '男', '女'],
    genderIndex: 0,
    updateLoading: false
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight || 20,
      navBarHeight: 44
    })
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 4 })
    }
    this.checkLoginStatus()
  },

  checkLoginStatus() {
    const isLoggedIn = auth.isLoggedIn()
    const userInfo = auth.getUserInfo()

    this.setData({
      isLoggedIn,
      userInfo,
      nickname: userInfo ? userInfo.nickname || '' : '',
      genderIndex: userInfo ? userInfo.gender || 0 : 0
    })

    // 已登录时自动从服务器刷新用户信息，确保 role 等字段同步
    if (isLoggedIn) {
      this.refreshUserInfo()
    }
  },

  /** 静默刷新用户信息（不显示loading） */
  async refreshUserInfo() {
    try {
      const data = await http.get('/api/user/me', {}, { auth: true, loading: false })
      auth.updateUserInfo(data)
      this.setData({
        userInfo: data,
        nickname: data.nickname || '',
        genderIndex: data.gender || 0
      })
    } catch (err) {
      // 静默失败，使用本地缓存
    }
  },

  goLogin() {
    wx.navigateTo({ url: '/pages/login/login' })
  },

  onNicknameInput(e) {
    this.setData({ nickname: e.detail.value })
  },

  onGenderChange(e) {
    this.setData({ genderIndex: Number(e.detail.value) })
  },

  /** 更新个人资料 */
  async onUpdateProfile() {
    const { nickname, genderIndex, genderOptions } = this.data
    const userInfo = auth.getUserInfo()

    if (!userInfo) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    // 检查是否有变化
    const newNickname = nickname || null
    const newGender = genderIndex
    const oldNickname = userInfo.nickname || ''
    const oldGender = userInfo.gender || 0

    if (newNickname === oldNickname && newGender === oldGender) {
      wx.showToast({ title: '没有修改', icon: 'none' })
      return
    }

    this.setData({ updateLoading: true })

    try {
      const updateData = {}
      if (newNickname !== oldNickname) updateData.nickname = newNickname
      if (newGender !== oldGender) updateData.gender = newGender

      const data = await http.put('/api/user/update', updateData, { auth: true })
      auth.updateUserInfo(data)
      this.setData({ userInfo: data })
      wx.showToast({ title: '修改成功', icon: 'success' })
    } catch (err) {
      // 错误已在 request 中提示
    } finally {
      this.setData({ updateLoading: false })
    }
  },

  /** 更换头像 */
  async onChangeAvatar() {
    try {
      const uploadResult = await uploadImage()
      // 上传成功后，更新头像 URL
      const data = await http.put('/api/user/update', {
        avatar: uploadResult.file_url
      }, { auth: true, loading: false })

      auth.updateUserInfo(data)
      this.setData({ userInfo: data })
      wx.showToast({ title: '头像更新成功', icon: 'success' })
    } catch (err) {
      // 用户取消或上传失败
    }
  },

  /** 从服务器刷新用户信息 */
  async onRefreshInfo() {
    try {
      const data = await http.get('/api/user/me', {}, { auth: true })
      auth.updateUserInfo(data)
      this.setData({
        userInfo: data,
        nickname: data.nickname || '',
        genderIndex: data.gender || 0
      })
      wx.showToast({ title: '刷新成功', icon: 'success' })
    } catch (err) {
      // 错误已在 request 中提示
    }
  },

  /** 退出登录 */
  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      success(res) {
        if (res.confirm) {
          auth.logout()
          wx.showToast({ title: '已退出', icon: 'success' })
          setTimeout(() => {
            wx.switchTab({ url: '/pages/index/index' })
          }, 500)
        }
      }
    })
  },

  /** 跳转订单 */
  goOrders() {
    wx.navigateTo({ url: '/pages/order/order' })
  },

  /** 跳转地址 */
  goAddress() {
    wx.navigateTo({ url: '/pages/address/address' })
  },

  /** 跳转反馈 */
  goFeedback() {
    wx.navigateTo({ url: '/pages/feedback/feedback' })
  },

  /** 跳转管理后台 */
  goAdmin() {
    wx.navigateTo({ url: '/pages/admin/admin' })
  },

  /** 跳转权限管理 */
  goAdminPerm() {
    wx.navigateTo({ url: '/pages/admin-perm/admin-perm' })
  }
})