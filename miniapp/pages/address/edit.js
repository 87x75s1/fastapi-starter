const { http } = require('../../utils/request')
const auth = require('../../utils/auth')

Page({
  data: {
    id: null,
    isEdit: false,
    name: '',
    phone: '',
    province: '',
    city: '',
    district: '',
    detail: '',
    is_default: 0,
    region: ['山西省', '临汾市', '尧都区'],
    customRegion: false
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ id: options.id, isEdit: true })
      this.loadAddress(options.id)
    }
  },

  async loadAddress(id) {
    try {
      const addrs = await http.get('/api/address/list', {}, { auth: true })
      const addr = addrs.find(a => a.id === Number(id))
      if (addr) {
        this.setData({
          name: addr.name,
          phone: addr.phone,
          province: addr.province,
          city: addr.city,
          district: addr.district,
          detail: addr.detail,
          is_default: addr.is_default,
          region: [addr.province, addr.city, addr.district]
        })
      }
    } catch (err) {}
  },

  onRegionChange(e) {
    const region = e.detail.value
    this.setData({
      region,
      province: region[0],
      city: region[1],
      district: region[2]
    })
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [field]: e.detail.value })
  },

  onDefaultChange(e) {
    this.setData({ is_default: e.detail.value ? 1 : 0 })
  },

  async onSave() {
    const { id, isEdit, name, phone, province, city, district, detail, is_default } = this.data
    if (!name.trim()) { wx.showToast({ title: '请输入姓名', icon: 'none' }); return }
    if (!phone.trim() || phone.length < 11) { wx.showToast({ title: '请输入正确手机号', icon: 'none' }); return }
    if (!detail.trim()) { wx.showToast({ title: '请输入详细地址', icon: 'none' }); return }

    const body = { name, phone, province, city, district, detail, is_default }
    try {
      if (isEdit) {
        await http.put(`/api/address/${id}`, body, { auth: true })
        wx.showToast({ title: '保存成功', icon: 'success' })
      } else {
        await http.post('/api/address/create', body, { auth: true })
        wx.showToast({ title: '添加成功', icon: 'success' })
      }
      setTimeout(() => wx.navigateBack(), 1000)
    } catch (err) {}
  }
})