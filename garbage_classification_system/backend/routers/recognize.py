"""在线图片识别：调百度 EasyDL。结果写入 recognize_logs。"""
import base64
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from core.security import get_require_permission
from models import User, RecognizeLog
from routers.service import _get_kv, _oauth_get_token, _easydl_classify_requests
from schemas import RecognizeLogListResponse, RecognizeStatsResponse
from services.train import GarbagePredictor

router = APIRouter(prefix="/api/recognize", tags=["在线识别"])

_predictor: Optional[GarbagePredictor] = None
_predictor_model_path: Optional[str] = None


def _find_default_h5() -> Optional[Path]:
    from services.recognize import DEFAULT_MODEL_FILE, resolve_model_path

    try:
        return Path(resolve_model_path(DEFAULT_MODEL_FILE))
    except FileNotFoundError:
        return None


def _get_local_predictor() -> Optional[GarbagePredictor]:
    global _predictor, _predictor_model_path
    path = _find_default_h5()
    if not path:
        return None
    p = str(path.resolve())
    if _predictor is not None and _predictor_model_path == p:
        return _predictor
    _predictor = GarbagePredictor(model_path=p)
    _predictor_model_path = p
    return _predictor


def _fill_log_fields_from_result(res: Any) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    从本地返回或 EasyDL 返回中取出细类 / 大类 / 置信度展示串。
    本地：class_name, category, confidence（百分比数字字符串）。
    EasyDL：{ log_id, results: [{ name, score }, ...] } → name、score、按细类映射大类。
    """
    if not isinstance(res, dict):
        return None, None, None

    if res.get("class_name") is not None:
        cn = str(res["class_name"])
        cat = res.get("category") or GarbagePredictor._category_for(cn)
        c = res.get("confidence")
        conf_str = str(c) if c is not None else None
        return cn, cat, conf_str

    results = res.get("results")
    if isinstance(results, list) and len(results) > 0:
        first = results[0]
        if isinstance(first, dict):
            name = first.get("name") or first.get("class_name")
            if name is None:
                return None, None, None
            cn = str(name)
            cat = GarbagePredictor._category_for(cn)
            score = first.get("score")
            if score is not None:
                try:
                    conf_str = f"{float(score):.6f}"
                except (TypeError, ValueError):
                    conf_str = str(score)
            else:
                conf_str = None
            return cn, cat, conf_str

    return None, None, None


def _safe_commit_log(db: Session, user: User, filename: str, started: float, response: Dict[str, Any]) -> None:
    try:
        latency_ms = int((time.perf_counter() - started) * 1000)
        ok = bool(response.get("ok"))
        src = str(response.get("source") or "none")
        err_parts = []
        if not ok:
            if response.get("error"):
                err_parts.append(str(response["error"]))
            if response.get("local_error"):
                err_parts.append(str(response["local_error"]))
        err_msg = "；".join(err_parts) if err_parts else None

        class_name = None
        category = None
        conf_str = None
        rj = None
        res = response.get("result")
        if ok and res is not None:
            if isinstance(res, dict):
                class_name, category, conf_str = _fill_log_fields_from_result(res)
                rj = json.dumps(res, ensure_ascii=False)[:16000]
            else:
                rj = json.dumps(res, ensure_ascii=False)[:16000]
        else:
            rj = json.dumps(response, ensure_ascii=False)[:8000]

        row = RecognizeLog(
            user_id=user.id,
            username=user.username,
            success=ok,
            latency_ms=latency_ms,
            source=src,
            filename=filename or "",
            class_name=class_name,
            category=category,
            confidence=conf_str,
            result_json=rj,
            error_message=err_msg,
        )
        db.add(row)
        db.commit()
    except Exception:
        db.rollback()


@router.post("/predict")
async def predict_image(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_require_permission("recognize_test")),
    file: UploadFile = File(...),
    top_num: int = Query(2, ge=1, le=20),
):
    """
    1. 优先使用 train.py 中 GarbagePredictor 加载 mobilenetv2_laji.h5。
    2. 若无模型或推理失败，再调用百度 EasyDL。
    3. 每次调用写入 recognize_logs（用于识别历史与 API 统计）。
    """
    raw = await file.read()
    filename = file.filename or ""
    started = time.perf_counter()
    local_err: Optional[str] = None

    if not raw:
        out = {"ok": False, "error": "空文件", "source": None}
        _safe_commit_log(db, current_user, filename, started, out)
        return out

    b64 = base64.b64encode(raw).decode("UTF8")
    kv = _get_kv(db)
    api_key = (kv.get("model_api_key") or "").strip()
    secret_key = (kv.get("model_secret_key") or "").strip()
    model_url = (kv.get("model_api_url") or "").strip()
    token, _oauth_ms, oauth_err = _oauth_get_token(api_key, secret_key)
    if not token:
        out = {
            "ok": False,
            "source": None,
            "error": oauth_err or "云端 OAuth 失败",
            "local_error": local_err,
        }
        _safe_commit_log(db, current_user, filename, started, out)
        return out

    ok, cls_ms, err2, data = _easydl_classify_requests(
        model_url,
        token,
        b64,
        top_num=max(1, min(top_num, 20)),
    )
    if ok and data is not None and not data.get("error_code"):
        out = {
            "ok": True,
            "source": "easydl",
            "latency_ms": cls_ms,
            "result": data,
            "local_error": local_err,
        }
        _safe_commit_log(db, current_user, filename, started, out)
        return out

    easydl_msg = err2 or (data.get("error_msg") if isinstance(data, dict) else None) or "EasyDL 未返回有效结果"
    out = {
        "ok": False,
        "source": None,
        "error": easydl_msg,
        "local_error": local_err,
    }
    _safe_commit_log(db, current_user, filename, started, out)
    return out


@router.get("/history", response_model=RecognizeLogListResponse)
def list_recognize_history(
    db: Session = Depends(get_db),
    _: User = Depends(get_require_permission("recognize_test")),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    total = db.query(func.count(RecognizeLog.id)).scalar() or 0
    rows = (
        db.query(RecognizeLog)
        .order_by(RecognizeLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return RecognizeLogListResponse(total=total, items=rows)


@router.get("/stats", response_model=RecognizeStatsResponse)
def recognize_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_require_permission("recognize_test")),
):
    from datetime import date, datetime, timedelta

    today = date.today()
    day_start = datetime.combine(today, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    q_day = db.query(RecognizeLog).filter(
        RecognizeLog.created_at >= day_start,
        RecognizeLog.created_at < day_end,
    )
    today_calls = q_day.count()
    today_ok = q_day.filter(RecognizeLog.success.is_(True)).count()
    today_failures = today_calls - today_ok
    rate = (today_ok / today_calls * 100.0) if today_calls else 0.0

    avg_raw = (
        db.query(func.avg(RecognizeLog.latency_ms))
        .filter(
            RecognizeLog.created_at >= day_start,
            RecognizeLog.created_at < day_end,
            RecognizeLog.success.is_(True),
            RecognizeLog.latency_ms.isnot(None),
        )
        .scalar()
    )
    avg_lat = float(avg_raw or 0.0)

    total_calls = db.query(func.count(RecognizeLog.id)).scalar() or 0

    return RecognizeStatsResponse(
        today_calls=today_calls,
        today_success_rate=round(rate, 2),
        today_avg_latency_ms=round(avg_lat, 1),
        today_failures=today_failures,
        total_calls=int(total_calls),
    )
