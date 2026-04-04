import os
import cv2
import numpy as np
import tensorflow as tf

# 分类目录定义
OUTPUT_DIR = 'tu'
NON_RECYCLABLE_DIR = 'non_recyclable'
RECYCLABLE_DIR = 'recyclable'
HAZARDOUS_DIR = 'hazardous'
OTHER_DIR = 'other'


class GarbageClassifier:
    def __init__(self, model_path="./mobilenetv2_laji.h5"):
        # 加载训练好的模型
        self.model = tf.keras.models.load_model(model_path)

        # 类别名称（必须和训练时一致）
        self.class_names = [
            '一次性杯子', '卫生纸', '口罩', '指甲油',
            '易拉罐', '杀虫剂', '果皮', '水果',
            '瓶子', '纸袋', '过期药物', '食物'
        ]

    # ====================== 【核心预测方法】 ======================
    # 输入：图片路径
    # 输出：预测类别名称 + 置信度 + 垃圾分类大类
    # ==============================================================
    def predict_image(self, image_path):
        """
        单张图片预测
        :param image_path: 图片路径
        :return: 预测类别, 置信度, 垃圾大类
        """
        # 1. 读取图片
        img = cv2.imread(image_path)
        if img is None:
            return "读取失败", 0.0, "未知"

        # 2. 预处理（和训练时一致：224x224）
        img = cv2.resize(img, (224, 224))

        # 3. 模型预测
        outputs = self.model.predict(np.expand_dims(img, axis=0), verbose=0)
        result_index = np.argmax(outputs)
        confidence = float(np.max(outputs))  # 置信度
        class_name = self.class_names[result_index]

        # 4. 判断属于哪一类垃圾
        if class_name in ['果皮', '水果', '食物']:
            category = "厨余垃圾(湿垃圾)"
        elif class_name in ['瓶子', '纸袋', '易拉罐']:
            category = "可回收物"
        elif class_name in ['杀虫剂', '过期药物', '指甲油']:
            category = "有害垃圾"
        else:
            category = "其他垃圾"

        return class_name, confidence, category

    # ====================== 批量预测 ======================
    def predict_batch(self, image_paths):
        results = []
        for path in image_paths:
            class_name, conf, cat = self.predict_image(path)
            results.append({
                "path": path,
                "class": class_name,
                "confidence": round(conf * 100, 2),  # 转为百分比
                "category": cat
            })
        return results

    # ====================== 保存到对应分类文件夹 ======================
    def save_to_category(self, image_path):
        class_name, _, category = self.predict_image(image_path)
        filename = os.path.basename(image_path)
        img = cv2.imread(image_path)

        # 创建目录
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


# ====================== 使用示例（直接运行） ======================
if __name__ == "__main__":
    # 初始化分类器
    classifier = GarbageClassifier(model_path="./mobilenetv2_laji.h5")

    # 预测单张图片
    img_path = "test.jpg"  # 把这里换成你的图片路径
    class_name, confidence, category = classifier.predict_image(img_path)

    # 输出结果（带指标）
    print("=" * 50)
    print("【垃圾分类预测结果】")
    print(f"预测类别：{class_name}")
    print(f"置信度：{confidence * 100:.2f}%")
    print(f"所属大类：{category}")
    print("=" * 50)

    # 保存图片
    classifier.save_to_category(img_path)