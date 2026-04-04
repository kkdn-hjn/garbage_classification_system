from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserRole
from schemas import UserCreate, UserResponse, UserUpdate, UserListResponse
from core.security import get_password_hash, get_require_permission
from core.logging import create_log, get_client_ip, get_user_agent

from models import LogType, LogLevel

router = APIRouter(prefix="/api/users", tags=["用户管理"])


def _log_user_action(db, action, current_user, description, request):
    create_log(
        db=db,
        action=action,
        log_type=LogType.USER.value,
        log_level=LogLevel.INFO.value,
        user_id=current_user.id,
        username=current_user.username,
        description=description,
        ip_address=get_client_ip(request) if request else None,
        user_agent=get_user_agent(request) if request else None,
    )


@router.get("", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("user_manage")),
):
    query = db.query(User)
    if search:
        query = query.filter(
            (User.username.contains(search)) | (User.email.contains(search))
        )
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return {"total": total, "users": users}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("user_manage")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("user_manage")),
):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        _log_user_action(db, "创建用户失败", current_user, f"用户名 {user.username} 已存在", request)
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        _log_user_action(db, "创建用户失败", current_user, f"邮箱 {user.email} 已存在", request)
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.role not in [UserRole.ADMIN.value, UserRole.USER.value]:
        raise HTTPException(status_code=400, detail="Invalid role")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    role_name = "管理员" if user.role == UserRole.ADMIN.value else "普通用户"
    _log_user_action(db, "创建用户", current_user, f"创建用户: {user.username}, 角色: {role_name}", request)
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("user_manage")),
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == current_user.id and user_update.role and user_update.role != current_user.role:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    changes = []
    if user_update.username is not None:
        existing = db.query(User).filter(User.username == user_update.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        changes.append(f"用户名: {db_user.username} -> {user_update.username}")
        db_user.username = user_update.username
    if user_update.email is not None:
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        changes.append(f"邮箱: {db_user.email} -> {user_update.email}")
        db_user.email = user_update.email
    if user_update.password is not None:
        changes.append("密码已更新")
        db_user.password = get_password_hash(user_update.password)
    if user_update.role is not None:
        if user_update.role not in [UserRole.ADMIN.value, UserRole.USER.value]:
            raise HTTPException(status_code=400, detail="Invalid role")
        changes.append(f"角色已更新")
        db_user.role = user_update.role
    db.commit()
    db.refresh(db_user)
    if changes:
        _log_user_action(db, "更新用户", current_user, f"更新用户 {db_user.username}: {', '.join(changes)}", request)
    return db_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("user_manage")),
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    deleted_username = db_user.username
    deleted_email = db_user.email
    db.delete(db_user)
    db.commit()
    _log_user_action(db, "删除用户", current_user, f"删除用户: {deleted_username} ({deleted_email})", request)
    return {"message": "User deleted successfully"}
