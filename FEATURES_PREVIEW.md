# 功能预览文档

本文档展示本次新增的所有功能模块，包含界面示意、操作流程和接口清单。**请先浏览此文档确认效果，满意后再部署到服务器。**

---

## 一、小程序页面结构

```
底部 TabBar
├── 首页
├── 商品   ← 新增
└── 我的

普通用户入口（在"我的"页面）
├── 我的订单   ← 新增
├── 收货地址   ← 新增
├── 意见反馈   ← 新增
└── (管理员额外看到) 管理后台   ← 新增

管理后台内部 Tab
├── 统计（数据概览）
├── 商品（增删）
├── 订单（审核状态）
├── 反馈（回复用户）
├── 配置（键值对）
└── 用户（角色管理）
```

---

## 二、页面示意

### 1. 商品列表页（`pages/product/product`）
- 网格布局，两列展示
- 每张卡片：商品图片 / 名称 / 描述 / 价格 / 分类标签
- 支持下拉刷新、上拉加载更多
- 点击卡片跳转到详情（详情页需另外开发）

### 2. 订单列表页（`pages/order/order`）
- 顶部状态 Tab：全部 / 待付款 / 已付款 / 已完成 / 已取消
- 卡片显示：订单号 / 商品列表 / 单价×数量 / 合计金额 / 状态
- 待付款订单可"取消订单"

### 3. 地址管理页（`pages/address/address`）
- 卡片列表：收货人 / 手机号 / 完整地址
- 默认地址有绿色"默认"标签
- 每张卡片可"设为默认" / "删除"
- 底部固定"新增收货地址"按钮
- 注：新增/编辑地址表单页（`pages/address/edit`）尚未生成，如需要请说

### 4. 意见反馈页（`pages/feedback/feedback`）
- 顶部：文本输入框（反馈内容）+ 联系方式输入框 + 提交按钮
- 下方：历史反馈列表，显示状态（待处理/已回复）和管理员回复内容

### 5. 管理后台页（`pages/admin/admin`）
- 顶部横向滚动 Tab：统计 / 商品 / 订单 / 反馈 / 配置 / 用户
- **统计**：4宫格显示 用户数 / 商品数 / 订单数 / 今日订单
- **商品**：表单添加商品（名称/价格/分类/图片URL/描述）+ 下方商品列表可删除
- **订单**：所有用户订单列表，可"确认付款" / "完成"
- **反馈**：所有反馈列表，可直接输入回复
- **配置**：键值对表单添加配置 + 列表可删除
- **用户**：所有用户列表，可"设为管理员" / "取消管理员"

### 6. 个人中心页更新
在原有基础上增加了菜单项：
- 我的订单
- 收货地址
- 意见反馈
- 管理后台（仅管理员可见）

---

## 三、后端接口清单

### 商品模块 `/api/product/*`
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/product/create | 创建商品 | 否 |
| GET | /api/product/list | 商品列表（支持category/status筛选） | 否 |
| GET | /api/product/{id} | 商品详情 | 否 |
| PUT | /api/product/{id} | 更新商品 | 否 |
| DELETE | /api/product/{id} | 删除商品 | 否 |

### 订单模块 `/api/order/*`
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/order/create | 创建订单 | 是 |
| GET | /api/order/list | 我的订单列表 | 是 |
| GET | /api/order/{id} | 订单详情 | 是 |
| PUT | /api/order/{id}/status | 更新订单状态 | 是 |
| DELETE | /api/order/{id} | 取消订单 | 是 |

### 地址模块 `/api/address/*`
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/address/create | 创建地址 | 是 |
| GET | /api/address/list | 我的地址列表 | 是 |
| GET | /api/address/{id} | 地址详情 | 是 |
| PUT | /api/address/{id} | 更新地址 | 是 |
| PUT | /api/address/{id}/default | 设为默认 | 是 |
| DELETE | /api/address/{id} | 删除地址 | 是 |

### 反馈模块 `/api/feedback/*`
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/feedback/create | 提交反馈 | 是 |
| GET | /api/feedback/list | 我的反馈列表 | 是 |
| GET | /api/feedback/{id} | 反馈详情 | 是 |

### 系统配置 `/api/config/*`
| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/config/create | 创建配置 | 否 |
| GET | /api/config/list | 配置列表 | 否 |
| GET | /api/config/key/{key} | 按key获取 | 否 |
| PUT | /api/config/key/{key} | 按key更新 | 否 |
| DELETE | /api/config/{id} | 删除 | 否 |

### 管理员专用 `/api/admin/*`（全部需要 role=1）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/admin/stats | 数据统计概览 |
| POST | /api/admin/product/create | 创建商品 |
| PUT | /api/admin/product/{id} | 更新商品 |
| DELETE | /api/admin/product/{id} | 删除商品 |
| GET | /api/admin/order/list | 所有订单 |
| PUT | /api/admin/order/{id}/status | 更新订单状态 |
| GET | /api/admin/feedback/list | 所有反馈 |
| PUT | /api/admin/feedback/{id}/reply | 回复反馈 |
| POST | /api/admin/config/create | 创建配置 |
| PUT | /api/admin/config/key/{key} | 更新配置 |
| DELETE | /api/admin/config/{id} | 删除配置 |
| GET | /api/admin/user/list | 用户列表 |
| PUT | /api/admin/user/{id}/role | 设置用户角色 |

---

## 四、数据库表新增

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| products | 商品表 | name, price(分), image, category, status, sort_order |
| orders | 订单表 | user_id, order_no, total_amount, status, address_snapshot |
| order_items | 订单项表 | order_id, product_id, product_name(快照), price(快照), quantity |
| addresses | 地址表 | user_id, name, phone, province/city/district, detail, is_default |
| feedbacks | 反馈表 | user_id, content, contact, status, reply |
| sys_configs | 配置表 | key(唯一), value, description |

用户表新增字段：
- `role` INTEGER DEFAULT 0（0普通用户 / 1管理员）

---

## 五、管理员账号

**默认管理员：** 手机号 `18435709771`

启动时自动将该手机号设为管理员：
- 已注册 → 启动时自动 role=1
- 未注册 → 提示注册后重启

登录该账号后，个人中心会显示"管理后台"入口。

---

## 六、关键逻辑说明

### 订单流转
```
下单 → 状态0(待付款) → 状态1(已付款) → 状态2(已完成)
              ↓
           状态3(已取消)
```
- 用户可自行取消状态0的订单
- 管理员可推进 0→1→2 状态
- 订单包含商品快照（防止商品删除后订单信息丢失）

### 地址逻辑
- 每个用户可有多个地址
- "设为默认"时会自动取消该用户的其他默认地址（互斥）
- 下单时可选择地址，选中的地址会以 JSON 快照存到订单里

### 反馈流转
- 用户提交 → 状态0(待处理)
- 管理员回复 → 状态1(已回复)
- 用户在小程序看到回复内容

### 权限体系
- 未登录：可看商品列表、商品详情、首页
- 已登录（role=0）：可下单、管理地址、提交反馈、查看订单
- 管理员（role=1）：额外可访问 `/api/admin/*` 全部接口和管理后台页面

---

## 七、什么还没做（重要）

以下功能**尚未实现**，如需要请告诉我：

1. **商品详情页**（`pages/product/detail`）
   - 商品列表点击后跳转，但详情页还没生成

2. **购物车 / 直接下单流程**
   - 商品页目前只能看，没有"加入购物车""立即下单"按钮
   - 需要额外的购物车页面或结算页

3. **地址编辑页**（`pages/address/edit`）
   - 地址列表可"点击进入编辑"，但编辑页没生成

4. **订单支付**
   - 目前订单创建后只是"待付款"状态，没有对接微信支付
   - 管理员手动改为"已付款"

5. **图片上传集成到管理后台**
   - 添加商品时"图片URL"字段目前需要手动填URL
   - 没有直接调用图片上传接口

6. **搜索/分类筛选 UI**
   - 后端支持按 category 筛选，但小程序商品页没做筛选交互

7. **首页轮播图**
   - 后端没有 banner 模块

---

## 八、下一步建议

请根据需求告诉我：

- [ ] 需要商品详情页 + 下单流程吗？
- [ ] 需要购物车吗？
- [ ] 需要接入微信支付吗？
- [ ] 需要首页轮播图/公告吗？
- [ ] 需要地址编辑页吗？
- [ ] 需要管理后台的图片上传吗？
- [ ] 其他自定义业务？

---

## 九、如何本地预览效果

小程序端：
1. 用微信开发者工具打开 `miniapp/` 目录
2. 后端服务需要先在服务器上跑起来
3. 用手机号 `18435709771` 注册登录（如果服务器已重启且账号已注册，自动是管理员）

后端 API 文档（Swagger）：
- 部署后访问 `http://60.205.126.22:8000/docs` 查看所有接口

---

**当前状态：代码已完成，打包已生成（fastapi-app.tar.gz），等待你确认后再部署。**