#!/usr/bin/env python3
"""
YOLO11 本地自动标注脚本
完全免费，支持离线使用，速度快
"""

import cv2
import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import time

try:
    from ultralytics import YOLO
except ImportError:
    print("错误: 未安装 ultralytics 库")
    print("请运行: pip install ultralytics")
    exit(1)


# COCO数据集类别映射到中文（YOLO预训练模型使用COCO数据集）
COCO_TO_CHINESE = {
    "person": "行人",
    "bicycle": "自行车",
    "car": "汽车",
    "motorcycle": "摩托车",
    "bus": "公交车",
    "truck": "卡车",
    "traffic light": "交通信号灯",
    "stop sign": "停止标志",
    # 完整的COCO 80类
    "airplane": "飞机",
    "train": "火车",
    "boat": "船",
    "bird": "鸟",
    "cat": "猫",
    "dog": "狗",
    "horse": "马",
    "sheep": "羊",
    "cow": "牛",
    "elephant": "大象",
    "bear": "熊",
    "zebra": "斑马",
    "giraffe": "长颈鹿",
    "backpack": "背包",
    "umbrella": "雨伞",
    "handbag": "手提包",
    "tie": "领带",
    "suitcase": "行李箱",
    "frisbee": "飞盘",
    "skis": "滑雪板",
    "snowboard": "滑雪板",
    "sports ball": "运动球",
    "kite": "风筝",
    "baseball bat": "棒球棒",
    "baseball glove": "棒球手套",
    "skateboard": "滑板",
    "surfboard": "冲浪板",
    "tennis racket": "网球拍",
    "bottle": "瓶子",
    "wine glass": "酒杯",
    "cup": "杯子",
    "fork": "叉子",
    "knife": "刀",
    "spoon": "勺子",
    "bowl": "碗",
    "banana": "香蕉",
    "apple": "苹果",
    "sandwich": "三明治",
    "orange": "橙子",
    "broccoli": "西兰花",
    "carrot": "胡萝卜",
    "hot dog": "热狗",
    "pizza": "披萨",
    "donut": "甜甜圈",
    "cake": "蛋糕",
    "chair": "椅子",
    "couch": "沙发",
    "potted plant": "盆栽",
    "bed": "床",
    "dining table": "餐桌",
    "toilet": "马桶",
    "tv": "电视",
    "laptop": "笔记本电脑",
    "mouse": "鼠标",
    "remote": "遥控器",
    "keyboard": "键盘",
    "cell phone": "手机",
    "microwave": "微波炉",
    "oven": "烤箱",
    "toaster": "烤面包机",
    "sink": "水槽",
    "refrigerator": "冰箱",
    "book": "书",
    "clock": "时钟",
    "vase": "花瓶",
    "scissors": "剪刀",
    "teddy bear": "泰迪熊",
    "hair drier": "吹风机",
    "toothbrush": "牙刷",
}

# 交通场景相关类别（用于过滤）
TRAFFIC_CATEGORIES = {
    "person", "bicycle", "car", "motorcycle", "bus", "truck",
    "traffic light", "stop sign"
}


class YOLOVideoLabeler:
    """YOLO视频自动标注器"""
    
    def __init__(self, model_name: str = "yolo11n.pt", confidence: float = 0.25):
        """
        Args:
            model_name: YOLO模型名称
                - yolo11n.pt: 最快，准确度较低（推荐快速测试）
                - yolo11s.pt: 平衡
                - yolo11m.pt: 中等
                - yolo11l.pt: 大模型
                - yolo11x.pt: 最准确，最慢
            confidence: 置信度阈值（0-1）
        """
        self.model_name = model_name
        self.confidence = confidence
        
        print(f"加载YOLO模型: {model_name}")
        print("首次运行会自动下载模型，请稍候...")
        
        self.model = YOLO(model_name)
        print("✓ 模型加载成功！")
        
    def detect_video(
        self, 
        video_path: str, 
        sample_rate: int = 30,
        traffic_only: bool = True
    ) -> Tuple[List[Dict], Dict]:
        """
        检测视频中的目标
        
        Args:
            video_path: 视频文件路径
            sample_rate: 采样率（每N帧检测一次）
            traffic_only: 是否只检测交通相关目标
            
        Returns:
            (检测结果列表, 视频信息)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_info = {
            "fps": fps,
            "total_frames": total_frames,
            "width": width,
            "height": height,
            "duration": total_frames / fps
        }
        
        print(f"\n视频信息:")
        print(f"  分辨率: {width}x{height}")
        print(f"  帧率: {fps} fps")
        print(f"  总帧数: {total_frames}")
        print(f"  时长: {video_info['duration']:.2f} 秒")
        print(f"  采样率: 每 {sample_rate} 帧")
        print()
        
        frame_detections = []
        frame_count = 0
        detected_count = 0
        
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 按采样率检测
            if frame_count % sample_rate == 0:
                # 运行检测
                results = self.model(
                    frame, 
                    conf=self.confidence,
                    verbose=False  # 不显示每帧的详细信息
                )
                
                # 解析结果
                objects = []
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # 获取类别名称
                        cls_id = int(box.cls[0])
                        cls_name = result.names[cls_id]
                        
                        # 过滤非交通类别
                        if traffic_only and cls_name not in TRAFFIC_CATEGORIES:
                            continue
                        
                        # 获取边界框（xyxy格式）
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        # 转换为相对坐标（0-1范围）
                        bbox = [
                            x1 / width,
                            y1 / height,
                            x2 / width,
                            y2 / height
                        ]
                        
                        # 获取置信度
                        conf = float(box.conf[0])
                        
                        # 转换为中文类别
                        category_cn = COCO_TO_CHINESE.get(cls_name, cls_name)
                        
                        objects.append({
                            "category": category_cn,
                            "category_en": cls_name,
                            "bbox": bbox,
                            "confidence": conf,
                            "frame": frame_count,
                            "time": frame_count / fps
                        })
                
                frame_detections.append({
                    "frame": frame_count,
                    "objects": objects
                })
                
                detected_count += 1
                if detected_count % 10 == 0:
                    elapsed = time.time() - start_time
                    fps_processing = detected_count / elapsed
                    print(f"已处理 {detected_count} 帧 ({frame_count}/{total_frames}) "
                          f"- 速度: {fps_processing:.1f} 帧/秒")
            
            frame_count += 1
        
        cap.release()
        
        elapsed = time.time() - start_time
        print(f"\n✓ 检测完成!")
        print(f"  总耗时: {elapsed:.2f} 秒")
        print(f"  处理速度: {detected_count/elapsed:.1f} 帧/秒")
        print(f"  检测帧数: {detected_count}")
        
        # 统计检测到的目标
        total_objects = sum(len(fd["objects"]) for fd in frame_detections)
        print(f"  检测到目标总数: {total_objects}")
        
        return frame_detections, video_info
    
    def convert_to_label_studio(
        self, 
        video_path: str,
        detections: List[Dict],
        video_info: Dict
    ) -> Dict:
        """转换为Label Studio格式"""
        
        results = []
        
        for frame_data in detections:
            for obj in frame_data["objects"]:
                bbox = obj["bbox"]
                
                # Label Studio使用 x, y, width, height 格式（百分比）
                result = {
                    "value": {
                        "x": bbox[0] * 100,
                        "y": bbox[1] * 100,
                        "width": (bbox[2] - bbox[0]) * 100,
                        "height": (bbox[3] - bbox[1]) * 100,
                        "rotation": 0,
                        "rectanglelabels": [obj["category"]],
                        "frame": obj["frame"],
                        "time": obj["time"]
                    },
                    "from_name": "videoLabels",
                    "to_name": "video",
                    "type": "videorectangle",
                    "meta": {
                        "confidence": obj["confidence"]
                    }
                }
                results.append(result)
        
        return {
            "data": {
                "video": f"/data/local-files/?d={os.path.basename(video_path)}"
            },
            "predictions": [{
                "result": results,
                "score": 0.0,
                "model_version": self.model_name
            }]
        }


def main():
    parser = argparse.ArgumentParser(
        description="YOLO11 本地视频自动标注工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用默认模型（nano，最快）
  python yolo_auto_labeling.py video.mp4
  
  # 使用更大的模型（更准确）
  python yolo_auto_labeling.py video.mp4 --model yolo11m.pt
  
  # 调整采样率和置信度
  python yolo_auto_labeling.py video.mp4 --sample-rate 10 --confidence 0.4
  
  # 检测所有类别（不只是交通相关）
  python yolo_auto_labeling.py video.mp4 --all-categories
        """
    )
    
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument(
        "--model", 
        default="yolo11n.pt",
        choices=["yolo11n.pt", "yolo11s.pt", "yolo11m.pt", "yolo11l.pt", "yolo11x.pt"],
        help="YOLO模型大小 (n=最快, x=最准确)"
    )
    parser.add_argument(
        "--confidence", 
        type=float, 
        default=0.25,
        help="置信度阈值 (0-1, 默认0.25)"
    )
    parser.add_argument(
        "--sample-rate", 
        type=int, 
        default=30,
        help="采样率（每N帧检测一次，默认30）"
    )
    parser.add_argument(
        "--all-categories",
        action="store_true",
        help="检测所有类别（默认只检测交通相关类别）"
    )
    parser.add_argument(
        "--output", 
        default="yolo_labels.json",
        help="输出JSON文件路径"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("YOLO11 本地视频自动标注工具")
    print("=" * 60)
    print(f"视频文件: {args.video_path}")
    print(f"YOLO模型: {args.model}")
    print(f"置信度阈值: {args.confidence}")
    print(f"采样率: 每 {args.sample_rate} 帧")
    print(f"类别过滤: {'关闭（所有类别）' if args.all_categories else '开启（仅交通相关）'}")
    print("=" * 60)
    
    # 创建标注器
    labeler = YOLOVideoLabeler(
        model_name=args.model,
        confidence=args.confidence
    )
    
    # 检测视频
    detections, video_info = labeler.detect_video(
        args.video_path,
        sample_rate=args.sample_rate,
        traffic_only=not args.all_categories
    )
    
    # 转换为Label Studio格式
    print("\n转换为Label Studio格式...")
    label_studio_data = labeler.convert_to_label_studio(
        args.video_path,
        detections,
        video_info
    )
    
    # 保存结果
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([label_studio_data], f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 完成！标注结果已保存到: {args.output}")
    print(f"\n📋 导入Label Studio的步骤：")
    print(f"1. 在Label Studio项目中点击右上角 'Import'")
    print(f"2. 上传 {args.output} 文件")
    print(f"3. 选择 'Treat as predictions' (作为预标注)")
    print(f"4. 开始人工审核和修正！")
    
    # 显示检测统计
    print(f"\n📊 检测统计：")
    category_stats = {}
    for frame_data in detections:
        for obj in frame_data["objects"]:
            cat = obj["category"]
            category_stats[cat] = category_stats.get(cat, 0) + 1
    
    for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count} 个")


if __name__ == "__main__":
    main()
