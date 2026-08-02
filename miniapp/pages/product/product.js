const { http } = require('../../utils/request')
const auth = require('../../utils/auth')
const { resolveImageUrl } = require('../../utils/upload')

Page({
  data: {
    products: [],
    page: 1,
    pageSize: 20,
    total: 0,
    loading: false,
    noMore: false,

    // 搜索
    keyword: '',
    searchInput: '',

    // 分类
    categories: [],
    activeCategory: '',

    // 排序
    sortOptions: [
      { key: 'default', label: '综合' },
      { key: 'price_asc', label: '价格↑' },
      { key: 'price_desc', label: '价格↓' },
      { key: 'newest', label: '最新' },
    ],
    activeSort: 'default',
  },

  onShow() {
    this.loadCategories()
    this.resetAndLoad()
  },

  async loadCategories() {
    try {
      const data = await http.get('/api/product/categories', {}, { loading: false })
      this.setData({ categories: data || [] })
    } catch (err) {
      // 忽略分类加载失败
    }
  },

  resetAndLoad() {
    this.setData({ products: [], page: 1, noMore: false })
    this.loadProducts()
  },

  async loadProducts() {
    if (this.data.loading || this.data.noMore) return
    this.setData({ loading: true })

    try {
      const params = {
        page: this.data.page,
        page_size: this.data.pageSize,
        status: 1,
      }
      if (this.data.keyword) params.keyword = this.data.keyword
      if (this.data.activeCategory) params.category = this.data.activeCategory
      if (this.data.activeSort !== 'default') params.sort = this.data.activeSort

      const data = await http.get('/api/product/list', params, { loading: false })

      const newItems = data.items.map(item => {
        item.price_text = (item.price / 100).toFixed(2)
        item.stock_text = item.stock > 0 ? `库存:${item.stock}` : '库存充足'
        item.full_image = resolveImageUrl(item.image)
        return item
      })
      const products = [...this.data.products, ...newItems]
      this.setData({
        products,
        total: data.total,
        page: this.data.page + 1,
        noMore: products.length >= data.total,
      })
    } catch (err) {
      // 错误已在 request 中提示
    } finally {
      this.setData({ loading: false })
    }
  },

  // 搜索输入
  onSearchInput(e) {
    this.setData({ searchInput: e.detail.value })
  },

  // 确认搜索
  onSearchConfirm() {
    this.setData({ keyword: this.data.searchInput })
    this.resetAndLoad()
  },

  // 清空搜索
  onSearchClear() {
    this.setData({ keyword: '', searchInput: '' })
    this.resetAndLoad()
  },

  // 切换分类
  onCategoryTap(e) {
    const category = e.currentTarget.dataset.category
    this.setData({ activeCategory: category })
    this.resetAndLoad()
  },

  // 切换排序
  onSortTap(e) {
    const sort = e.currentTarget.dataset.sort
    this.setData({ activeSort: sort })
    this.resetAndLoad()
  },

  onReachBottom() {
    this.loadProducts()
  },

  onPullDownRefresh() {
    this.resetAndLoad()
    wx.stopPullDownRefresh()
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  }
})