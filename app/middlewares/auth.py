# 鉴权中间件模块
# 当前鉴权通过 core/dependencies.py 中的 get_current_user 依赖实现
# 如需全局鉴权（排除白名单），可在此模块中实现 BaseHTTPMiddleware