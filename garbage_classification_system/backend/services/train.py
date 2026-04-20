import ssl
from typing import Optional

ssl._create_default_https_context = ssl._create_unverified_context
# import tensorflow as tf
# import matplotlib.pyplot as plt
import numpy as np
# from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import json
import os
import sys
import tempfile
import cv2
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
from services.recognize import resolve_model_path

# ====================== 1. 数据加载 ======================
def _count_images_in_dir(data_dir: str) -> int:
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
    p = Path(data_dir)
    if not p.exists():
        return 0
    count = 0
    for f in p.rglob("*"):
        if f.is_file() and f.suffix.lower() in exts:
            count += 1
    return count


def data_load(data_dir, img_height, img_width, batch_size):
    total_images = _count_images_in_dir(data_dir)
    if total_images == 0:
        raise ValueError(f"训练数据为空：目录 '{data_dir}' 下未找到图片。请确认 laji3/{'{类别}'}/ 下有图片文件。")

    # 数据太少时切分会导致训练/验证集为空，直接禁用验证集切分
    use_split = total_images >= max(10, batch_size * 2)

    if use_split:
        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            label_mode="categorical",
            validation_split=0.2,
            subset="training",
            seed=123,
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )
        val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            label_mode="categorical",
            validation_split=0.2,
            subset="validation",
            seed=123,
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )
    else:
        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            data_dir,
            label_mode="categorical",
            seed=123,
            image_size=(img_height, img_width),
            batch_size=batch_size,
        )
        val_ds = None

    class_names = train_ds.class_names

    # 2) 数据增强
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.2),
    ])

    train_ds = (
        train_ds
        .map(lambda x, y: (data_augmentation(x, training=True), y))
        .prefetch(buffer_size=tf.data.AUTOTUNE)
        .ignore_errors()
    )

    if val_ds is not None:
        val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE).ignore_errors()

    return train_ds, val_ds, class_names


# ====================== 2. 模型构建 ======================
def model_load(model_name='mobilenetv2', IMG_SHAPE=(224, 224, 3), dense_layers=1, dense_units=128,
               dense_activation='relu', num_classes: int = 12):
    if model_name == 'mobilenetv2':
        base_model = MobileNetV2(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
    elif model_name == 'resnet50':
        base_model = ResNet50(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
    elif model_name == 'efficientnetb0':
        base_model = EfficientNetB0(input_shape=IMG_SHAPE, include_top=False, weights='imagenet')
    else:
        raise ValueError('Invalid model name')

    base_model.trainable = False

    model = tf.keras.models.Sequential([
        tf.keras.layers.Rescaling(1. / 127.5, offset=-1, input_shape=IMG_SHAPE),
        base_model,
        tf.keras.layers.GlobalAveragePooling2D()
    ])

    for _ in range(dense_layers):
        model.add(tf.keras.layers.Dense(dense_units, activation=dense_activation))

    model.add(tf.keras.layers.Dense(num_classes, activation='softmax'))
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# ====================== 3. 训练 ======================
def _default_data_dir() -> str:
    """默认使用 backend/laji3 作为训练数据目录（采集/上传图片都会落到这里）。"""
    backend_dir = Path(__file__).parent.parent.resolve()
    return str((backend_dir / "laji3").resolve())


def _save_class_names(model_path: str, class_names: list[str]) -> str:
    """将类别顺序保存到模型旁边，推理时读取以保证一致性。"""
    p = Path(model_path)
    classes_path = p.with_suffix(p.suffix + ".classes.json")
    classes_path.write_text(json.dumps(class_names, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(classes_path)


def train(
    model_name='mobilenetv2',
    epochs=10,
    dense_layers=1,
    dense_units=256,
    dense_activation='relu',
    data_dir: Optional[str] = None,
    batch_size: int = 4,
):
    data_dir = data_dir or _default_data_dir()
    total_images = _count_images_in_dir(data_dir)
    if total_images == 0:
        raise ValueError(f"训练数据为空：目录 '{data_dir}' 下未找到图片。")
    batch_size = max(1, min(batch_size, total_images))

    train_ds, val_ds, class_names = data_load(data_dir, 224, 224, batch_size)
    model = model_load(
        model_name,
        dense_layers=dense_layers,
        dense_units=dense_units,
        dense_activation=dense_activation,
        num_classes=len(class_names),
    )
    # 不手动指定 steps_per_epoch / validation_steps，让 Keras 基于数据集自动推断
    if val_ds is None:
        history = model.fit(train_ds, epochs=epochs)
    else:
        history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)
    model_path = f"{model_name}_laji.h5"
    model.save(model_path)
    _save_class_names(model_path, class_names)
    return model, history, val_ds, class_names


# ====================== 4. 训练曲线绘图 ======================
def show_loss_acc(history, model_name="model"):
    # Keras 版本差异：有的叫 acc/val_acc，有的叫 accuracy/val_accuracy
    acc = history.history.get('accuracy', history.history.get('acc'))
    val_acc = history.history.get('val_accuracy', history.history.get('val_acc'))
    loss = history.history.get('loss')
    val_loss = history.history.get('val_loss')

    plt.figure(figsize=(8, 8))
    plt.subplot(2, 1, 1)
    plt.plot(acc, label=f'训练准确率')
    plt.plot(val_acc, label=f'验证准确率')
    plt.legend(loc='lower right')
    plt.ylabel('准确率')
    plt.title('准确率曲线')

    plt.subplot(2, 1, 2)
    if loss is not None:
        plt.plot(loss, label='训练损失')
    if val_loss is not None:
        plt.plot(val_loss, label='验证损失')
    plt.legend(loc='upper right')
    plt.ylabel('损失')
    plt.title('损失曲线')
    plt.xlabel('epoch')

    plt.savefig(f'{model_name}_curve.png')
    plt.show()


# ====================== 5. 计算所有指标：准确率、精确率、召回率、F1 ======================
def calculate_metrics(model, val_ds):
    y_true = []
    y_pred = []

    for x, y in val_ds:
        pred = model.predict(x, verbose=0)
        y_true.extend(np.argmax(y.numpy(), axis=1))
        y_pred.extend(np.argmax(pred, axis=1))

    acc = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')

    print("\n" + "=" * 50)
    print("【模型测试指标】")
    print(f"准确率 (Accuracy): {acc:.4f}")
    print(f"精确率 (Precision): {precision:.4f}")
    print(f"召回率 (Recall): {recall:.4f}")
    print(f"F1 分数 (F1 Score): {f1:.4f}")
    print("=" * 50 + "\n")

    return acc, precision, recall, f1


# ====================== 6. 预测方法（无界面） ======================
class GarbagePredictor:
    def __init__(self, model_path="mobilenetv2_laji.h5"):
        resolved = resolve_model_path(model_path)
        self.model = tf.keras.models.load_model(resolved, compile=False)
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

    @staticmethod
    def _category_for(class_name: str) -> str:
        if class_name in ["果皮", "水果", "食物"]:
            return "厨余垃圾"
        if class_name in ["瓶子", "纸袋", "易拉罐"]:
            return "可回收物"
        if class_name in ["杀虫剂", "过期药物", "指甲油"]:
            return "有害垃圾"
        return "其他垃圾"

    def _predict_array(self, img):
        img = cv2.resize(img, (224, 224))
        outputs = self.model.predict(np.expand_dims(img, axis=0), verbose=0)
        return np.asarray(outputs[0], dtype=np.float64)

    def predict_top(self, image_path: str, top_num: int = 1):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"图片读取失败：{image_path}（请检查路径是否存在）")
        probs = self._predict_array(img)
        n = max(1, min(int(top_num), len(probs)))
        order = np.argsort(probs)[-n:][::-1]
        out = []
        for idx in order:
            cn = self.class_names[int(idx)]
            out.append(
                {
                    "class_name": cn,
                    "confidence": float(probs[idx]),
                    "category": self._category_for(cn),
                }
            )
        return out

    def predict(self, image_path):
        top = self.predict_top(image_path, 1)
        r = top[0]
        return r["class_name"], r["confidence"], r["category"]

    def predict_bytes(self, data: bytes, top_num: int = 1):
        fd, path = tempfile.mkstemp(suffix=".jpg")
        try:
            os.write(fd, data)
            os.close(fd)
            return self.predict_top(path, top_num)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass


# ====================== 运行示例 ======================
if __name__ == '__main__':
    # --- 训练 + 计算指标 ---
    # model, history, val_ds, class_names = train(model_name='mobilenetv2', epochs=10)
    # show_loss_acc(history, "mobilenetv2")
    # calculate_metrics(model, val_ds)  # 自动计算所有指标

    # --- 预测 ---
    predictor = GarbagePredictor("mobilenetv2_laji.h5")
    # 默认测试图：优先从 backend/laji3 下随便找一张；找不到就跳过预测
    backend_dir = Path(__file__).parent.parent.resolve()
    laji3_dir = (backend_dir / "laji3").resolve()
    candidates = list(laji3_dir.rglob("*.jpg")) + list(laji3_dir.rglob("*.jpeg")) + list(laji3_dir.rglob("*.png"))
    if candidates:
        test_path = str(candidates[0])
        res, conf, cat = predictor.predict(test_path)
        print(f"测试图片：{test_path}")
        print(f"预测结果：{res}，置信度：{conf * 100:.2f}%，分类：{cat}")
    else:
        print(f"未找到测试图片，已跳过预测。请将图片放到：{laji3_dir} 或自行调用 predictor.predict(图片路径)")