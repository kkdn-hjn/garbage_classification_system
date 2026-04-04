from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import User, UserRole, SystemLog, SystemSetting, Role, Permission, RolePermission
from schemas import (
    SystemStats,
    SystemLogListResponse,
    SystemSettingsResponse,
    SystemSettingsUpdate,
    PermissionResponse,
    RoleResponse,
    RolePermissionUpdate,
)
from core.security import get_current_admin_user, get_require_permission

router = APIRouter(prefix="/api/admin", tags=["系统管理"])

_SETTING_KEYS = {
    "model_api_url": ("", str),
    "model_api_key": ("", str),
    "model_secret_key": ("", str),
    "log_retention_days": (90, int),
}


def _get_settings(db: Session) -> dict:
    rows = db.query(SystemSetting).all()
    data = {r.key: r.value for r in rows}
    result = {}
    for key, (default, dtype) in _SETTING_KEYS.items():
        raw = data.get(key)
        if raw is None:
            result[key] = default
        elif dtype == int:
            try:
                result[key] = int(raw)
            except (ValueError, TypeError):
                result[key] = default
        else:
            result[key] = raw or default
    return result


def _save_settings(db: Session, updates: dict):
    for key, value in updates.items():
        if key not in _SETTING_KEYS:
            continue
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        str_val = str(value) if value is not None else ""
        if row:
            row.value = str_val
        else:
            db.add(SystemSetting(key=key, value=str_val))
    db.commit()


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("system_logs")),
):
    total_users = db.query(User).count()
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN.value).count()
    regular_users = db.query(User).filter(User.role == UserRole.USER.value).count()
    return {
        "total_users": total_users,
        "admin_users": admin_users,
        "regular_users": regular_users,
    }


@router.get("/logs", response_model=SystemLogListResponse)
async def get_system_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    log_type: str = Query(None, description="认证/用户管理/系统"),
    log_level: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("system_logs")),
):
    query = db.query(SystemLog)
    if log_type:
        query = query.filter(SystemLog.log_type == log_type)
    if log_level:
        query = query.filter(SystemLog.log_level == log_level)
    if search:
        query = query.filter(
            or_(
                SystemLog.username.contains(search),
                SystemLog.action.contains(search),
                SystemLog.description.contains(search),
            )
        )
    query = query.order_by(SystemLog.created_at.desc())
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    return {"total": total, "logs": logs}


@router.get("/settings", response_model=SystemSettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("system_settings")),
):
    data = _get_settings(db)
    return SystemSettingsResponse(**data)


@router.put("/settings", response_model=SystemSettingsResponse)
async def update_settings(
    body: SystemSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("system_settings")),
):
    updates = body.model_dump(exclude_none=True)
    _save_settings(db, updates)
    return SystemSettingsResponse(**_get_settings(db))


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("role_manage")),
):
    perms = db.query(Permission).order_by(Permission.module, Permission.id).all()
    return perms


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("role_manage")),
):
    roles = db.query(Role).order_by(Role.id).all()
    result = []
    for r in roles:
        perm_ids = [rp.permission_id for rp in db.query(RolePermission).filter(RolePermission.role_id == r.id).all()]
        result.append(RoleResponse(id=r.id, name=r.name, code=r.code, description=r.description, permission_ids=perm_ids))
    return result


@router.put("/roles/{role_id}/permissions", response_model=RoleResponse)
async def update_role_permissions(
    role_id: int,
    body: RolePermissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("role_manage")),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.query(RolePermission).filter(RolePermission.role_id == role_id).delete()
    for pid in body.permission_ids:
        perm = db.query(Permission).filter(Permission.id == pid).first()
        if perm:
            db.add(RolePermission(role_id=role_id, permission_id=pid))
    db.commit()
    perm_ids = [rp.permission_id for rp in db.query(RolePermission).filter(RolePermission.role_id == role_id).all()]
    return RoleResponse(id=role.id, name=role.name, code=role.code, description=role.description, permission_ids=perm_ids)
