from database import SessionLocal, engine, Base
from models import User, UserRole, SystemSetting, Role, Permission, RolePermission
from core.security import get_password_hash

Base.metadata.create_all(bind=engine)

# 权限定义 (code, name, module)
PERMISSIONS = [
    ("data_manage", "数据管理", "数据"),
    ("model_manage", "模型管理", "模型"),
    ("service_manage", "服务管理", "服务"),
    ("recognize_test", "识别测试", "识别"),
    ("user_manage", "用户管理", "系统"),
    ("role_manage", "角色权限", "系统"),
    ("system_logs", "操作日志", "系统"),
    ("system_settings", "系统设置", "系统"),
]

db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            password=get_password_hash("admin123"),
            role=UserRole.ADMIN.value,
        )
        db.add(admin)
        db.commit()
        print("默认管理员已创建: admin / admin123")
    else:
        print("管理员已存在")

    # 初始化系统设置默认值
    defaults = [
        ("model_api_url", "", "百度智能云识别API地址"),
        ("model_api_key", "", "百度智能云API Key"),
        ("model_secret_key", "", "百度智能云Secret Key"),
        ("log_retention_days", "90", "操作日志保存时长(天)"),
    ]
    for key, value, desc in defaults:
        if db.query(SystemSetting).filter(SystemSetting.key == key).first() is None:
            db.add(SystemSetting(key=key, value=value, description=desc))
    db.commit()
    print("系统设置已初始化")

    # 初始化角色
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    if not admin_role:
        admin_role = Role(name="管理员", code="admin", description="拥有全部权限")
        db.add(admin_role)
        db.flush()
    user_role = db.query(Role).filter(Role.code == "user").first()
    if not user_role:
        user_role = Role(name="普通用户", code="user", description="基础功能权限")
        db.add(user_role)
        db.flush()

    # 初始化权限
    perm_map = {}
    for code, name, module in PERMISSIONS:
        p = db.query(Permission).filter(Permission.code == code).first()
        if not p:
            p = Permission(name=name, code=code, module=module)
            db.add(p)
            db.flush()
        perm_map[code] = p.id

    # 管理员拥有全部权限
    for pid in perm_map.values():
        if not db.query(RolePermission).filter(RolePermission.role_id == admin_role.id, RolePermission.permission_id == pid).first():
            db.add(RolePermission(role_id=admin_role.id, permission_id=pid))

    # 普通用户：数据、模型、服务、识别（无系统管理）
    user_perm_codes = ["data_manage", "model_manage", "service_manage", "recognize_test"]
    for code in user_perm_codes:
        pid = perm_map.get(code)
        if pid and not db.query(RolePermission).filter(RolePermission.role_id == user_role.id, RolePermission.permission_id == pid).first():
            db.add(RolePermission(role_id=user_role.id, permission_id=pid))

    db.commit()
    print("角色权限已初始化")
finally:
    db.close()
