#!/bin/bash

# 批量处理前10个视频 - SR:5方案
# 估算费用：¥12（10个视频）
# 估算耗时：1-1.5小时

echo "======================================================================"
echo "🚀 批量处理前10个视频（SR:5无插值方案）"
echo "======================================================================"
echo ""
echo "⚙️  配置："
echo "  - 采样率：5（每5帧标注一次）"
echo "  - API：通义千问 Qwen VL Max"
echo "  - 视频数量：10个"
echo "  - 估算费用：¥12"
echo "  - 估算耗时：1-1.5小时"
echo ""
read -p "按Enter键开始处理，或Ctrl+C取消... " -r
echo ""

# 检查API Key
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo "❌ 错误：未设置 DASHSCOPE_API_KEY"
    echo "请运行：export DASHSCOPE_API_KEY='your-key-here'"
    exit 1
fi

# 激活虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，使用系统Python"
fi

# 创建输出目录
mkdir -p labels/batch_output
mkdir -p labels/batch_output/json

echo ""
echo "======================================================================"
echo "📹 开始处理视频..."
echo "======================================================================"
echo ""

# 视频目录
VIDEO_DIR="data/D1_video_clips"

# 统计信息
TOTAL=10
CURRENT=0
SUCCESS=0
FAILED=0

# 记录开始时间
START_TIME=$(date +%s)

# 处理前10个视频
count=0
for video in "$VIDEO_DIR"/*.mp4; do
    # 只处理前10个
    if [ $count -ge 10 ]; then
        break
    fi
    count=$((count + 1))
    CURRENT=$((CURRENT + 1))
    BASENAME=$(basename "$video" .mp4)
    OUTPUT_JSON="labels/batch_output/json/${BASENAME}_sr5.json"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[$CURRENT/$TOTAL] 处理: $BASENAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # 跳过已处理的文件
    if [ -f "$OUTPUT_JSON" ]; then
        echo "⏭️  跳过（已存在）: $OUTPUT_JSON"
        SUCCESS=$((SUCCESS + 1))
        echo ""
        continue
    fi
    
    # 运行标注
    python scripts/video_auto_labeling.py "$video" \
        --provider qwen \
        --sample-rate 5 \
        --output "$OUTPUT_JSON"
    
    # 检查是否成功
    if [ $? -eq 0 ] && [ -f "$OUTPUT_JSON" ]; then
        SUCCESS=$((SUCCESS + 1))
        echo "✅ 成功: $BASENAME"
        
        # 显示文件大小
        SIZE=$(ls -lh "$OUTPUT_JSON" | awk '{print $5}')
        echo "   文件: $OUTPUT_JSON ($SIZE)"
    else
        FAILED=$((FAILED + 1))
        echo "❌ 失败: $BASENAME"
    fi
    
    echo ""
    
    # 避免API限流，每个视频处理后等待1秒
    if [ $CURRENT -lt $TOTAL ]; then
        sleep 1
    fi
done

# 计算耗时
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "======================================================================"
echo "✅ 批量处理完成！"
echo "======================================================================"
echo ""
echo "📊 处理统计："
echo "  - 总数：$TOTAL 个视频"
echo "  - 成功：$SUCCESS 个"
echo "  - 失败：$FAILED 个"
echo "  - 耗时：${MINUTES}分${SECONDS}秒"
echo ""
echo "📁 输出文件："
echo "  - JSON标注：labels/batch_output/json/"
echo "  - 文件数量：$(ls -1 labels/batch_output/json/*.json 2>/dev/null | wc -l)"
echo ""
echo "💰 估算费用：约¥$((SUCCESS * 12 / 10))"
echo ""
echo "======================================================================"
echo "📋 下一步："
echo "======================================================================"
echo ""
echo "1️⃣  查看标注文件："
echo "   ls -lh labels/batch_output/json/"
echo ""
echo "2️⃣  导入到 Label Studio："
echo "   - 启动：bash scripts/start_label_studio.sh"
echo "   - 导入视频和JSON文件"
echo ""
echo "3️⃣  继续处理剩余视频（如果满意）："
echo "   - 修改脚本中的 head -10 为 tail -41"
echo "   - 或运行完整批处理脚本"
echo ""
echo "======================================================================"

