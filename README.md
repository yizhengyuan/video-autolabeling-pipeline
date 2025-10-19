# MLLM Auto-Labeling for Images & Videos

**Leverage Multimodal Large Language Models (MLLMs) to automatically label your image and video datasets.**

Generate high-quality bounding box annotations using state-of-the-art vision-language models like GPT-4V, Claude 3.5 Sonnet, and Qwen-VL. Save 80%+ annotation time while maintaining 85-95% accuracy.

Integrate with Label Studio for human review and collaborative annotation workflows.

---

## 📁 Project Structure

```
video-autolabeling-pipeline/
├── README.md              # Main documentation
├── LICENSE                # Open source license
├── requirements.txt       # Python dependencies
├── docs/                  # 📚 Documentation
│   ├── 快速开始.md        # Quick start guide (Chinese)
│   ├── QWEN_GUIDE.md      # Qwen-VL detailed guide
│   ├── AUTO_LABELING_GUIDE.md  # VLM auto-labeling guide
│   └── YOLO_GUIDE.md      # YOLO local labeling guide
├── scripts/               # 🔧 Core scripts
│   ├── image_auto_labeling.py     # Image auto-labeling
│   ├── video_auto_labeling.py     # Video auto-labeling
│   ├── yolo_auto_labeling.py      # YOLO labeling
│   ├── quick_yolo_label.sh        # YOLO quick labeling script
│   ├── visualize_result.py        # Visualize labeling results
│   ├── test_qwen_api.py           # Test Qwen API
│   └── start_label_studio.sh      # Start Label Studio
├── templates/             # 📋 Labeling templates
├── data/                  # 📹 Data files (examples)
└── labels/                # 🏷️ Labeling results (output)
```

---

## 🎓 Getting Started

**First time user?** → Check **[QUICKSTART.md](QUICKSTART.md)** for complete tutorial (10 mins setup)

---

## 🚀 Quick Start

**Test with an image (fastest):**

```bash
# 1. Set API Key (choose one)
export DASHSCOPE_API_KEY="your-qwen-key"        # Qwen (recommended for China)
export ANTHROPIC_API_KEY="your-claude-key"     # Claude (recommended for international)

# 2. Label an image
python3 scripts/image_auto_labeling.py your-image.jpg --provider qwen --visualize

# View the labeled result with bounding boxes instantly!
```

> 💡 For detailed steps, see **[QUICKSTART.md](QUICKSTART.md)** or **[快速开始.md](docs/快速开始.md)** (Chinese)

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **MLLM Auto-Labeling** | Leverage GPT-4V, Claude 3.5 Sonnet, Qwen-VL to auto-generate labels |
| 📹 **Video Frame Labeling** | Smart sampling strategies for efficient video annotation |
| 🖼️ **Image Object Detection** | Single-shot bounding box generation for images |
| ⚡ **Save 80%+ Time** | AI generates initial labels, humans only review and refine |
| 🎯 **High Accuracy** | Claude: 90-95%, Qwen: 85-90%, YOLO: 80-85% |
| 🌐 **China-Friendly** | Qwen-VL support, no VPN required |
| 🔧 **Production Ready** | Label Studio integration, batch processing, visualization tools |

---

## 📚 Documentation

**For Beginners:**
- **[QUICKSTART.md](QUICKSTART.md)** 🔰 **Start Here** - Complete tutorial, 10-min setup
- **[快速开始.md](docs/快速开始.md)** ⭐ Quick Start - Three ways to get started (Chinese)

**Advanced Guides:**
- **[QWEN_GUIDE.md](docs/QWEN_GUIDE.md)** - Qwen-VL detailed guide (recommended for users in China)
- **[AUTO_LABELING_GUIDE.md](docs/AUTO_LABELING_GUIDE.md)** - VLM auto-labeling with GPT-4V, Claude, etc.
- **[YOLO_GUIDE.md](docs/YOLO_GUIDE.md)** - YOLO local labeling (free, offline)

---

## 🎯 Use Cases

- 🚗 **Autonomous Driving**: Vehicle, pedestrian, traffic sign detection
- 🏭 **Industrial QA**: Defect detection, product classification
- 🏥 **Medical Imaging**: Lesion annotation, organ segmentation
- 📦 **E-commerce**: Product recognition, shelf monitoring
- 🎥 **Video Analytics**: Action recognition, object tracking

---

## 💡 Contributing

We welcome Issues and Pull Requests! If you have questions or suggestions, please contact us on GitHub.

## 📄 License

This project is licensed under the [LICENSE](LICENSE) file.
