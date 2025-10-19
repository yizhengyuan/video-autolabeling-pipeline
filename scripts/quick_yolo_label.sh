#!/bin/bash

# YOLO 快速标注脚本

echo "🚀 YOLO11 快速自动标注"
echo "================================"
echo ""

# 激活虚拟环境
source .venv/bin/activate

# 检查是否提供视频文件
if [ -z "$1" ]; then
    echo "用法: ./quick_yolo_label.sh <视频文件路径> [模型大小]"
    echo ""
    echo "示例:"
    echo "  ./quick_yolo_label.sh data/videos/my_video.mp4"
    echo "  ./quick_yolo_label.sh data/videos/my_video.mp4 m  # 使用中等模型"
    echo ""
    echo "模型大小选项: n (最快), s (推荐), m (平衡), l (准确), x (最准确)"
    exit 1
fi

VIDEO_PATH="$1"
MODEL_SIZE="${2:-s}"  # 默认使用 small 模型

# 验证视频文件存在
if [ ! -f "$VIDEO_PATH" ]; then
    echo "❌ 错误: 找不到视频文件 $VIDEO_PATH"
    exit 1
fi

# 生成输出文件名
BASENAME=$(basename "$VIDEO_PATH" | sed 's/\.[^.]*$//')
OUTPUT_FILE="labels/${BASENAME}_yolo.json"

# 创建labels目录
mkdir -p labels

echo "📹 视频文件: $VIDEO_PATH"
echo "🤖 YOLO模型: yolo11${MODEL_SIZE}.pt"
echo "📁 输出文件: $OUTPUT_FILE"
echo ""
echo "开始处理..."
echo ""

# 运行YOLO标注
python yolo_auto_labeling.py "$VIDEO_PATH" \
    --model "yolo11${MODEL_SIZE}.pt" \
    --confidence 0.3 \
    --sample-rate 30 \
    --output "$OUTPUT_FILE"

echo ""
echo "================================"
echo "✅ 完成！"
echo ""
echo "📋 下一步："
echo "1. 在Label Studio项目中点击 'Import'"
echo "2. 上传文件: $OUTPUT_FILE"
echo "3. 选择 'Treat as predictions'"
echo "4. 开始审核和修正标注"
echo ""

