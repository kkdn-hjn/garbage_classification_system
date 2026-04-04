#!/usr/bin/env python3
"""
扫描 laji1 目录下的图片，直接导入数据库（不复制，只记录引用）。
用法：python import_laji1.py [扫描目录，默认 laji1]
递归遍历所有子文件夹。路径中若包含分类名（纸类、塑料等），则使用该分类；否则归类为「其他」。
"""
import sys
from pathlib import Path
from typing import List, Tuple

# 确保能导入项目模块
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from database import SessionLocal
from models import GarbageImage, GarbageCategory, GARBAGE_CATEGORIES

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}

# filepath 前缀，用于区分 laji1 与 laji3
LAJI1_PREFIX = "laji1/"


def _get_categories(db: Session) -> List[str]:
    cats = db.query(GarbageCategory.name).order_by(GarbageCategory.sort_order).all()
    return [c[0] for c in cats] if cats else GARBAGE_CATEGORIES


def import_laji1(laji1_path: Path, db: Session) -> Tuple[int, int]:
    """递归扫描子目录，直接入库不复制，返回 (新增数, 跳过数)"""
    added, skipped = 0, 0
    valid_cats = _get_categories(db)

    def infer_category(rel_path: Path) -> str:
        """从路径中的文件夹名推断分类，优先取最深层匹配"""
        for part in reversed(rel_path.parts[:-1]):
            if part in valid_cats:
                return part
        return "其他" if "其他" in valid_cats else (valid_cats[0] if valid_cats else "其他")

    laji1_path = laji1_path.resolve()
    for fp in sorted(laji1_path.rglob("*")):
        if fp.is_file() and fp.suffix.lower() in IMG_EXT:
            try:
                rel = fp.relative_to(laji1_path)
            except ValueError:
                continue
            rel_str = str(rel).replace("\\", "/")
            filepath = LAJI1_PREFIX + rel_str
            existing = db.query(GarbageImage).filter(GarbageImage.filepath == filepath).first()
            if existing:
                skipped += 1
                continue
            category = infer_category(rel)
            db.add(GarbageImage(filename=fp.name, filepath=filepath, category=category))
            added += 1

    return added, skipped


def main():
    base = Path(__file__).parent
    if len(sys.argv) > 1:
        laji1_path = Path(sys.argv[1]).resolve()
    else:
        for cand in [base / "laji1", base.parent / "laji1"]:
            if cand.is_dir():
                laji1_path = cand
                break
        else:
            print("未找到 laji1 目录，请指定：python import_laji1.py /path/to/laji1")
            sys.exit(1)

    if not laji1_path.is_dir():
        print(f"目录不存在: {laji1_path}")
        sys.exit(1)

    print(f"扫描目录: {laji1_path}")
    db = SessionLocal()
    try:
        added, skipped = import_laji1(laji1_path, db)
        db.commit()
        print(f"已导入 {added} 张，跳过已存在 {skipped} 张")
    finally:
        db.close()


if __name__ == "__main__":
    main()
