#!/usr/bin/env python3
"""
图片自动标注脚本 - 使用多模态大模型
更快速的演示方案，适合快速测试
"""

import cv2
import base64
import json
import os
from pathlib import Path
import argparse

# 从视频标注脚本导入配置
from video_auto_labeling import (
    API_PROVIDERS,
    OBJECT_CATEGORIES,
    MultiModalLabeler
)


def visualize_labels(image_path: str, annotations: dict, output_path: str):
    """可视化标注结果"""
    img = cv2.imread(image_path)
    height, width = img.shape[:2]
    
    # 颜色映射
    colors = {
        "行人": (255, 112, 67),      # 橙色
        "汽车": (66, 165, 245),       # 蓝色
        "摩托车": (102, 187, 106),    # 绿色
        "自行车": (255, 193, 7),      # 黄色
        "交通标志": (156, 39, 176),   # 紫色
        "交通信号灯": (38, 198, 218), # 青色
        "施工区域": (255, 87, 34),    # 深橙色
        "其他": (158, 158, 158)       # 灰色
    }
    
    for obj in annotations.get("objects", []):
        category = obj["category"]
        bbox = obj["bbox"]  # [x_min, y_min, x_max, y_max] 0-1范围
        confidence = obj.get("confidence", 0)
        
        # 转换为像素坐标
        x1 = int(bbox[0] * width)
        y1 = int(bbox[1] * height)
        x2 = int(bbox[2] * width)
        y2 = int(bbox[3] * height)
        
        # 获取颜色
        color = colors.get(category, (255, 255, 255))
        
        # 绘制矩形框
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # 绘制标签背景
        label = f"{category} {confidence:.2f}"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
        
        # 绘制文字
        cv2.putText(img, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    # 保存结果
    cv2.imwrite(output_path, img)
    print(f"✓ 可视化结果已保存: {output_path}")


def convert_to_label_studio_format(image_path: str, annotations: dict) -> dict:
    """转换为 Label Studio 图片标注格式"""
    results = []
    
    for obj in annotations.get("objects", []):
        bbox = obj["bbox"]  # [x_min, y_min, x_max, y_max] 0-1范围
        
        result = {
            "value": {
                "x": bbox[0] * 100,  # 转换为百分比
                "y": bbox[1] * 100,
                "width": (bbox[2] - bbox[0]) * 100,
                "height": (bbox[3] - bbox[1]) * 100,
                "rotation": 0,
                "rectanglelabels": [obj["category"]]
            },
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels"
        }
        results.append(result)
    
    return {
        "data": {
            "image": f"/data/local-files/?d={os.path.basename(image_path)}"
        },
        "predictions": [{
            "result": results,
            "score": 0.0
        }]
    }


def main():
    parser = argparse.ArgumentParser(description="图片自动标注工具")
    parser.add_argument("image_path", help="图片文件路径")
    parser.add_argument("--provider", default="qwen", choices=["openai", "anthropic", "qwen"],
                        help="API提供商")
    parser.add_argument("--output", help="输出JSON文件路径（默认：图片名_labels.json）")
    parser.add_argument("--visualize", action="store_true", help="生成可视化结果图")
    
    args = parser.parse_args()
    
    # 检查图片文件
    if not os.path.exists(args.image_path):
        print(f"❌ 错误：图片文件不存在: {args.image_path}")
        return
    
    print("=" * 60)
    print("图片自动标注工具")
    print("=" * 60)
    print(f"图片文件: {args.image_path}")
    print(f"API提供商: {args.provider}")
    print()
    
    # 1. 使用多模态模型标注
    print("[1/3] 调用多模态模型分析图片...")
    labeler = MultiModalLabeler(provider=args.provider)
    
    try:
        annotations = labeler.label_image(args.image_path)
        object_count = len(annotations.get("objects", []))
        print(f"✓ 检测到 {object_count} 个目标")
        
        # 显示检测结果
        if object_count > 0:
            print("\n检测结果：")
            for i, obj in enumerate(annotations.get("objects", []), 1):
                print(f"  {i}. {obj['category']} (置信度: {obj.get('confidence', 0):.2f})")
        print()
        
    except Exception as e:
        print(f"❌ 标注失败: {e}")
        return
    
    # 2. 转换为 Label Studio 格式
    print("[2/3] 转换为 Label Studio 格式...")
    label_studio_data = convert_to_label_studio_format(args.image_path, annotations)
    
    # 确定输出文件名
    if args.output:
        output_json = args.output
    else:
        base_name = Path(args.image_path).stem
        output_json = f"{base_name}_labels.json"
    
    # 保存 JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump([label_studio_data], f, ensure_ascii=False, indent=2)
    
    print(f"✓ 标注文件已保存: {output_json}")
    print()
    
    # 3. 生成可视化（可选）
    if args.visualize:
        print("[3/3] 生成可视化结果...")
        base_name = Path(args.image_path).stem
        output_vis = f"{base_name}_labeled.jpg"
        visualize_labels(args.image_path, annotations, output_vis)
        print()
    
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print()
    print("生成的文件：")
    print(f"  - {output_json} (Label Studio 导入文件)")
    if args.visualize:
        print(f"  - {base_name}_labeled.jpg (可视化结果)")
    print()
    print("导入到 Label Studio：")
    print("  1. 启动 Label Studio: bash scripts/start_label_studio.sh")
    print("  2. 创建图片标注项目")
    print(f"  3. 先导入图片: {args.image_path}")
    print(f"  4. 再导入标注: {output_json} (选择 'Predictions')")
    print()


if __name__ == "__main__":
    main()

