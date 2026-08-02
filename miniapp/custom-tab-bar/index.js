Component({
  data: {
    selected: 0,
    list: [
      {
        pagePath: '/pages/index/index',
        text: '首页',
        iconPath: '/assets/tab-home.png',
        selectedIconPath: '/assets/tab-home-active.png'
      },
      {
        pagePath: '/pages/category/category',
        text: '分类',
        iconPath: '/assets/tab-category.png',
        selectedIconPath: '/assets/tab-category-active.png'
      },
      {
        pagePath: '/pages/service/service',
        text: '客服',
        iconPath: '/assets/tab-service.png',
        selectedIconPath: '/assets/tab-service-active.png'
      },
      {
        pagePath: '/pages/cart/cart',
        text: '购物车',
        iconPath: '/assets/tab-cart.png',
        selectedIconPath: '/assets/tab-cart-active.png'
      },
      {
        pagePath: '/pages/profile/profile',
        text: '我的',
        iconPath: '/assets/tab-user.png',
        selectedIconPath: '/assets/tab-user-active.png'
      }
    ]
  },

  methods: {
    switchTab(e) {
      const data = e.currentTarget.dataset
      const url = data.path
      const index = data.index
      wx.switchTab({ url })
      this.setData({ selected: index })
    }
  }
})