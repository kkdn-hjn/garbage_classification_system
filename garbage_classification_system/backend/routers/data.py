import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import get_db
from models import GarbageImage, GarbageCategory, GARBAGE_CATEGORIES, User
from schemas import (
    GarbageImageResponse,
    GarbageImageListResponse,
    GarbageImageUpdate,
    GarbageCategoryResponse,
    GarbageCategoryCreate,
    GarbageCategoryUpdate,
    DataCollectRequest,
)
from core.security import get_require_permission
from config import settings

router = APIRouter(prefix="/api/data", tags=["数据管理"])

_BACKEND_DIR = Path(__file__).parent.parent.resolve()
UPLOAD_DIR = (_BACKEND_DIR / settings.upload_dir).resolve()
LAJI1_DIR = (_BACKEND_DIR / settings.laji1_dir).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

LAJI1_PREFIX = "laji1/"


def _resolve_image_path(filepath: str) -> Path:
    """根据 filepath 解析实际文件路径：laji1/xxx 走 laji1 目录，否则走 laji3"""
    if filepath.startswith(LAJI1_PREFIX):
        return LAJI1_DIR / filepath[len(LAJI1_PREFIX):]
    return UPLOAD_DIR / filepath


def _get_ext(filename: str) -> str:
    return Path(filename).suffix.lower() or ".jpg"


def _allowed_ext(ext: str) -> bool:
    return ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")


def _get_valid_categories(db: Session) -> List[str]:
    """从数据库获取有效分类名列表，用于校验"""
    cats = db.query(GarbageCategory.name).order_by(GarbageCategory.sort_order).all()
    return [c[0] for c in cats] if cats else GARBAGE_CATEGORIES


# ========== 垃圾分类管理 ==========


@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """数据集统计：各类别数量、图片总数"""
    cats = db.query(GarbageCategory).order_by(GarbageCategory.sort_order).all()
    items = []
    total = 0
    for c in cats:
        count = db.query(GarbageImage).filter(GarbageImage.category == c.name).count()
        items.append({"name": c.name, "count": count})
        total += count
    max_count = max((x["count"] for x in items), default=0)
    return {
        "total": total,
        "category_count": len(items),
        "items": items,
        "max_count": max_count,
    }


@router.get("/categories/list", response_model=List[GarbageCategoryResponse])
async def list_categories(
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """获取所有垃圾分类（含图片数量）"""
    cats = db.query(GarbageCategory).order_by(GarbageCategory.sort_order).all()
    result = []
    for c in cats:
        count = db.query(GarbageImage).filter(GarbageImage.category == c.name).count()
        data = GarbageCategoryResponse.model_validate(c).model_dump()
        data["image_count"] = count
        result.append(GarbageCategoryResponse(**data))
    return result


@router.post("/categories", response_model=GarbageCategoryResponse)
async def create_category(
    body: GarbageCategoryCreate,
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """新增垃圾分类"""
    if db.query(GarbageCategory).filter(GarbageCategory.name == body.name).first():
        raise HTTPException(status_code=400, detail="分类名称已存在")
    cat = GarbageCategory(name=body.name, type=body.type, description=body.description, sort_order=body.sort_order)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return GarbageCategoryResponse.model_validate(cat)


@router.put("/categories/{category_id}", response_model=GarbageCategoryResponse)
async def update_category(
    category_id: int,
    body: GarbageCategoryUpdate,
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """更新垃圾分类"""
    cat = db.query(GarbageCategory).filter(GarbageCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    if body.name is not None:
        if body.name != cat.name and db.query(GarbageCategory).filter(GarbageCategory.name == body.name).first():
            raise HTTPException(status_code=400, detail="分类名称已存在")
        old_name = cat.name
        cat.name = body.name
        # 同步更新 GarbageImage 的 category 字段
        db.query(GarbageImage).filter(GarbageImage.category == old_name).update({GarbageImage.category: body.name})
        # 若物理目录存在，需重命名 laji3/旧名 -> laji3/新名
        old_dir = UPLOAD_DIR / old_name
        new_dir = UPLOAD_DIR / body.name
        if old_dir.is_dir() and not new_dir.exists():
            old_dir.rename(new_dir)
    if body.type is not None:
        cat.type = body.type
    if body.description is not None:
        cat.description = body.description
    if body.sort_order is not None:
        cat.sort_order = body.sort_order
    db.commit()
    db.refresh(cat)
    return GarbageCategoryResponse.model_validate(cat)


@router.post("/collect")
def collect_images_api(
    body: DataCollectRequest,
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """选择分类从百度图片采集，保存到 laji3 并写入 garbage_images。搜索关键词用该类别的描述"""
    cat = db.query(GarbageCategory).filter(GarbageCategory.name == body.category).first()
    if not cat:
        raise HTTPException(status_code=400, detail="分类不存在，请在垃圾类别管理中配置")
    count = max(1, min(body.count, 50))  # 限制 1-50 张
    from services.pacong import collect_images

    search_keyword = (cat.description or "").strip() or cat.name
    ok, fail = collect_images(body.category, count, UPLOAD_DIR, db, search_keyword=search_keyword)
    db.commit()
    return {"message": "采集完成", "success": ok, "failed": fail, "category": body.category}


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """删除垃圾分类（若有关联图片则拒绝）"""
    cat = db.query(GarbageCategory).filter(GarbageCategory.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="分类不存在")
    count = db.query(GarbageImage).filter(GarbageImage.category == cat.name).count()
    if count > 0:
        raise HTTPException(status_code=400, detail=f"该分类下还有 {count} 张图片，请先迁移或删除后再操作")
    db.delete(cat)
    db.commit()
    return {"message": "ok"}


# ========== 垃圾图片 ==========


@router.get("/images", response_model=GarbageImageListResponse)
async def list_images(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    query = db.query(GarbageImage)
    if category:
        query = query.filter(GarbageImage.category == category)
    query = query.order_by(GarbageImage.created_at.desc())
    total = query.count()
    images = query.offset(skip).limit(limit).all()
    return {"total": total, "images": images}


@router.get("/images/categories")
async def get_categories(
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    """供图片管理下拉框使用的分类列表"""
    return {"categories": _get_valid_categories(db)}


async def _get_image_file_auth(request: Request, db: Session = Depends(get_db)):
    """图片接口认证：支持 Header Bearer 或 Query token（供 img src 使用）"""
    from models import RolePermission, Permission
    token = request.query_params.get("token")
    if not token:
        auth = request.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        perm = db.query(Permission).filter(Permission.code == "data_manage").first()
        if perm:
            rp = db.query(RolePermission).filter(
                RolePermission.role_id == user.role,
                RolePermission.permission_id == perm.id,
            ).first()
            if not rp:
                raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


@router.get("/images/file/{image_id}")
async def get_image_file(
    image_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_get_image_file_auth),
):
    """返回图片文件（需登录），解决中文路径编码问题，支持 ?token=xxx 供 img 标签使用"""
    img = db.query(GarbageImage).filter(GarbageImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    full_path = _resolve_image_path(img.filepath)
    if not full_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(full_path), filename=img.filename)


@router.post("/images/upload", response_model=GarbageImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    category: str = Form("其他"),
    rel_path: str = Form(None),  # 前端传入的路径，如 "纸类/1.jpg"，用于从文件夹名推断分类
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    ext = _get_ext(file.filename or "")
    if not _allowed_ext(ext):
        raise HTTPException(status_code=400, detail="只支持 jpg/png/gif/webp/bmp 格式")
    valid_cats = _get_valid_categories(db)
    if category not in valid_cats:
        category = "其他" if "其他" in valid_cats else (valid_cats[0] if valid_cats else "其他")
    if rel_path:
        for part in rel_path.replace("\\", "/").split("/")[:-1]:
            if part in valid_cats:
                category = part
                break
    unique = uuid.uuid4().hex[:8]
    safe_name = (file.filename or "img").split("/")[-1][-50:]
    filename = f"{unique}_{safe_name}"
    category_dir = UPLOAD_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)
    filepath = category_dir / filename
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    rel_path = f"{category}/{filename}"
    img = GarbageImage(filename=filename, filepath=rel_path, category=category)
    db.add(img)
    db.commit()
    db.refresh(img)
    return img


@router.put("/images/{image_id}", response_model=GarbageImageResponse)
async def update_image(
    image_id: int,
    body: GarbageImageUpdate,
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    img = db.query(GarbageImage).filter(GarbageImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    if body.category in _get_valid_categories(db):
        img.category = body.category
    db.commit()
    db.refresh(img)
    return img


@router.delete("/images/{image_id}")
async def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    _= Depends(get_require_permission("data_manage")),
):
    img = db.query(GarbageImage).filter(GarbageImage.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    # 仅删除 laji3 中的物理文件，laji1 为引用不删原文件
    if not img.filepath.startswith(LAJI1_PREFIX):
        full_path = UPLOAD_DIR / img.filepath
        if full_path.is_file():
            try:
                full_path.unlink()
            except OSError:
                pass
    db.delete(img)
    db.commit()
    return {"message": "ok"}
