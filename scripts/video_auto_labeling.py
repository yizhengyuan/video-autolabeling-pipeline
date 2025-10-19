#!/usr/bin/env python3
"""
视频自动标注脚本 - 使用多模态大模型
支持 GPT-4V, Claude, Gemini 等多模态模型
"""

import cv2
import base64
import json
import os
from pathlib import Path
from typing import List, Dict
import argparse

# 配置区域
API_PROVIDERS = {
    "openai": {
        "model": "gpt-4o",  # 或 gpt-4-vision-preview
        "api_key_env": "OPENAI_API_KEY",
        "endpoint": "https://api.openai.com/v1/chat/completions"
    },
    "anthropic": {
        "model": "claude-3-5-sonnet-20241022",
        "api_key_env": "ANTHROPIC_API_KEY",
        "endpoint": "https://api.anthropic.com/v1/messages"
    },
    "gemini": {
        "model": "gemini-1.5-pro",
        "api_key_env": "GEMINI_API_KEY",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models"
    },
    "qwen": {
        "model": "qwen-vl-max",  # 或 qwen-vl-plus
        "api_key_env": "DASHSCOPE_API_KEY",
        "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    }
}

OBJECT_CATEGORIES = [
    "行人", "汽车", "摩托车", "自行车", 
    "交通标志", "交通信号灯", "施工区域", "其他"
]


class VideoFrameExtractor:
    """视频帧提取器"""
    
    def __init__(self, video_path: str, sample_rate: int = 30):
        """
        Args:
            video_path: 视频文件路径
            sample_rate: 采样率（每N帧提取一帧）
        """
        self.video_path = video_path
        self.sample_rate = sample_rate
        
    def extract_frames(self, output_dir: str) -> List[str]:
        """提取视频关键帧"""
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {self.video_path}")
        
        os.makedirs(output_dir, exist_ok=True)
        frame_paths = []
        frame_count = 0
        saved_count = 0
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息：FPS={fps}, 总帧数={total_frames}")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 按采样率保存帧
            if frame_count % self.sample_rate == 0:
                frame_path = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                saved_count += 1
                print(f"提取帧 {saved_count}: 原始帧号 {frame_count}")
            
            frame_count += 1
        
        cap.release()
        print(f"✓ 共提取 {saved_count} 帧")
        return frame_paths


class MultiModalLabeler:
    """多模态模型标注器"""
    
    def __init__(self, provider: str = "openai"):
        """
        Args:
            provider: API提供商 (openai, anthropic, gemini)
        """
        self.provider = provider
        self.config = API_PROVIDERS[provider]
        self.api_key = os.getenv(self.config["api_key_env"])
        
        if not self.api_key:
            raise ValueError(f"请设置环境变量: {self.config['api_key_env']}")
    
    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def create_prompt(self) -> str:
        """创建标注提示词"""
        categories = ", ".join(OBJECT_CATEGORIES)
        
        prompt = f"""请帮我分析这张摩托车第一人称视角的交通场景图片，检测并标注以下类别的目标：{categories}

重要提示：
- 这是摩托车骑手的第一人称视角
- 不要标注拍摄者自己骑的摩托车（画面底部可见的车把、仪表盘等）
- 只标注道路上的其他车辆、行人、交通标志等外部目标

对于每个检测到的目标，请提供：
1. 类别（从上述类别中选择）
2. 边界框坐标（格式：[x_min, y_min, x_max, y_max]，相对于图片尺寸的比例，范围0-1）
3. 置信度（0-1之间）

请以JSON格式返回结果，格式如下：
{{
  "objects": [
    {{
      "category": "行人",
      "bbox": [0.1, 0.2, 0.3, 0.5],
      "confidence": 0.95
    }}
  ]
}}

只返回JSON，不要其他解释。"""
        return prompt
    
    def label_image_openai(self, image_path: str) -> Dict:
        """使用OpenAI GPT-4V标注图片"""
        import requests
        
        base64_image = self.encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.config["model"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.create_prompt()},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        response = requests.post(
            self.config["endpoint"],
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            # 提取JSON部分
            try:
                # 移除可能的markdown代码块标记
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            except json.JSONDecodeError:
                print(f"JSON解析失败，原始响应: {content}")
                return {"objects": []}
        else:
            print(f"API请求失败: {response.status_code}, {response.text}")
            return {"objects": []}
    
    def label_image_anthropic(self, image_path: str) -> Dict:
        """使用Claude标注图片"""
        import requests
        import anthropic
        
        # 读取图片
        with open(image_path, "rb") as f:
            image_data = base64.standard_b64encode(f.read()).decode("utf-8")
        
        client = anthropic.Anthropic(api_key=self.api_key)
        
        message = client.messages.create(
            model=self.config["model"],
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": self.create_prompt()
                        }
                    ],
                }
            ],
        )
        
        content = message.content[0].text
        try:
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except json.JSONDecodeError:
            print(f"JSON解析失败，原始响应: {content}")
            return {"objects": []}
    
    def label_image_qwen(self, image_path: str) -> Dict:
        """使用Qwen VL标注图片"""
        import requests
        
        base64_image = self.encode_image(image_path)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.config["model"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": self.create_prompt()
                        }
                    ]
                }
            ],
            "max_tokens": 1000
        }
        
        response = requests.post(
            self.config["endpoint"],
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            # 提取JSON部分
            try:
                # 移除可能的markdown代码块标记
                content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(content)
            except json.JSONDecodeError:
                print(f"JSON解析失败，原始响应: {content}")
                return {"objects": []}
        else:
            print(f"API请求失败: {response.status_code}, {response.text}")
            return {"objects": []}
    
    def label_image(self, image_path: str) -> Dict:
        """标注单张图片"""
        if self.provider == "openai":
            return self.label_image_openai(image_path)
        elif self.provider == "anthropic":
            return self.label_image_anthropic(image_path)
        elif self.provider == "qwen":
            return self.label_image_qwen(image_path)
        else:
            raise NotImplementedError(f"暂不支持提供商: {self.provider}")


def convert_to_label_studio_format(
    video_path: str,
    frame_annotations: List[Dict],
    sample_rate: int,
    fps: float
) -> Dict:
    """转换为Label Studio导入格式"""
    
    results = []
    
    for idx, frame_data in enumerate(frame_annotations):
        frame_number = idx * sample_rate
        time_seconds = frame_number / fps
        
        for obj in frame_data.get("objects", []):
            # 转换bbox格式
            bbox = obj["bbox"]  # [x_min, y_min, x_max, y_max] 0-1范围
            
            result = {
                "value": {
                    "x": bbox[0] * 100,  # 转换为百分比
                    "y": bbox[1] * 100,
                    "width": (bbox[2] - bbox[0]) * 100,
                    "height": (bbox[3] - bbox[1]) * 100,
                    "rotation": 0,
                    "rectanglelabels": [obj["category"]],
                    "frame": frame_number,
                    "time": time_seconds
                },
                "from_name": "box",
                "to_name": "video",
                "type": "videorectangle"
            }
            results.append(result)
    
    return {
        "data": {
            "video": f"/data/local-files/?d={os.path.basename(video_path)}"
        },
        "predictions": [{
            "result": results,
            "score": 0.0
        }]
    }


def main():
    parser = argparse.ArgumentParser(description="视频自动标注工具")
    parser.add_argument("video_path", help="视频文件路径")
    parser.add_argument("--provider", default="openai", choices=["openai", "anthropic", "qwen"],
                        help="API提供商")
    parser.add_argument("--sample-rate", type=int, default=30,
                        help="采样率（每N帧提取一帧）")
    parser.add_argument("--output", default="auto_labels.json",
                        help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("视频自动标注工具")
    print("=" * 50)
    print(f"视频文件: {args.video_path}")
    print(f"API提供商: {args.provider}")
    print(f"采样率: 每 {args.sample_rate} 帧")
    print()
    
    # 1. 提取视频帧
    print("[1/3] 提取视频帧...")
    extractor = VideoFrameExtractor(args.video_path, args.sample_rate)
    frames_dir = "temp_frames"
    frame_paths = extractor.extract_frames(frames_dir)
    
    # 2. 使用多模态模型标注
    print("\n[2/3] 调用多模态模型标注...")
    labeler = MultiModalLabeler(provider=args.provider)
    
    frame_annotations = []
    for i, frame_path in enumerate(frame_paths):
        print(f"标注帧 {i+1}/{len(frame_paths)}: {frame_path}")
        annotation = labeler.label_image(frame_path)
        frame_annotations.append(annotation)
        print(f"  检测到 {len(annotation.get('objects', []))} 个目标")
    
    # 3. 转换为Label Studio格式
    print("\n[3/3] 转换为Label Studio格式...")
    cap = cv2.VideoCapture(args.video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    label_studio_data = convert_to_label_studio_format(
        args.video_path,
        frame_annotations,
        args.sample_rate,
        fps
    )
    
    # 保存结果
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump([label_studio_data], f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 完成！标注结果已保存到: {args.output}")
    print(f"\n导入方法：")
    print(f"1. 在Label Studio项目中点击 Import")
    print(f"2. 上传 {args.output} 文件")
    print(f"3. 选择 'Predictions' 导入模式")
    
    # 清理临时文件
    print(f"\n提示：临时帧文件保存在 {frames_dir}/，可以手动删除")


if __name__ == "__main__":
    main()

