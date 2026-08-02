Page({
  data: {
    statusBarHeight: 20,
    navBarHeight: 44,
    currentTab: 0,
    categories: [
      { id: 1, name: '家居生活' },
      { id: 2, name: '数码科技' },
      { id: 3, name: '服饰箱包' },
      { id: 4, name: '美妆个护' },
      { id: 5, name: '食品茶饮' },
      { id: 6, name: '运动户外' },
      { id: 7, name: '图书文创' },
      { id: 8, name: '母婴亲子' },
      { id: 9, name: '家电厨具' },
      { id: 10, name: '更多好物' }
    ],
    currentCatId: 1,
    scrollIntoId: 'cat-1',
    sortOptions: ['综合', '销量', '价格'],
    currentSort: 0,
    productList: [],
    displayProducts: [],
    categoryProducts: {
      1: [
        { id: 101, name: '北欧简约陶瓷花瓶', price: 89, sales: 1286, image: '' },
        { id: 102, name: '纯棉高支床品四件套', price: 329, sales: 1547, image: '' },
        { id: 103, name: '智能香薰机 静音雾化', price: 199, sales: 976, image: '' },
        { id: 104, name: '实木书架落地式 四层', price: 459, sales: 321, image: '' },
        { id: 105, name: '日式手冲咖啡壶套装', price: 168, sales: 2156, image: '' },
        { id: 106, name: '极简挂钟 静音实木', price: 128, sales: 890, image: '' }
      ],
      2: [
        { id: 201, name: '无线蓝牙降噪耳机', price: 599, sales: 934, image: '' },
        { id: 202, name: '机械键盘87键 茶轴', price: 349, sales: 2890, image: '' },
        { id: 203, name: '便携式投影仪 家用', price: 1299, sales: 432, image: '' },
        { id: 204, name: '智能手环 血氧监测', price: 199, sales: 3456, image: '' },
        { id: 205, name: 'USB-C拓展坞 七合一', price: 168, sales: 1234, image: '' },
        { id: 206, name: '4K显示器 27英寸', price: 1899, sales: 567, image: '' }
      ],
      3: [
        { id: 301, name: '头层牛皮商务手提包', price: 459, sales: 823, image: '' },
        { id: 302, name: '羊绒围巾 纯色经典款', price: 268, sales: 478, image: '' },
        { id: 303, name: '真皮极简钱包 短款', price: 239, sales: 678, image: '' },
        { id: 304, name: '纯棉衬衫 免烫商务', price: 189, sales: 1567, image: '' }
      ],
      4: [
        { id: 401, name: '氨基酸洁面乳 温和', price: 89, sales: 5678, image: '' },
        { id: 402, name: '精华液 玻尿酸30ml', price: 199, sales: 2345, image: '' },
        { id: 403, name: '防晒霜 SPF50 清爽', price: 128, sales: 3456, image: '' },
        { id: 404, name: '电动牙刷 声波式', price: 259, sales: 890, image: '' }
      ],
      5: [
        { id: 501, name: '西湖龙井 明前特级', price: 168, sales: 567, image: '' },
        { id: 502, name: '云南普洱茶饼 熟茶', price: 88, sales: 1234, image: '' },
        { id: 503, name: '手冲咖啡豆 精品', price: 68, sales: 2345, image: '' },
        { id: 504, name: '有机坚果混合装', price: 49, sales: 4567, image: '' }
      ],
      6: [
        { id: 601, name: '瑜伽垫 加厚防滑', price: 99, sales: 2345, image: '' },
        { id: 602, name: '跑步鞋 轻量缓震', price: 399, sales: 890, image: '' },
        { id: 603, name: '运动水壶 大容量', price: 59, sales: 3456, image: '' }
      ],
      7: [
        { id: 701, name: '经典文学名著套装', price: 128, sales: 678, image: '' },
        { id: 702, name: '手账本 A5 文艺', price: 38, sales: 2345, image: '' },
        { id: 703, name: '钢笔 礼盒装', price: 168, sales: 456, image: '' }
      ],
      8: [
        { id: 801, name: '婴儿纯棉连体衣', price: 79, sales: 3456, image: '' },
        { id: 802, name: '儿童益智积木', price: 129, sales: 1234, image: '' },
        { id: 803, name: '妈咪包 大容量', price: 159, sales: 567, image: '' }
      ],
      9: [
        { id: 901, name: '德国不锈钢厨具套装', price: 388, sales: 1567, image: '' },
        { id: 902, name: '扫地机器人 激光', price: 1599, sales: 432, image: '' },
        { id: 903, name: '空气炸锅 大容量', price: 299, sales: 2890, image: '' }
      ],
      10: [
        { id: 1001, name: '桌面收纳架 多层', price: 69, sales: 4567, image: '' },
        { id: 1002, name: '旅行收纳包套装', price: 49, sales: 2345, image: '' },
        { id: 1003, name: '极简雨伞 自动折叠', price: 79, sales: 890, image: '' }
      ]
    }
  },

  onLoad() {
    const sysInfo = wx.getSystemInfoSync()
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight || 20,
      navBarHeight: 44
    })
    this.loadProducts()
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 })
    }
  },

  onSwitchTab(e) {
    this.setData({ currentTab: Number(e.currentTarget.dataset.tab) })
    this.loadProducts()
  },

  onCatTap(e) {
    this.setData({ currentCatId: e.currentTarget.dataset.id })
    this.loadProducts()
  },

  onSortTap(e) {
    this.setData({ currentSort: Number(e.currentTarget.dataset.idx) })
    this.sortProducts()
  },

  loadProducts() {
    const products = this.data.categoryProducts[this.data.currentCatId] || []
    this.setData({ productList: [...products] })
    this.sortProducts()
  },

  sortProducts() {
    const list = [...this.data.productList]
    const sort = this.data.currentSort
    if (sort === 1) list.sort((a, b) => b.sales - a.sales)
    else if (sort === 2) list.sort((a, b) => a.price - b.price)
    this.setData({ displayProducts: list })
  },

  onSearch(e) {
    const keyword = e.detail.value.trim()
    if (!keyword) { this.loadProducts(); return }
    this.setData({ displayProducts: this.data.productList.filter(p => p.name.indexOf(keyword) !== -1) })
  },

  onImgError() {},

  onProductTap(e) {
    wx.navigateTo({ url: '/pages/product/detail?id=' + e.currentTarget.dataset.id })
  },

  onAddCart() {
    wx.showToast({ title: '已加入购物车', icon: 'success', duration: 1500 })
  }
})