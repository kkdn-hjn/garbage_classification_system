import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np
from tensorflow.keras.applications import MobileNetV2, ResNet50, EfficientNetB0
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
import cv2


# ====================== 1. 数据加载 ======================
def data_load(data_dir, img_height, img_width, batch_size):
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        label_mode='categorical',
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )

    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        label_mode='categorical',
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size
    )

    class_names = train_ds.class_names

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal_and_vertical"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.2),
    ])

    train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))
    return train_ds, val_ds, class_names


# ====================== 2. 模型构建 ======================
def model_load(model_name='mobilenetv2', IMG_SHAPE=(224, 224, 3), dense_layers=1, dense_units=128,
               dense_activation='relu'):
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

    model.add(tf.keras.layers.Dense(18, activation='softmax'))
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
    model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# ====================== 3. 训练 ======================
def train(model_name='mobilenetv2', epochs=10, dense_layers=1, dense_units=256, dense_activation='relu'):
    train_ds, val_ds, class_names = data_load("D:\\laji\\laji2\\train", 224, 224, 4)
    model = model_load(model_name, dense_layers=dense_layers, dense_units=dense_units,
                       dense_activation=dense_activation)
    history = model.fit(train_ds, validation_data=val_ds, epochs=epochs)
    model.save(f"{model_name}_laji.h5")
    return model, history, val_ds, class_names


# ====================== 4. 训练曲线绘图 ======================
def show_loss_acc(history, model_name="model"):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    plt.figure(figsize=(8, 8))
    plt.subplot(2, 1, 1)
    plt.plot(acc, label=f'训练准确率')
    plt.plot(val_acc, label=f'验证准确率')
    plt.legend(loc='lower right')
    plt.ylabel('准确率')
    plt.title('准确率曲线')

    plt.subplot(2, 1, 2)
    plt.plot(loss, label=f'训练损失')
    plt.plot(val_loss, label=f'验证损失')
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
        self.model = tf.keras.models.load_model(model_path)
        self.class_names = [
            '一次性杯子', '卫生纸', '口罩', '指甲油',
            '易拉罐', '杀虫剂', '果皮', '水果',
            '瓶子', '纸袋', '过期药物', '食物'
        ]

    def predict(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.resize(img, (224, 224))
        outputs = self.model.predict(np.expand_dims(img, axis=0), verbose=0)
        index = np.argmax(outputs)
        class_name = self.class_names[index]
        confidence = float(np.max(outputs))

        if class_name in ['果皮', '水果', '食物']:
            category = "厨余垃圾"
        elif class_name in ['瓶子', '纸袋', '易拉罐']:
            category = "可回收物"
        elif class_name in ['杀虫剂', '过期药物', '指甲油']:
            category = "有害垃圾"
        else:
            category = "其他垃圾"

        return class_name, confidence, category


# ====================== 运行示例 ======================
if __name__ == '__main__':
    # --- 训练 + 计算指标 ---
    model, history, val_ds, class_names = train(model_name='mobilenetv2', epochs=10)
    show_loss_acc(history, "mobilenetv2")
    calculate_metrics(model, val_ds)  # 自动计算所有指标

    # --- 预测 ---
    predictor = GarbagePredictor("mobilenetv2_laji.h5")
    res, conf, cat = predictor.predict("test.jpg")
    print(f"预测结果：{res}，置信度：{conf * 100:.2f}%，分类：{cat}")