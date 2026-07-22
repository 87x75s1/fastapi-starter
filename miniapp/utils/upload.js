/**
 * 文件上传工具
 * 封装 wx.uploadFile，自动带上 Token
 */

const { BASE_URL } = require('./request')
const auth = require('./auth')

/**
 * 上传图片到服务器
 * @param {object} options - { sourceType: ['album', 'camera'] }
 * @returns {Promise<object>} - { filename, file_url, file_size }
 */
function uploadImage(options = {}) {
  const { sourceType = ['album', 'camera'] } = options

  return new Promise((resolve, reject) => {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType,
      sizeType: ['compressed'],
      success(chooseRes) {
        const tempFilePath = chooseRes.tempFiles[0].tempFilePath
        const token = auth.getToken()

        if (!token) {
          wx.showToast({ title: '请先登录', icon: 'none' })
          reject(new Error('未登录'))
          return
        }

        wx.showLoading({ title: '上传中...', mask: true })

        wx.uploadFile({
          url: `${BASE_URL}/api/upload/image`,
          filePath: tempFilePath,
          name: 'file',
          header: {
            'Authorization': `Bearer ${token}`
          },
          success(res) {
            wx.hideLoading()
            const data = JSON.parse(res.data)
            if (data.code === 0) {
              wx.showToast({ title: '上传成功', icon: 'success' })
              resolve(data.data)
            } else {
              wx.showToast({ title: data.message || '上传失败', icon: 'none' })
              reject(new Error(data.message))
            }
          },
          fail(err) {
            wx.hideLoading()
            wx.showToast({ title: '上传失败', icon: 'none' })
            reject(err)
          }
        })
      },
      fail(err) {
        // 用户取消选择
        reject(err)
      }
    })
  })
}

module.exports = {
  uploadImage
}