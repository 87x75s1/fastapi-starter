const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    products: [],
    page: 1,
    pageSize: 20,
    total: 0,
    loading: false,
    noMore: false,
    category: '',
    categories: []
  },

  onShow() {
    this.setData({ products: [], page: 1, noMore: false })
    this.loadProducts()
  },

  async loadProducts() {
    if (this.data.loading || this.data.noMore) return
    this.setData({ loading: true })

    try {
      const data = await http.get('/api/product/list', {
        page: this.data.page,
        page_size: this.data.pageSize,
        status: 1
      }, { loading: false })

      const products = [...this.data.products, ...data.items]
      this.setData({
        products,
        total: data.total,
        page: this.data.page + 1,
        noMore: products.length >= data.total
      })
    } catch (err) {
      // 错误已在 request 中提示
    } finally {
      this.setData({ loading: false })
    }
  },

  onReachBottom() {
    this.loadProducts()
  },

  onPullDownRefresh() {
    this.setData({ products: [], page: 1, noMore: false })
    this.loadProducts().then(() => wx.stopPullDownRefresh())
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/product/detail?id=${id}` })
  }
})