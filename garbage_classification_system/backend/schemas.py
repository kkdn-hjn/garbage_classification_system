from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    role: Optional[int] = 2


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[int] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str  # 使用 str 以兼容 .local 等非标准邮箱
    role: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    users: List[UserResponse]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserPermissionsResponse(BaseModel):
    permission_codes: List[str]


class SystemStats(BaseModel):
    total_users: int
    admin_users: int
    regular_users: int


class SystemLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    log_type: str
    log_level: str
    action: str
    description: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SystemLogListResponse(BaseModel):
    total: int
    logs: List[SystemLogResponse]


class SystemSettingsResponse(BaseModel):
    model_api_url: Optional[str] = ""
    model_api_key: Optional[str] = ""
    model_secret_key: Optional[str] = ""
    log_retention_days: int = 90


class SystemSettingsUpdate(BaseModel):
    model_api_url: Optional[str] = None
    model_api_key: Optional[str] = None
    model_secret_key: Optional[str] = None
    log_retention_days: Optional[int] = None


class ServiceConfigResponse(BaseModel):
    model_api_url: Optional[str] = ""
    model_api_key: Optional[str] = ""
    model_secret_key: Optional[str] = ""


class ServiceConfigUpdate(BaseModel):
    model_api_url: Optional[str] = None
    model_api_key: Optional[str] = None
    model_secret_key: Optional[str] = None


class PermissionResponse(BaseModel):
    id: int
    name: str
    code: str
    module: Optional[str] = None

    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    permission_ids: List[int] = []

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    permission_ids: List[int]


class GarbageImageResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    category: str
    created_at: datetime

    class Config:
        from_attributes = True


class GarbageImageListResponse(BaseModel):
    total: int
    images: List[GarbageImageResponse]


class GarbageImageUpdate(BaseModel):
    category: str


class GarbageCategoryResponse(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    sort_order: int
    image_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class GarbageCategoryCreate(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class GarbageCategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class DataCollectRequest(BaseModel):
    category: str
    count: int = 20


class RecognizeLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    success: bool
    latency_ms: Optional[int] = None
    source: str
    filename: Optional[str] = None
    class_name: Optional[str] = None
    category: Optional[str] = None
    confidence: Optional[str] = None
    result_json: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecognizeLogListResponse(BaseModel):
    total: int
    items: List[RecognizeLogResponse]


class RecognizeStatsResponse(BaseModel):
    """API 调用记录看板指标（基于 recognize_logs）。"""

    today_calls: int
    today_success_rate: float  # 百分比 0–100
    today_avg_latency_ms: float
    today_failures: int
    total_calls: int
