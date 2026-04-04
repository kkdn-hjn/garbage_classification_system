from sqlalchemy.orm import Session
from models import SystemLog, LogLevel, LogType
from typing import Optional
from fastapi import Request


def get_client_ip(request: Request) -> Optional[str]:
    if request.client:
        return request.client.host
    return None


def get_user_agent(request: Request) -> Optional[str]:
    return request.headers.get("user-agent")


def create_log(
    db: Session,
    action: str,
    log_type: str,
    log_level: str = LogLevel.INFO.value,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    log = SystemLog(
        user_id=user_id,
        username=username,
        log_type=log_type,
        log_level=log_level,
        action=action,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    db.commit()
    return log


def log_auth_action(
    db: Session,
    action: str,
    username: Optional[str] = None,
    description: Optional[str] = None,
    request: Optional[Request] = None,
    log_level: str = LogLevel.INFO.value,
    success: bool = True,
    user_id: Optional[int] = None,
):
    ip_address = get_client_ip(request) if request else None
    user_agent = get_user_agent(request) if request else None
    level = LogLevel.SUCCESS.value if success else LogLevel.WARNING.value
    return create_log(
        db=db,
        action=action,
        log_type=LogType.AUTH.value,
        log_level=level,
        user_id=user_id,
        username=username,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
    )
