"""
定时任务调度器 - 超时订单自动取消
使用 asyncio.create_task 实现，无需额外依赖
"""
import asyncio
from app.core.database import async_session
from app.modules.order.service import OrderService


async def cancel_expired_orders_task():
    """每5分钟检查一次超时未付款订单（30分钟未付自动取消）"""
    while True:
        try:
            async with async_session() as db:
                count = await OrderService.cancel_expired_orders(db)
                await db.commit()
                if count > 0:
                    print(f"⏰ 自动取消了 {count} 个超时未付款订单")
        except Exception as e:
            print(f"❌ 超时订单取消任务异常: {e}")
        await asyncio.sleep(300)  # 5分钟执行一次


def start_scheduler():
    """启动定时任务"""
    asyncio.create_task(cancel_expired_orders_task())