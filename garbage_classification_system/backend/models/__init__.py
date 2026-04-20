from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(enum.Enum):
    ADMIN = 1
    USER = 2


class LogLevel(enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"


class LogType(enum.Enum):
    AUTH = "认证"
    USER = "用户管理"
    SYSTEM = "系统"
    OTHER = "其他"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    role = Column(Integer, nullable=False, default=UserRole.USER.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(255), nullable=True)
    log_type = Column(String(50), nullable=False, index=True)
    log_level = Column(String(20), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", foreign_keys=[user_id])


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)
    module = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", backref="role_permissions")
    permission = relationship("Permission", backref="role_permissions")


# 默认分类（无 DB 时的回退）
GARBAGE_CATEGORIES = [
    "纸类", "塑料", "玻璃", "金属", "织物",
    "厨余", "有害", "可回收物", "电池", "灯管", "药品", "其他"
]

DEFAULT_CATEGORIES = [
    ("纸类", "可回收", "废纸、纸箱、书刊等"),
    ("塑料", "可回收", "塑料瓶、塑料袋、塑料制品等"),
    ("玻璃", "可回收", "玻璃瓶、碎玻璃等"),
    ("金属", "可回收", "易拉罐、金属制品等"),
    ("织物", "可回收", "旧衣物、纺织物等"),
    ("厨余", "厨余垃圾", "剩饭剩菜、果皮、菜叶等"),
    ("有害", "有害垃圾", "油漆、农药、化妆品等"),
    ("可回收物", "可回收", "其他可回收物品"),
    ("电池", "有害垃圾", "各类电池"),
    ("灯管", "有害垃圾", "日光灯管、节能灯等"),
    ("药品", "有害垃圾", "过期药品、药品包装等"),
    ("其他", "其他", "无法归类的垃圾"),
]


class GarbageCategory(Base):
    __tablename__ = "garbage_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=True)  # 可回收/厨余/有害/其他
    description = Column(String(255), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GarbageImage(Base):
    __tablename__ = "garbage_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, index=True)
    filepath = Column(String(500), nullable=False)
    category = Column(String(50), nullable=False, default="其他", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RecognizeLog(Base):
    """在线识别与 API 调用记录（用于识别历史与统计看板）。"""

    __tablename__ = "recognize_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(255), nullable=True, index=True)
    success = Column(Boolean, nullable=False, default=False, index=True)
    latency_ms = Column(Integer, nullable=True)
    source = Column(String(32), nullable=False, default="none", index=True)  # local / easydl / none
    filename = Column(String(512), nullable=True)
    class_name = Column(String(128), nullable=True)
    category = Column(String(128), nullable=True)
    confidence = Column(String(64), nullable=True)  # 存展示用字符串，如 "95.20"
    result_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", foreign_keys=[user_id])
