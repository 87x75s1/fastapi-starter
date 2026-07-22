/**
 * 认证工具模块
 * 管理 token 存储和用户信息缓存
 */

const TOKEN_KEY = 'token'
const USER_KEY = 'user_info'

/**
 * 保存登录信息
 * @param {string} token - JWT Token
 * @param {object} user - 用户信息
 */
function saveLogin(token, user) {
  wx.setStorageSync(TOKEN_KEY, token)
  wx.setStorageSync(USER_KEY, user)
}

/**
 * 获取 Token
 * @returns {string} token
 */
function getToken() {
  return wx.getStorageSync(TOKEN_KEY) || ''
}

/**
 * 获取用户信息（本地缓存）
 * @returns {object|null} 用户信息
 */
function getUserInfo() {
  const info = wx.getStorageSync(USER_KEY)
  return info || null
}

/**
 * 更新本地用户信息
 * @param {object} user - 新的用户信息
 */
function updateUserInfo(user) {
  wx.setStorageSync(USER_KEY, user)
}

/**
 * 是否已登录
 * @returns {boolean}
 */
function isLoggedIn() {
  return !!getToken()
}

/**
 * 退出登录（清除本地缓存）
 */
function logout() {
  wx.removeStorageSync(TOKEN_KEY)
  wx.removeStorageSync(USER_KEY)
}

module.exports = {
  saveLogin,
  getToken,
  getUserInfo,
  updateUserInfo,
  isLoggedIn,
  logout
}