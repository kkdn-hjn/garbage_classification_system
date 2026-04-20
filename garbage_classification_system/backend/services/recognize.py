import os
import tempfile
import cv2
import json
import numpy as np
# import tensorflow as tf
from pathlib import Path

# 默认使用的训练模型文件名（放在 backend/、backend/ml_models/ 或 backend/services/ 下）
DEFAULT_MODEL_FILE = "mobilenetv2_laji.h5"


def resolve_model_path(model_path: str) -> str:
    """
    将相对文件名解析为实际存在的 .h5 绝对路径。
    依次查找：绝对/相对当前工作目录、backend 根目录、backend/ml_models、backend/services。
    """
    p = Path(model_path)
    if p.is_file():
        return str(p.resolve())
    backend = Path(__file__).resolve().parent.parent
    for cand in (backend / model_path, backend / "ml_models" / model_path, backend / "services" / model_path):
        if cand.is_file():
            return str(cand.resolve())
    raise FileNotFoundError(
        f"未找到模型文件: {model_path}，请将 {DEFAULT_MODEL_FILE} 放在 backend、ml_models 或 services 目录下"
    )


# 分类目录定义
OUTPUT_DIR = "tu"
NON_RECYCLABLE_DIR = "non_recyclable"
RECYCLABLE_DIR = "recyclable"
HAZARDOUS_DIR = "hazardous"
OTHER_DIR = "other"


class GarbageClassifier:
    def __init__(self, model_path: str = DEFAULT_MODEL_FILE):
        resolved = resolve_model_path(model_path)
        self.model = tf.keras.models.load_model(resolved, compile=False)
        self._resolved_path = resolved

        classes_path = Path(resolved).with_suffix(Path(resolved).suffix + ".classes.json")
        if classes_path.exists():
            self.class_names = json.loads(classes_path.read_text(encoding="utf-8"))
        else:
            self.class_names = [
                "一次性杯子",
                "卫生纸",
                "口罩",
                "指甲油",
                "易拉罐",
                "杀虫剂",
                "果皮",
                "水果",
                "瓶子",
                "纸袋",
                "过期药物",
                "食物",
            ]

    def predict_image(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return "读取失败", 0.0, "未知"

        img = cv2.resize(img, (224, 224))
        outputs = self.model.predict(np.expand_dims(img, axis=0), verbose=0)
        result_index = np.argmax(outputs)
        confidence = float(np.max(outputs))
        class_name = self.class_names[result_index]

        if class_name in ["果皮", "水果", "食物"]:
            category = "厨余垃圾(湿垃圾)"
        elif class_name in ["瓶子", "纸袋", "易拉罐"]:
            category = "可回收物"
        elif class_name in ["杀虫剂", "过期药物", "指甲油"]:
            category = "有害垃圾"
        else:
            category = "其他垃圾"

        return class_name, confidence, category

    def predict_image_bytes(self, data: bytes):
        fd, path = tempfile.mkstemp(suffix=".jpg")
        try:
            os.write(fd, data)
            os.close(fd)
            return self.predict_image(path)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def predict_batch(self, image_paths):
        results = []
        for path in image_paths:
            class_name, conf, cat = self.predict_image(path)
            results.append(
                {
                    "path": path,
                    "class": class_name,
                    "confidence": round(conf * 100, 2),
                    "category": cat,
                }
            )
        return results

    def save_to_category(self, image_path):
        class_name, _, category = self.predict_image(image_path)
        filename = os.path.basename(image_path)
        img = cv2.imread(image_path)

        if category == "厨余垃圾(湿垃圾)":
            save_dir = os.path.join(OUTPUT_DIR, NON_RECYCLABLE_DIR)
        elif category == "可回收物":
            save_dir = os.path.join(OUTPUT_DIR, RECYCLABLE_DIR)
        elif category == "有害垃圾":
            save_dir = os.path.join(OUTPUT_DIR, HAZARDOUS_DIR)
        else:
            save_dir = os.path.join(OUTPUT_DIR, OTHER_DIR)

        os.makedirs(save_dir, exist_ok=True)
        cv2.imwrite(os.path.join(save_dir, filename), img)
        return f"已保存到：{save_dir}"


if __name__ == "__main__":
    classifier = GarbageClassifier(DEFAULT_MODEL_FILE)
    img_path = "test.jpg"
    class_name, confidence, category = classifier.predict_image(img_path)
    print("预测类别：", class_name, "置信度：", confidence, "大类：", category)
