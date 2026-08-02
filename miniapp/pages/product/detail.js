const { http } = require('../../utils/request')
const auth = require('../../utils/auth')
const { resolveImageUrl } = require('../../utils/upload')

Page({
  data: {
    product: null,
    quantity: 1,
    loading: true,
    showAddressPicker: false,
    addresses: [],
    selectedAddress: null
  },

  onLoad(options) {
    this.productId = options.id
    this.loadProduct()
  },

  async loadProduct() {
    try {
      const data = await http.get(`/api/product/${this.productId}`, {}, { loading: true })
      data.price_text = (data.price / 100).toFixed(2)
      data.stock_text = data.stock > 0 ? `库存: ${data.stock}` : '库存充足'
      data.full_image = resolveImageUrl(data.image)
      this.setData({ product: data, loading: false })
    } catch (err) {
      this.setData({ loading: false })
    }
  },

  onQuantityMinus() {
    if (this.data.quantity > 1) {
      this.setData({ quantity: this.data.quantity - 1 })
    }
  },

  onQuantityPlus() {
    const { product, quantity } = this.data
    if (product && product.stock > 0 && quantity >= product.stock) {
      wx.showToast({ title: '已达最大库存', icon: 'none' })
      return
    }
    this.setData({ quantity: quantity + 1 })
  },

  onQuantityInput(e) {
    let val = parseInt(e.detail.value) || 1
    if (val < 1) val = 1
    const { product } = this.data
    if (product && product.stock > 0 && val > product.stock) val = product.stock
    this.setData({ quantity: val })
  },

  async onBuyNow() {
    if (!auth.isLoggedIn()) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/login/login' }), 500)
      return
    }

    // 加载地址列表
    try {
      const addrs = await http.get('/api/address/list', {}, { auth: true, loading: false })
      if (!addrs || addrs.length === 0) {
        wx.showModal({
          title: '提示',
          content: '请先添加收货地址',
          confirmText: '去添加',
          success: (res) => {
            if (res.confirm) wx.navigateTo({ url: '/pages/address/edit' })
          }
        })
        return
      }
      // 找默认地址，没有则取第一个
      const defaultAddr = addrs.find(a => a.is_default === 1) || addrs[0]
      this.setData({ addresses: addrs, selectedAddress: defaultAddr, showAddressPicker: true })
    } catch (err) {
      // 地址加载失败，直接下单（不带地址）
      this.doCreateOrder(null)
    }
  },

  onSelectAddress(e) {
    const id = Number(e.currentTarget.dataset.id)
    const addr = this.data.addresses.find(a => a.id === id)
    if (addr) this.setData({ selectedAddress: addr })
  },

  onConfirmAddress() {
    this.setData({ showAddressPicker: false })
    this.doCreateOrder(this.data.selectedAddress)
  },

  onCancelAddress() {
    this.setData({ showAddressPicker: false })
  },

  async doCreateOrder(address) {
    wx.showLoading({ title: '提交中...' })
    try {
      const body = {
        items: [{ product_id: this.productId, quantity: this.data.quantity }]
      }
      if (address) body.address_id = address.id

      const order = await http.post('/api/order/create', body, { auth: true })
      wx.hideLoading()

      // 跳转到支付
      wx.showModal({
        title: '下单成功',
        content: `订单号: ${order.order_no}\n金额: ¥${(order.total_amount / 100).toFixed(2)}`,
        confirmText: '去支付',
        cancelText: '稍后付',
        success: (res) => {
          if (res.confirm) {
            this.doPay(order.id)
          } else {
            wx.navigateTo({ url: '/pages/order/order' })
          }
        }
      })
    } catch (err) {
      wx.hideLoading()
    }
  },

  async doPay(orderId) {
    try {
      // 模拟支付
      await http.post('/api/payment/mock-pay', { order_id: orderId }, { auth: true })
      wx.showToast({ title: '支付成功', icon: 'success' })
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/order/order' })
      }, 1500)
    } catch (err) {
      wx.showToast({ title: '支付失败', icon: 'none' })
    }
  }
})