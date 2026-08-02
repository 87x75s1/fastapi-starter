const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    isAdmin: false,
    statusBarHeight: 44,
    users: [],
    filteredUsers: [],
    searchKey: '',
    adminCount: 0,
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync()
    this.setData({ statusBarHeight: sysInfo.statusBarHeight || 44 })
  },

  goBack() {
    wx.navigateBack({ delta: 1 })
  },

  async onShow() {
    const localUserInfo = auth.getUserInfo()
    if (localUserInfo && localUserInfo.role === 1) {
      this.setData({ isAdmin: true })
      this.loadUsers()
      return
    }
    if (auth.isLoggedIn()) {
      try {
        const data = await http.get('/api/user/me', {}, { auth: true, loading: false })
        auth.updateUserInfo(data)
        if (data.role === 1) {
          this.setData({ isAdmin: true })
          this.loadUsers()
          return
        }
      } catch (err) {}
    }
    wx.showToast({ title: '需要管理员权限', icon: 'none' })
    setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 1000)
  },

  async loadUsers() {
    try {
      const data = await http.get('/api/admin/user/list', { page_size: 100 }, { auth: true, loading: false })
      const users = (data.items || []).map(u => {
        u._avatarText = (u.nickname || u.phone || '?')[0] || '?'
        return u
      })
      const adminCount = users.filter(u => u.role === 1).length
      this.setData({
        users,
        filteredUsers: this._filterUsers(users, this.data.searchKey),
        adminCount,
      })
    } catch (err) {
      console.error('[AdminPerm] loadUsers 失败:', err)
    }
  },

  _filterUsers(users, search) {
    if (!search) return users
    const key = search.toLowerCase()
    return users.filter(u =>
      (u.nickname && u.nickname.toLowerCase().includes(key)) ||
      (u.phone && u.phone.includes(key))
    )
  },

  onSearch(e) {
    const searchKey = e.detail.value
    this.setData({
      searchKey,
      filteredUsers: this._filterUsers(this.data.users, searchKey),
    })
  },

  async onToggleRole(e) {
    const { id, role } = e.currentTarget.dataset
    const newRole = role === 1 ? 0 : 1
    const msg = newRole === 1 ? '设为管理员' : '取消管理员'
    wx.showModal({
      title: '确认操作',
      content: `确定${msg}吗？`,
      confirmColor: '#365486',
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.put(`/api/admin/user/${id}/role`, { role: newRole }, { auth: true })
            wx.showToast({ title: '操作成功', icon: 'success' })
            this.loadUsers()
          } catch (err) {}
        }
      },
    })
  },
})