"""
百度图片爬取，采集图片保存到指定目录并写入 garbage_images 表。
"""
import re
import uuid
import requests
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session

HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}


def _fetch_image_urls(keyword: str, max_count: int = 200) -> List[str]:
    """从百度图片搜索获取图片 URL 列表"""
    url_base = f"http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word={keyword}&pn="
    all_urls = []
    offset = 0
    while len(all_urls) < max_count and offset < 1000:
        try:
            r = requests.get(url_base + str(offset), headers=HEADERS, timeout=10)
            r.encoding = "utf-8"
            urls = re.findall(r'"objURL":"(.*?)",', r.text, re.S)
            if not urls:
                break
            for u in urls:
                if u and u.startswith("http") and u not in all_urls:
                    all_urls.append(u)
                    if len(all_urls) >= max_count:
                        break
            offset += 60
        except Exception:
            offset += 60
            continue
    return all_urls[:max_count]


def collect_images(
    category: str,
    count: int,
    upload_dir: Path,
    db: Session,
    search_keyword: str = None,
) -> Tuple[int, int]:
    """
    采集指定分类的图片，保存到 upload_dir/{category}/ 并写入 garbage_images。

    Args:
        category: 分类名称（如 纸类、塑料），用于保存目录和 DB
        count: 采集数量
        upload_dir: 上传根目录（laji3）
        db: 数据库会话
        search_keyword: 百度图片搜索关键词，默认用 category。建议用垃圾类别的 description

    Returns:
        (成功数, 失败数)
    """
    from models import GarbageImage

    keyword = (search_keyword or "").strip() or category

    upload_dir = Path(upload_dir).resolve()
    category_dir = upload_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)

    urls = _fetch_image_urls(keyword, max_count=count * 2)  # 多取一些以应对失败
    ok, fail = 0, 0

    for i, pic_url in enumerate(urls):
        if ok >= count:
            break
        try:
            resp = requests.get(pic_url, headers=HEADERS, timeout=7)
            resp.raise_for_status()
            content = resp.content
            if len(content) < 1024:  # 太小可能是错误页
                fail += 1
                continue
            ext = ".jpg"
            uniq = uuid.uuid4().hex[:8]
            filename = f"{uniq}_{category}_{i}.jpg"
            filepath = category_dir / filename
            filepath.write_bytes(content)
            rel_path = f"{category}/{filename}"
            img = GarbageImage(filename=filename, filepath=rel_path, category=category)
            db.add(img)
            ok += 1
        except Exception:
            fail += 1
            continue

    return ok, fail


if __name__ == "__main__":
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from database import SessionLocal
    from config import settings

    keyword = input("请输入采集关键词（分类名）: ").strip() or "塑料"
    tm = int(input("请输入采集数量: ") or "10")
    upload_dir = Path(__file__).parent.parent / settings.upload_dir
    db = SessionLocal()
    try:
        ok, fail = collect_images(keyword, tm, upload_dir, db)
        db.commit()
        print(f"采集完成：成功 {ok} 张，失败 {fail} 张")
    finally:
        db.close()
