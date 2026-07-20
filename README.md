# FastAPI 小程序后台模板

面向个人开发者的万能小程序后台骨架，支持快速开发餐饮点单、美容预约、洗车会员、社区团购等各类小程序。

## 特性

- **模块化架构**：每个业务功能独立成模块，复制模板文件夹即可新增模块
- **分层清晰**：严格遵循 Router -> Service -> Model 三层结构
- **代码复用**：BaseService 基类封装通用 CRUD，业务 Service 继承即用
- **配置分离**：敏感信息通过 .env 环境变量管理
- **异步支持**：SQLAlchemy 2.0 异步模式 + FastAPI 原生 async
- **标准输出**：统一 API 响应格式 `{code, message, data}`，全局异常捕获
- **开箱即用**：默认 SQLite 数据库，启动自动建表，自带 Swagger 文档

## 快速启动

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env，至少修改 JWT_SECRET_KEY 为一个随机长字符串
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload
```

启动成功后访问：
- 接口文档（Swagger）：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/

## 项目结构

```
app/
├── core/                    # 核心模块
│   ├── config.py            # Pydantic Settings，读取 .env
│   ├── database.py          # SQLAlchemy 异步引擎 + Base + get_db
│   ├── response.py          # 统一返回格式 success() / error()
│   ├── jwt_handler.py       # JWT Token 创建/解码
│   ├── base_service.py      # 泛型 BaseService（CRUD 基类）
│   ├── dependencies.py      # 通用依赖（get_current_user）
│   └── exceptions.py        # 自定义业务异常
├── middlewares/             # 中间件
│   └── auth.py              # 鉴权中间件（预留扩展）
├── modules/                 # 业务模块
│   ├── user/                # 用户模块（注册/登录/个人信息）
│   └── upload/              # 文件上传模块
├── utils/                   # 工具函数
│   └── common.py            # 密码加密、手机号校验等
└── main.py                  # 应用入口
```

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_NAME | 应用名称 | FastAPI 小程序后台 |
| DEBUG | 调试模式 | True |
| DATABASE_URL | 数据库连接 | sqlite+aiosqlite:///./app.db |
| JWT_SECRET_KEY | JWT 密钥 | change-me-to-a-very-long-random-secret-key |
| JWT_ALGORITHM | JWT 算法 | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Token 过期时间（分钟） | 10080（7天） |
| UPLOAD_DIR | 上传目录 | ./uploads |
| UPLOAD_URL_PREFIX | 上传文件 URL 前缀 | /static |
| MAX_FILE_SIZE | 最大文件大小（字节） | 5242880（5MB） |

## API 接口

| 方法 | 路径 | 说明 | 鉴权 |
|------|------|------|------|
| POST | /api/user/register | 用户注册 | 否 |
| POST | /api/user/login | 用户登录 | 否 |
| GET | /api/user/me | 获取当前用户信息 | 是 |
| PUT | /api/user/update | 更新用户信息 | 是 |
| POST | /api/upload/image | 上传图片 | 否 |

## 切换 MySQL

1. 安装异步 MySQL 驱动：`pip install aiomysql`
2. 修改 `.env` 中的 `DATABASE_URL`：
   ```
   DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/dbname
   ```
3. 重启服务即可，无需修改任何代码

---

## 扩展新模块指南

### 第一步：复制模板文件夹

复制 `app/modules/user/` 文件夹，重命名为新模块名（如 `product`）：

```
app/modules/product/
├── __init__.py
├── model.py       # 表模型
├── schema.py      # 请求/响应模型
├── service.py     # 业务逻辑（继承 BaseService）
└── router.py      # 路由定义
```

### 第二步：修改各文件

1. **model.py**：定义新表，继承 `Base`，设置 `__tablename__`
2. **schema.py**：定义 Pydantic 请求/响应模型
3. **service.py**：继承 `BaseService`，设置 `model = YourModel`，添加自定义业务方法
4. **router.py**：定义路由，设置 `prefix` 和 `tags`，调用 Service 层方法

### 第三步：注册路由

在 `app/main.py` 中导入并注册新路由：

```python
from app.modules.product.router import router as product_router
app.include_router(product_router)
```

### 示例：快速生成"商品模块"

1. 复制 `app/modules/user/` → `app/modules/product/`
2. `model.py`：创建 `Product` 表（name, price, stock, image, status 等字段）
3. `schema.py`：创建 `ProductCreateRequest`、`ProductResponse` 等模型
4. `service.py`：`class ProductService(BaseService): model = Product`
5. `router.py`：定义 CRUD 路由（GET/POST/PUT/DELETE），tags=["商品模块"]
6. 在 `main.py` 中注册路由
7. 重启服务，Swagger 文档自动更新