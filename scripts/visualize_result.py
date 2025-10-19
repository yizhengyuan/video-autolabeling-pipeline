#!/usr/bin/env python3
"""
可视化标注结果 - 在图片上绘制边界框
"""

import cv2
import json
import sys

def visualize_annotations(video_path, json_path, output_path, frame_number=30):
    """
    从视频提取一帧并绘制标注框
    
    Args:
        video_path: 视频文件路径
        json_path: Label Studio JSON标注文件
        output_path: 输出图片路径
        frame_number: 要可视化的帧号
    """
    # 读取视频
    cap = cv2.VideoCapture(video_path)
    
    # 跳转到指定帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    
    if not ret:
        print(f"❌ 无法读取帧 {frame_number}")
        return
    
    height, width = frame.shape[:2]
    cap.release()
    
    # 读取标注
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    results = data[0]['predictions'][0]['result']
    
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
    
    # 筛选该帧的标注
    frame_results = [r for r in results if r['value']['frame'] == frame_number]
    
    print(f"📊 帧 {frame_number} 检测到 {len(frame_results)} 个目标")
    
    # 绘制边界框
    for i, result in enumerate(frame_results, 1):
        value = result['value']
        category = value['rectanglelabels'][0]
        
        # 从百分比转换为像素坐标
        x = int(value['x'] * width / 100)
        y = int(value['y'] * height / 100)
        w = int(value['width'] * width / 100)
        h = int(value['height'] * height / 100)
        
        # 获取颜色
        color = colors.get(category, (255, 255, 255))
        
        # 绘制矩形框（加粗）
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 3)
        
        # 绘制标签背景
        label = f"{category} #{i}"
        (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x, y - label_h - 15), (x + label_w + 10, y), color, -1)
        
        # 绘制文字
        cv2.putText(frame, label, (x + 5, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        print(f"  {i}. {category} - 位置: ({x}, {y}), 大小: ({w}x{h})")
    
    # 添加标题
    title = f"Frame {frame_number} - {len(frame_results)} objects detected"
    cv2.putText(frame, title, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    
    # 保存结果
    cv2.imwrite(output_path, frame)
    print(f"\n✅ 可视化结果已保存: {output_path}")
    print(f"   分辨率: {width}x{height}")


if __name__ == "__main__":
    video_path = "../data/D1_video_clips/D1_rand11-15_clip_000.mp4"
    json_path = "../labels/test_qwen_result.json"
    output_path = "../labels/visualization_frame30.jpg"
    
    print("🎨 创建可视化结果...")
    print(f"视频: {video_path}")
    print(f"标注: {json_path}")
    print()
    
    visualize_annotations(video_path, json_path, output_path, frame_number=30)
    
    # 也可视化其他帧
    print("\n" + "="*60)
    print("🎨 创建第二个可视化（帧180）...")
    print()
    visualize_annotations(video_path, json_path, "../labels/visualization_frame180.jpg", frame_number=180)

