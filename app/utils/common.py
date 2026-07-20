"""
通用工具函数
提供密码加密、手机号校验等常用功能
"""
import re
import bcrypt


def hash_password(password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希
    :param password: 明文密码
    :return: 哈希后的密码字符串
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码与哈希密码是否匹配
    :param plain_password: 明文密码
    :param hashed_password: 哈希密码
    :return: 是否匹配
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def validate_phone(phone: str) -> bool:
    """
    校验中国大陆手机号格式
    规则：1开头，第二位为3-9，共11位数字
    :param phone: 手机号字符串
    :return: 是否合法
    """
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    """
    校验邮箱格式
    :param email: 邮箱字符串
    :return: 是否合法
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))