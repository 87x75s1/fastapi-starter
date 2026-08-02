Page({
  data: {
    statusBarHeight: 20,
    navBarHeight: 44,
    noticeText: '新用户首单立减10元 · 全场满99包邮 · 品质保障',
    featuredProducts: [
      { id: 1, name: '北欧简约陶瓷花瓶 客厅摆件', price: 89, sales: 1286, image: '' },
      { id: 2, name: '头层牛皮商务手提包 大容量', price: 459, sales: 823, image: '' },
      { id: 3, name: '日式手冲咖啡壶套装 玻璃', price: 168, sales: 2156, image: '' },
      { id: 4, name: '纯棉高支床品四件套 素色', price: 329, sales: 1547, image: '' },
      { id: 5, name: '智能香薰机 静音雾化 卧室', price: 199, sales: 976, image: '' },
      { id: 6, name: '真皮极简钱包 短款头层牛皮', price: 239, sales: 678, image: '' }
    ],
    qualityProducts: [
      { id: 7, name: '无线蓝牙降噪耳机 头戴式', price: 599, sales: 934, image: '' },
      { id: 8, name: '德国不锈钢厨具五件套', price: 388, sales: 1567, image: '' },
      { id: 9, name: '羊绒围巾 纯色 经典款', price: 268, sales: 478, image: '' },
      { id: 10, name: '实木书架落地式 四层', price: 459, sales: 321, image: '' },
      { id: 11, name: '机械键盘87键 茶轴 复古', price: 349, sales: 2890, image: '' },
      { id: 12, name: '便携式投影仪 家用高清', price: 1299, sales: 432, image: '' }
    ]
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
      this.getTabBar().setData({ selected: 0 })
    }
  },

  onImgError() {},

  onProductTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/product/detail?id=' + id })
  },

  onAddCart(e) {
    wx.showToast({ title: '已加入购物车', icon: 'success', duration: 1500 })
  },

  onViewMore() {
    wx.switchTab({ url: '/pages/category/category' })
  },

  onSearchTap() {
    wx.switchTab({ url: '/pages/category/category' })
  },

  onMessageTap() {
    wx.showToast({ title: '暂无新消息', icon: 'none', duration: 1500 })
  }
})