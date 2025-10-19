# 多模态大模型自动标注指南

本指南介绍如何使用多模态大模型（GPT-4V、Claude等）自动标注视频。

---

## 🚀 快速开始

### 第一步：安装依赖

```bash
# 创建虚拟环境（如果还没有）
python3 -m venv .venv
source .venv/bin/activate

# 安装必要的包
pip install opencv-python requests anthropic
```

### 第二步：配置API密钥

根据你选择的提供商，设置对应的环境变量：

#### 选项1：使用 OpenAI GPT-4V

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

#### 选项2：使用 Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

#### 选项3：使用 Google Gemini

```bash
export GEMINI_API_KEY="your-api-key-here"
```

#### 选项4：使用阿里云通义千问 Qwen（推荐国内用户）

```bash
export DASHSCOPE_API_KEY="sk-your-dashscope-api-key-here"
```

> 💡 **获取API密钥**：
> - OpenAI: https://platform.openai.com/api-keys
> - Anthropic: https://console.anthropic.com/
> - Google: https://makersuite.google.com/app/apikey
> - 通义千问: https://dashscope.console.aliyun.com/apiKey

### 第三步：运行自动标注

```bash
# 使用OpenAI GPT-4V
python scripts/video_auto_labeling.py data/videos/your_video.mp4 --provider openai

# 使用Anthropic Claude（推荐，效果好）
python scripts/video_auto_labeling.py data/videos/your_video.mp4 --provider anthropic

# 使用通义千问 Qwen（推荐国内用户，速度快）
python scripts/video_auto_labeling.py data/videos/your_video.mp4 --provider qwen

# 自定义采样率（每10帧标注一次）
python scripts/video_auto_labeling.py data/videos/your_video.mp4 --sample-rate 10
```

### 第四步：导入到Label Studio

1. 在Label Studio项目中点击右上角的 **"Import"**
2. 选择生成的 `auto_labels.json` 文件上传
3. 在导入选项中选择 **"Treat as predictions"**（作为预标注导入）
4. 点击导入

现在你可以在标注界面看到AI自动生成的标注框，你只需要：
- ✅ 检查和修正错误
- ✅ 补充遗漏的目标
- ✅ 调整不准确的边界框

---

## 📊 效果对比

| 方法 | 速度 | 准确度 | 成本 | 适用场景 |
|------|------|--------|------|---------|
| **GPT-4V** | 较慢（~3s/帧） | 高（85-90%） | 较高（$0.01/图） | 复杂场景 |
| **Claude 3.5 Sonnet** | 中等（~2s/帧） | 很高（90-95%） | 中等（$0.003/图） | 推荐海外用户 |
| **Qwen VL Max** | 快（~1-2s/帧） | 高（85-90%） | 低（¥0.02/图） | 推荐国内用户 ⭐ |
| **Gemini Pro** | 快（~1s/帧） | 中等（80-85%） | 低（$0.001/图） | 大批量处理 |

---

## 🛠️ 高级配置

### 调整采样率

采样率决定了每隔多少帧提取一帧进行标注：

```bash
# 每30帧标注一次（默认，适合25-30fps视频）
--sample-rate 30

# 每10帧标注一次（更密集，适合快速运动场景）
--sample-rate 10

# 每60帧标注一次（更稀疏，节省API费用）
--sample-rate 60
```

### 自定义标注类别

编辑 `scripts/video_auto_labeling.py` 中的 `OBJECT_CATEGORIES`：

```python
OBJECT_CATEGORIES = [
    "行人", "汽车", "摩托车", "自行车", 
    "交通标志", "交通信号灯", "施工区域", "其他"
]
```

### 批量处理多个视频

创建批处理脚本：

```bash
#!/bin/bash
# batch_label.sh

for video in data/videos/*.mp4; do
    echo "Processing: $video"
    python scripts/video_auto_labeling.py "$video" \
        --provider anthropic \
        --output "labels/$(basename $video .mp4).json"
done
```

---

## 💰 成本估算

假设你有一个30秒的视频（30fps，共900帧）：

### GPT-4V
- 采样率30 → 30帧 → 费用约 $0.30
- 采样率10 → 90帧 → 费用约 $0.90

### Claude 3.5 Sonnet（推荐海外用户）
- 采样率30 → 30帧 → 费用约 $0.09
- 采样率10 → 90帧 → 费用约 $0.27

### Qwen VL Max（推荐国内用户）
- 采样率30 → 30帧 → 费用约 ¥0.60（约 $0.08）
- 采样率10 → 90帧 → 费用约 ¥1.80（约 $0.24）

### Gemini Pro
- 采样率30 → 30帧 → 费用约 $0.03
- 采样率10 → 90帧 → 费用约 $0.09

---

## 🎯 最佳实践

### 1. 选择合适的采样率

- **快速运动场景**（如赛车、追逐）：采样率 10-15
- **正常交通场景**：采样率 25-30
- **静态或缓慢场景**：采样率 50-60

### 2. 混合工作流

```
1. AI自动标注 → 生成初始标注（节省80%时间）
2. 人工审核 → 修正错误和遗漏
3. 补充标注 → 添加属性和场景信息
```

### 3. 质量控制

- 先用少量帧测试效果
- 对比不同模型的结果
- 设置置信度阈值过滤低质量标注

---

## 🔧 故障排查

### 问题1：API密钥错误

```
ValueError: 请设置环境变量: OPENAI_API_KEY
```

**解决**：
```bash
# 检查环境变量
echo $OPENAI_API_KEY

# 如果为空，重新设置
export OPENAI_API_KEY="your-key"
```

### 问题2：依赖包缺失

```
ModuleNotFoundError: No module named 'cv2'
```

**解决**：
```bash
pip install opencv-python requests anthropic
```

### 问题3：JSON格式错误

模型返回的不是标准JSON格式。

**解决**：
- 使用Claude模型（格式更规范）
- 调整prompt提示词
- 检查脚本中的JSON解析部分

### 问题4：API限流

```
Rate limit exceeded
```

**解决**：
- 增加请求间隔（修改脚本添加 `time.sleep(1)`）
- 降低采样率
- 升级API账户额度

---

## 🆚 方案对比：AI自动标注 vs 纯手工标注

| 指标 | AI预标注 + 人工修正 | 纯手工标注 |
|------|-------------------|-----------|
| **时间** | 2-5分钟/视频 | 15-30分钟/视频 |
| **成本** | $0.1-0.5/视频 | 人工成本高 |
| **准确度** | 90-95% | 95-99% |
| **适用场景** | 大批量数据 | 少量高质量需求 |

**推荐**：使用AI预标注节省时间，人工审核保证质量。

---

## 📚 进阶：本地模型方案（免费）

如果你想完全免费，可以使用本地YOLO模型：

### 安装YOLOv8

```bash
pip install ultralytics
```

### 使用脚本（我可以帮你创建）

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')

# 对视频进行检测
results = model.track(source='video.mp4', save=True)
```

**优点**：
- ✅ 完全免费
- ✅ 速度快（GPU加速）
- ✅ 离线可用

**缺点**：
- ❌ 需要配置环境
- ❌ 类别受限于预训练模型
- ❌ 准确度可能低于大模型

---

## 🤝 需要帮助？

如果遇到问题或需要定制化方案，请告诉我：
- 你使用的模型提供商
- 遇到的具体错误信息
- 你的视频特点（帧率、时长、场景复杂度等）

我会帮你优化配置！

