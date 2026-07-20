"""
文件上传 Service 层
处理文件保存逻辑，返回可访问的 URL
"""
import os
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.core.config import get_settings
from app.core.exceptions import BusinessException

settings = get_settings()

# 允许的 MIME 类型映射（与扩展名对应）
ALLOWED_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class UploadService:
    """文件上传服务"""

    @staticmethod
    async def save_image(file: UploadFile) -> dict:
        """
        保存上传的图片文件
        :param file: FastAPI UploadFile 对象
        :return: {"filename": 原始文件名, "file_url": 访问URL, "file_size": 文件大小}
        :raises BusinessException: 文件类型不允许或文件过大
        """
        # 校验文件扩展名
        if file.filename:
            ext = Path(file.filename).suffix.lower()
        else:
            ext = ""

        if ext not in settings.ALLOWED_EXTENSIONS:
            raise BusinessException(
                message=f"不支持的文件类型 {ext}，仅支持 {settings.ALLOWED_EXTENSIONS}",
                code=400,
            )

        # 校验 MIME 类型
        expected_mime = ALLOWED_MIME_TYPES.get(ext)
        if expected_mime and file.content_type and not file.content_type.startswith(expected_mime.split("/")[0]):
            raise BusinessException(
                message=f"文件 MIME 类型不匹配，期望 {expected_mime}，实际 {file.content_type}",
                code=400,
            )

        # 读取文件内容并校验大小
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise BusinessException(
                message=f"文件大小超过限制（最大 {settings.MAX_FILE_SIZE // 1024 // 1024}MB）",
                code=400,
            )

        # 校验文件头魔数（防止伪造扩展名）
        if not UploadService._validate_image_magic(content, ext):
            raise BusinessException(
                message="文件内容与扩展名不匹配，可能为伪造文件",
                code=400,
            )

        # 确保上传目录存在
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一文件名，避免冲突
        saved_name = f"{uuid.uuid4().hex}{ext}"
        file_path = upload_dir / saved_name

        # 写入文件
        with open(file_path, "wb") as f:
            f.write(content)

        # 构建访问 URL
        file_url = f"{settings.UPLOAD_URL_PREFIX}/{saved_name}"

        return {
            "filename": file.filename or saved_name,
            "file_url": file_url,
            "file_size": len(content),
        }

    @staticmethod
    def _validate_image_magic(content: bytes, ext: str) -> bool:
        """
        校验文件头魔数，防止伪造扩展名上传恶意文件
        :param content: 文件二进制内容
        :param ext: 文件扩展名
        :return: 是否匹配
        """
        if len(content) < 4:
            return False

        # 常见图片格式的文件头魔数
        magic_numbers = {
            ".jpg": [b"\xff\xd8\xff"],
            ".jpeg": [b"\xff\xd8\xff"],
            ".png": [b"\x89PNG"],
            ".gif": [b"GIF8"],
            ".webp": [b"RIFF"],  # WebP 以 RIFF 开头
        }

        expected = magic_numbers.get(ext)
        if expected is None:
            return True  # 非已知格式不做校验

        return any(content.startswith(m) for m in expected)