"""模型管理：列表、评估等"""
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends

from database import get_db
from core.security import get_require_permission
from config import settings

router = APIRouter(prefix="/api/model", tags=["模型管理"])

_BACKEND_DIR = Path(__file__).parent.parent.resolve()
MODEL_DIR = (_BACKEND_DIR / settings.model_dir).resolve()


def _scan_h5_models() -> List[dict]:
    """扫描 model_dir 和 backend 根目录下的 .h5 文件"""
    result = []
    seen = set()
    # 扫描 ml_models 目录
    if MODEL_DIR.exists() and MODEL_DIR.is_dir():
        for f in sorted(MODEL_DIR.glob("*.h5")):
            if f.name not in seen:
                seen.add(f.name)
                try:
                    size = f.stat().st_size
                except OSError:
                    size = 0
                result.append({
                    "name": f.name,
                    "path": str(f.relative_to(_BACKEND_DIR)),
                    "size": size,
                    "size_mb": round(size / (1024 * 1024), 2),
                })
    # 扫描 backend 根目录
    for f in sorted(_BACKEND_DIR.glob("*.h5")):
        if f.name not in seen:
            seen.add(f.name)
            try:
                size = f.stat().st_size
            except OSError:
                size = 0
            result.append({
                "name": f.name,
                "path": f.name,
                "size": size,
                "size_mb": round(size / (1024 * 1024), 2),
            })
    return result


@router.get("/list")
async def list_models(
    _= Depends(get_require_permission("model_manage")),
):
    """获取模型列表（.h5 文件）"""
    models = _scan_h5_models()
    return {
        "models": models,
        "model_dir": str(MODEL_DIR),
    }
