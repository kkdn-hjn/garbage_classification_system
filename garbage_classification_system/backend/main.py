from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import engine, Base
from models import (  # noqa: F401
    User,
    SystemLog,
    SystemSetting,
    Role,
    Permission,
    RolePermission,
    GarbageImage,
    GarbageCategory,
    RecognizeLog,
)
from routers import auth, users, admin, data, model, service, recognize
from config import settings

Base.metadata.create_all(bind=engine)


def _seed_garbage_categories():
    """若垃圾分类表为空，则插入默认 12 类"""
    from sqlalchemy.orm import Session
    from database import SessionLocal
    from models import GarbageCategory, DEFAULT_CATEGORIES
    db = SessionLocal()
    try:
        if db.query(GarbageCategory).count() == 0:
            for i, (name, typ, desc) in enumerate(DEFAULT_CATEGORIES):
                db.add(GarbageCategory(name=name, type=typ, description=desc, sort_order=i))
            db.commit()
    finally:
        db.close()


_seed_garbage_categories()

# 使用绝对路径，避免因工作目录不同导致找不到文件
_BACKEND_DIR = Path(__file__).parent.resolve()
UPLOAD_DIR = (_BACKEND_DIR / settings.upload_dir).resolve()
LAJI1_DIR = (_BACKEND_DIR / settings.laji1_dir).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
if not LAJI1_DIR.exists():
    LAJI1_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="基于百度智能云的垃圾分类识别系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(data.router)
app.include_router(model.router)
app.include_router(service.router)
app.include_router(recognize.router)

app.mount("/laji3", StaticFiles(directory=str(UPLOAD_DIR)), name="laji3")
app.mount("/laji1", StaticFiles(directory=str(LAJI1_DIR)), name="laji1")


@app.get("/")
async def root():
    return {"message": "基于百度智能云的垃圾分类识别系统 API"}
