const { http, BASE_URL } = require('../../utils/request')
const auth = require('../../utils/auth')
const { resolveImageUrl } = require('../../utils/upload')

Page({
  data: {
    isAdmin: false,
    activeTab: 'stats',
    statusBarHeight: 44,
    stats: {},
    // 商品
    productForm: { name: '', description: '', price: '', image: '', category: '', stock: '' },
    products: [],
    filteredProducts: [],
    productSearch: '',
    productCategory: '',
    productCategories: [],
    productPage: 1,
    productHasMore: false,
    productSubmitting: false,
    editingProductId: null,
    // 订单
    orders: [],
    orderStatusMap: { 0: '待付款', 1: '已付款', 2: '已完成', 3: '已取消' },
    // 反馈
    feedbacks: [],
    replyContent: '',
    // 配置
    configs: [],
    configForm: { key: '', value: '', description: '' },
    configSubmitting: false,
    // 用户
    users: [],
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
      this.loadCurrentTab()
      return
    }
    if (auth.isLoggedIn()) {
      try {
        const data = await http.get('/api/user/me', {}, { auth: true, loading: false })
        auth.updateUserInfo(data)
        if (data.role === 1) {
          this.setData({ isAdmin: true })
          this.loadCurrentTab()
          return
        }
      } catch (err) {}
    }
    wx.showToast({ title: '需要管理员权限', icon: 'none' })
    setTimeout(() => wx.switchTab({ url: '/pages/index/index' }), 1000)
  },

  /** 根据当前 tab 加载对应数据 */
  loadCurrentTab() {
    const tab = this.data.activeTab
    if (tab === 'stats') this.loadStats()
    else if (tab === 'product') this.loadProducts()
    else if (tab === 'order') this.loadOrders()
    else if (tab === 'feedback') this.loadFeedbacks()
    else if (tab === 'config') this.loadConfigs()
    else if (tab === 'user') this.loadUsers()
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ activeTab: tab })
    if (tab === 'stats') this.loadStats()
    else if (tab === 'product') this.loadProducts()
    else if (tab === 'order') this.loadOrders()
    else if (tab === 'feedback') this.loadFeedbacks()
    else if (tab === 'config') this.loadConfigs()
    else if (tab === 'user') this.loadUsers()
  },

  // ========== 统计 ==========
  async loadStats() {
    try {
      const data = await http.get('/api/admin/stats', {}, { auth: true, loading: false })
      this.setData({ stats: data })
    } catch (err) {}
  },

  // ========== 商品管理 ==========
  async loadProducts() {
    try {
      const data = await http.get('/api/product/list', { page: 1, page_size: 20 }, { auth: true, loading: false })
      const items = (data.items || []).map(item => {
        item.price_text = (item.price / 100).toFixed(2)
        item.full_image = resolveImageUrl(item.image)
        return item
      })
      // 提取分类列表
      const categories = [...new Set(items.map(i => i.category).filter(c => c))]
      this.setData({
        products: items,
        filteredProducts: this._filterProducts(items, this.data.productSearch, this.data.productCategory),
        productCategories: categories,
        productPage: 1,
        productHasMore: data.total > 20,
      })
    } catch (err) {
      console.error('[Admin] loadProducts 失败:', err)
    }
  },

  /** 本地搜索+分类筛选 */
  _filterProducts(products, search, category) {
    let list = products
    if (category) list = list.filter(p => p.category === category)
    if (search) list = list.filter(p => p.name.includes(search))
    return list
  },

  onProductSearch(e) {
    const search = e.detail.value
    this.setData({
      productSearch: search,
      filteredProducts: this._filterProducts(this.data.products, search, this.data.productCategory),
    })
  },

  onCategoryFilter(e) {
    const cat = e.currentTarget.dataset.cat
    this.setData({
      productCategory: cat,
      filteredProducts: this._filterProducts(this.data.products, this.data.productSearch, cat),
    })
  },

  onLoadMoreProducts() {
    const page = this.data.productPage + 1
    http.get('/api/product/list', { page, page_size: 20 }, { auth: true, loading: false }).then(data => {
      const items = (data.items || []).map(item => {
        item.price_text = (item.price / 100).toFixed(2)
        item.full_image = resolveImageUrl(item.image)
        return item
      })
      const all = [...this.data.products, ...items]
      const categories = [...new Set(all.map(i => i.category).filter(c => c))]
      this.setData({
        products: all,
        filteredProducts: this._filterProducts(all, this.data.productSearch, this.data.productCategory),
        productCategories: categories,
        productPage: page,
        productHasMore: all.length < data.total,
      })
    }).catch(() => {})
  },

  onProductInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`productForm.${field}`]: e.detail.value })
  },

  /** 简单 URL 格式校验 */
  _isValidUrl(str) {
    if (!str) return true // 空值允许
    // 允许 /static/ 开头的相对路径（本地上传图片）
    if (str.startsWith('/static/')) return true
    // 允许 http/https 开头的完整URL
    if (str.startsWith('http://') || str.startsWith('https://')) return true
    return false
  },

  /** 图片加载失败 - 清除无效图片地址 */
  onImgError(e) {
    const id = e.currentTarget.dataset.id
    const products = this.data.products.map(p => {
      if (p.id === id) p._imgError = true
      return p
    })
    this.setData({ products })
  },

  /** 提交商品（新增或编辑） */
  async onSubmitProduct() {
    const form = this.data.productForm
    if (!form.name) { wx.showToast({ title: '商品名称必填', icon: 'none' }); return }
    if (!form.price) { wx.showToast({ title: '价格必填', icon: 'none' }); return }
    if (isNaN(parseFloat(form.price)) || parseFloat(form.price) < 0) {
      wx.showToast({ title: '价格格式不正确', icon: 'none' }); return
    }
    if (form.image && !this._isValidUrl(form.image)) {
      wx.showToast({ title: '图片地址格式不正确', icon: 'none' }); return
    }

    this.setData({ productSubmitting: true })
    try {
      const payload = {
        name: form.name,
        description: form.description,
        price: Math.round(parseFloat(form.price) * 100),
        image: form.image,
        category: form.category,
        stock: parseInt(form.stock) || 0,
      }

      if (this.data.editingProductId) {
        // 编辑模式
        await http.put(`/api/admin/product/${this.data.editingProductId}`, payload, { auth: true })
        wx.showToast({ title: '修改成功', icon: 'success' })
      } else {
        // 新增模式
        await http.post('/api/admin/product/create', payload, { auth: true })
        wx.showToast({ title: '创建成功', icon: 'success' })
      }

      this.setData({
        productForm: { name: '', description: '', price: '', image: '', category: '', stock: '' },
        editingProductId: null,
      })
      // 刷新商品列表并确保显示商品tab
      await this.loadProducts()
      if (this.data.activeTab !== 'product') {
        this.setData({ activeTab: 'product' })
      }
      wx.pageScrollTo({ scrollTop: 0, duration: 300 })
    } catch (err) {
      // 错误已在 request 中提示
    } finally {
      this.setData({ productSubmitting: false })
    }
  },

  /** 编辑商品 - 填充表单 */
  onEditProduct(e) {
    const id = e.currentTarget.dataset.id
    const product = this.data.products.find(p => p.id === id)
    if (!product) return

    this.setData({
      editingProductId: id,
      productForm: {
        name: product.name || '',
        description: product.description || '',
        price: product.price_text || '',
        image: product.image || '',
        category: product.category || '',
        stock: product.stock ? String(product.stock) : '0',
      },
    })
    // 滚动到表单顶部
    wx.pageScrollTo({ scrollTop: 0, duration: 300 })
  },

  /** 取消编辑 */
  onCancelEdit() {
    this.setData({
      editingProductId: null,
      productForm: { name: '', description: '', price: '', image: '', category: '', stock: '' },
    })
  },

  /** 切换商品上下架 */
  onToggleProductStatus(e) {
    const { id, status } = e.currentTarget.dataset
    const newStatus = status === 1 ? 0 : 1
    const msg = newStatus === 1 ? '上架' : '下架'
    wx.showModal({
      title: '确认操作',
      content: `确定将商品设为"${msg}"吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.put(`/api/admin/product/${id}`, { status: newStatus }, { auth: true })
            wx.showToast({ title: `已${msg}`, icon: 'success' })
            this.loadProducts()
          } catch (err) {}
        }
      },
    })
  },

  /** 删除商品（带确认弹窗+商品名称） */
  onDeleteProduct(e) {
    const { id, name } = e.currentTarget.dataset
    wx.showModal({
      title: '确认删除',
      content: `确定删除商品"${name || ''}"吗？此操作不可恢复。`,
      confirmColor: '#e4393c',
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.delete(`/api/admin/product/${id}`, {}, { auth: true })
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadProducts()
          } catch (err) {}
        }
      },
    })
  },

  // ========== 订单管理 ==========
  async loadOrders() {
    try {
      const data = await http.get('/api/admin/order/list', { page_size: 50 }, { auth: true, loading: false })
      const items = (data.items || []).map(order => {
        order.total_amount_text = (order.total_amount / 100).toFixed(2)
        if (order.items) order.items = order.items.map(oi => { oi.price_text = (oi.price / 100).toFixed(2); return oi })
        return order
      })
      this.setData({ orders: items })
    } catch (err) {}
  },

  async onUpdateOrderStatus(e) {
    const { id, status } = e.currentTarget.dataset
    const statusNames = { 1: '已付款', 2: '已完成', 3: '已取消' }
    wx.showModal({
      title: '确认操作', content: `确定将订单标记为"${statusNames[status]}"吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.put(`/api/admin/order/${id}/status`, { status }, { auth: true })
            wx.showToast({ title: '操作成功', icon: 'success' })
            this.loadOrders()
          } catch (err) {}
        }
      },
    })
  },

  // ========== 反馈管理 ==========
  async loadFeedbacks() {
    try {
      const data = await http.get('/api/admin/feedback/list', { page_size: 50 }, { auth: true, loading: false })
      this.setData({ feedbacks: data.items || [] })
    } catch (err) {}
  },

  onReplyInput(e) { this.setData({ replyContent: e.detail.value }) },

  async onReplyFeedback(e) {
    const id = e.currentTarget.dataset.id
    const reply = this.data.replyContent
    if (!reply) { wx.showToast({ title: '请输入回复内容', icon: 'none' }); return }
    try {
      await http.put(`/api/admin/feedback/${id}/reply`, { reply }, { auth: true })
      wx.showToast({ title: '回复成功', icon: 'success' })
      this.setData({ replyContent: '' })
      this.loadFeedbacks()
    } catch (err) {}
  },

  // ========== 配置管理 ==========
  async loadConfigs() {
    try {
      const data = await http.get('/api/config/list', { page_size: 100 }, { auth: true, loading: false })
      this.setData({ configs: data.items || [] })
    } catch (err) {}
  },

  onConfigInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`configForm.${field}`]: e.detail.value })
  },

  async onCreateConfig() {
    const form = this.data.configForm
    if (!form.key) { wx.showToast({ title: '配置键必填', icon: 'none' }); return }
    this.setData({ configSubmitting: true })
    try {
      await http.post('/api/admin/config/create', form, { auth: true })
      wx.showToast({ title: '创建成功', icon: 'success' })
      this.setData({ configForm: { key: '', value: '', description: '' } })
      this.loadConfigs()
    } catch (err) {} finally {
      this.setData({ configSubmitting: false })
    }
  },

  async onDeleteConfig(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除', content: '确定删除该配置吗？',
      confirmColor: '#e4393c',
      success: async (res) => {
        if (res.confirm) {
          try {
            await http.delete(`/api/admin/config/${id}`, {}, { auth: true })
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadConfigs()
          } catch (err) {}
        }
      },
    })
  },

  // ========== 用户管理 ==========
  async loadUsers() {
    try {
      const data = await http.get('/api/admin/user/list', { page_size: 50 }, { auth: true, loading: false })
      this.setData({ users: data.items || [] })
    } catch (err) {}
  },

  async onToggleRole(e) {
    const { id, role } = e.currentTarget.dataset
    const newRole = role === 1 ? 0 : 1
    const msg = newRole === 1 ? '设为管理员' : '取消管理员'
    wx.showModal({
      title: '确认操作', content: `确定${msg}吗？`,
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