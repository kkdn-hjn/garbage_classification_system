from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import User, UserRole, RolePermission, Permission
from schemas import RegisterRequest, UserLogin, UserResponse, Token, UserPermissionsResponse
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_admin_user,
)
from core.logging import log_auth_action
from config import settings

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
async def register(user: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        log_auth_action(
            db, "用户注册失败", user.username, "用户名已存在", request, success=False
        )
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        log_auth_action(
            db, "用户注册失败", user.username, "邮箱已存在", request, success=False
        )
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=UserRole.USER.value,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    log_auth_action(
        db, "用户注册", user.username, f"新用户注册: {user.email}", request, success=True
    )
    return db_user


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == user_credentials.username).first()
    if not user or not verify_password(user_credentials.password, user.password):
        log_auth_action(
            db,
            "用户登录失败",
            user_credentials.username,
            "用户名或密码错误",
            request,
            success=False,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log_auth_action(
        db,
        "用户登录",
        user.username,
        f"用户 {user.username} 登录成功",
        request,
        success=True,
        user_id=user.id,
    )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/permissions", response_model=UserPermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rps = db.query(RolePermission).filter(RolePermission.role_id == current_user.role).all()
    perm_ids = [rp.permission_id for rp in rps]
    perms = db.query(Permission).filter(Permission.id.in_(perm_ids)).all() if perm_ids else []
    return UserPermissionsResponse(permission_codes=[p.code for p in perms])


@router.get("/admin")
async def admin_only(current_user: User = Depends(get_current_admin_user)):
    return {"message": "Admin access granted", "user": current_user.username}
