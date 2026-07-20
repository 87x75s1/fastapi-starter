"""
文件上传模块 Pydantic 模型
"""
from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """文件上传响应"""
    filename: str = Field(..., description="原始文件名")
    file_url: str = Field(..., description="文件访问 URL")
    file_size: int = Field(..., description="文件大小（字节）")

    model_config = {"from_attributes": True}