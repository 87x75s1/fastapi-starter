/**
 * 网络请求封装
 * 统一处理：基础URL、Token注入、错误提示、登录过期跳转
 */

// 后端服务地址（开发环境用本地，上线后改为正式域名）
const BASE_URL = 'http://60.205.126.22:8000'

/**
 * 封装 wx.request
 * @param {string} url - 接口路径（如 /api/user/login）
 * @param {string} method - 请求方法
 * @param {object} data - 请求参数
 * @param {object} options - 额外选项 { loading: 是否显示loading, auth: 是否需要token }
 */
function request(url, method = 'GET', data = {}, options = {}) {
  const { loading = true, auth = false } = options

  if (loading) {
    wx.showLoading({ title: '加载中...', mask: true })
  }

  return new Promise((resolve, reject) => {
    const header = { 'Content-Type': 'application/json' }

    // 需要鉴权的请求，自动带上 token
    if (auth) {
      const token = wx.getStorageSync('token')
      if (!token) {
        wx.hideLoading()
        wx.showToast({ title: '请先登录', icon: 'none' })
        setTimeout(() => {
          wx.navigateTo({ url: '/pages/login/login' })
        }, 500)
        reject(new Error('未登录'))
        return
      }
      header['Authorization'] = `Bearer ${token}`
    }

    wx.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      success(res) {
        if (loading) wx.hideLoading()

        // HTTP 状态码异常
        if (res.statusCode !== 200) {
          const msg = (res.data && res.data.message) || '服务器错误'
          wx.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
          return
        }

        // 业务状态码：0 表示成功
        if (res.data.code === 0) {
          resolve(res.data.data)
        } else {
          const msg = res.data.message || '操作失败'
          wx.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail(err) {
        if (loading) wx.hideLoading()
        wx.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 便捷方法
const http = {
  get(url, data, options) {
    return request(url, 'GET', data, options)
  },
  post(url, data, options) {
    return request(url, 'POST', data, options)
  },
  put(url, data, options) {
    return request(url, 'PUT', data, options)
  },
  del(url, data, options) {
    return request(url, 'DELETE', data, options)
  }
}

module.exports = {
  BASE_URL,
  http
}