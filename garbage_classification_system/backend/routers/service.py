"""识别服务：EasyDL 图像分类公有云 API（与官方 Python3 示例一致：requests 鉴权 + requests.post json=PARAMS）。"""
import base64
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import SystemSetting
from schemas import ServiceConfigResponse, ServiceConfigUpdate
from core.security import get_require_permission

router = APIRouter(prefix="/api/service", tags=["识别服务"])

_KEYS = ("model_api_url", "model_api_key", "model_secret_key")

_IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# 与 EasyDL 文档示例一致
OAUTH_URL_TEMPLATE = (
    "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials"
    "&client_id={}&client_secret={}"
)


def _parse_requests_json(resp: requests.Response) -> Tuple[Optional[dict], Optional[str]]:
    """
    安全解析 requests 响应为 JSON。空 body 或非 JSON（如 HTML 错误页）时返回错误说明，
    避免出现 Expecting value: line 1 column 1 (char 0)。
    """
    text = (resp.text or "").strip()
    if not text:
        return None, f"响应体为空（HTTP {resp.status_code}），请检查网络、代理或是否可访问 aip.baidubce.com"
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        return None, f"响应非 JSON（HTTP {resp.status_code}）：{text[:400]}"


def _get_kv(db: Session) -> Dict[str, str]:
    rows = db.query(SystemSetting).filter(SystemSetting.key.in_(_KEYS)).all()
    data = {r.key: (r.value or "") for r in rows}
    for k in _KEYS:
        data.setdefault(k, "")
    return data


def _save_kv(db: Session, updates: Dict[str, Optional[str]]):
    for key in _KEYS:
        if key not in updates:
            continue
        val = updates[key]
        if val is None:
            continue
        row = db.query(SystemSetting).filter(SystemSetting.key == key).first()
        s = str(val)
        if row:
            row.value = s
        else:
            db.add(SystemSetting(key=key, value=s))
    db.commit()


def _oauth_get_token(api_key: str, secret_key: str) -> Tuple[Optional[str], int, Optional[str]]:
    """
    与用户提供的代码一致：
    auth_url = "...token?grant_type=client_credentials&client_id={}&client_secret={}".format(...)
    auth_resp = requests.get(auth_url)
    ACCESS_TOKEN = auth_resp_json["access_token"]
    """
    if not (api_key or "").strip() or not (secret_key or "").strip():
        return None, 0, "未配置 API Key 或 Secret Key"

    auth_url = OAUTH_URL_TEMPLATE.format(api_key.strip(), secret_key.strip())
    t0 = time.perf_counter()
    try:
        auth_resp = requests.get(auth_url, timeout=15)
        ms = int((time.perf_counter() - t0) * 1000)
        auth_resp_json, parse_err = _parse_requests_json(auth_resp)
        if parse_err:
            return None, ms, parse_err
        assert auth_resp_json is not None
        tok = auth_resp_json.get("access_token")
        if tok:
            return tok, ms, None
        return None, ms, auth_resp_json.get("error_description") or auth_resp_json.get("error") or auth_resp.text[:300]
    except requests.RequestException as e:
        ms = int((time.perf_counter() - t0) * 1000)
        return None, ms, str(e)


def _easydl_classify_requests(
    model_api_url: str,
    access_token: str,
    image_b64: str,
    top_num: int = 2,
) -> Tuple[bool, int, Optional[str], Optional[dict]]:
    """
    与用户提供的代码一致：
    PARAMS = {"top_num": n, "image": base64_str}
    request_url = "{}?access_token={}".format(MODEL_API_URL, ACCESS_TOKEN)
    response = requests.post(url=request_url, json=PARAMS)
    """
    params = {"top_num": top_num, "image": image_b64}
    request_url = "{}?access_token={}".format(model_api_url.strip().rstrip("/"), access_token)
    t0 = time.perf_counter()
    try:
        response = requests.post(url=request_url, json=params, timeout=45)
        ms = int((time.perf_counter() - t0) * 1000)
        response_json, parse_err = _parse_requests_json(response)
        if parse_err:
            return False, ms, parse_err, None
        assert response_json is not None
        if response_json.get("error_code"):
            return False, ms, response_json.get("error_msg") or str(response_json.get("error_code")), response_json
        return True, ms, None, response_json
    except requests.RequestException as e:
        ms = int((time.perf_counter() - t0) * 1000)
        return False, ms, str(e), None


def _find_probe_images() -> List[Path]:
    backend_dir = Path(__file__).parent.parent.resolve()
    root = (backend_dir / settings.upload_dir).resolve()
    if not root.is_dir():
        return []
    out: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in _IMG_EXT:
            out.append(p)
            if len(out) >= 5:
                break
    return out


@router.get("/status")
async def service_status(
    db: Session = Depends(get_db),
    _=Depends(get_require_permission("service_manage")),
):
    kv = _get_kv(db)
    api_key = kv.get("model_api_key", "")
    secret_key = kv.get("model_secret_key", "")
    model_url = (kv.get("model_api_url") or "").strip()

    token, oauth_ms, oauth_err = _oauth_get_token(api_key, secret_key)
    if not token:
        return {
            "online": False,
            "latency_ms": oauth_ms,
            "oauth_ms": oauth_ms,
            "message": oauth_err,
            "checked_at": time.time(),
            "probe": "oauth_failed",
        }

    if not model_url:
        return {
            "online": True,
            "latency_ms": oauth_ms,
            "oauth_ms": oauth_ms,
            "message": "鉴权成功，未配置模型接口地址（请在服务配置中填写 MODEL_API_URL）",
            "checked_at": time.time(),
            "probe": "oauth_only",
        }

    probes = _find_probe_images()
    if not probes:
        return {
            "online": True,
            "latency_ms": oauth_ms,
            "oauth_ms": oauth_ms,
            "message": "鉴权成功；未在 laji3 目录找到样本图，未调用分类接口",
            "checked_at": time.time(),
            "probe": "oauth_only_no_image",
        }

    img_path = probes[0]
    try:
        raw = img_path.read_bytes()
        base64_str = base64.b64encode(raw).decode("UTF8")
    except Exception as e:
        return {
            "online": True,
            "latency_ms": oauth_ms,
            "oauth_ms": oauth_ms,
            "message": f"鉴权成功；读取样本图失败：{e}",
            "checked_at": time.time(),
            "probe": "read_image_failed",
        }

    ok, cls_ms, err, _data = _easydl_classify_requests(model_url, token, base64_str, top_num=2)
    return {
        "online": ok,
        "latency_ms": cls_ms,
        "oauth_ms": oauth_ms,
        "message": err,
        "checked_at": time.time(),
        "probe": "easydl_classify",
        "sample_image": str(img_path.relative_to(Path(__file__).parent.parent)),
    }


@router.post("/classify")
async def service_classify(
    db: Session = Depends(get_db),
    _=Depends(get_require_permission("recognize_test")),
    file: UploadFile = File(...),
    top_num: int = Query(2, ge=1, le=20),
):
    kv = _get_kv(db)
    model_url = (kv.get("model_api_url") or "").strip()
    if not model_url:
        return {"error": "未配置模型接口地址 model_api_url"}

    token, _ms, err = _oauth_get_token(kv.get("model_api_key", ""), kv.get("model_secret_key", ""))
    if not token:
        return {"error": err or "鉴权失败"}

    raw = await file.read()
    base64_str = base64.b64encode(raw).decode("UTF8")
    ok, cls_ms, err2, data = _easydl_classify_requests(
        model_url,
        token,
        base64_str,
        top_num=max(1, min(top_num, 20)),
    )
    return {
        "ok": ok,
        "latency_ms": cls_ms,
        "error": err2,
        "result": data,
    }


@router.get("/config", response_model=ServiceConfigResponse)
async def get_service_config(
    db: Session = Depends(get_db),
    _=Depends(get_require_permission("service_manage")),
):
    kv = _get_kv(db)
    return ServiceConfigResponse(
        model_api_url=kv.get("model_api_url") or "",
        model_api_key=kv.get("model_api_key") or "",
        model_secret_key=kv.get("model_secret_key") or "",
    )


@router.put("/config", response_model=ServiceConfigResponse)
async def update_service_config(
    body: ServiceConfigUpdate,
    db: Session = Depends(get_db),
    _=Depends(get_require_permission("service_manage")),
):
    updates: Dict[str, Any] = body.model_dump(exclude_none=True)
    if not updates:
        kv = _get_kv(db)
        return ServiceConfigResponse(
            model_api_url=kv.get("model_api_url") or "",
            model_api_key=kv.get("model_api_key") or "",
            model_secret_key=kv.get("model_secret_key") or "",
        )
    _save_kv(db, updates)
    kv = _get_kv(db)
    return ServiceConfigResponse(
        model_api_url=kv.get("model_api_url") or "",
        model_api_key=kv.get("model_api_key") or "",
        model_secret_key=kv.get("model_secret_key") or "",
    )
