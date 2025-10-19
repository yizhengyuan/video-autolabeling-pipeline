# 🚀 Quickstart Guide

**Get AI auto-labeling running in 10 minutes!**

---

## 📋 Prerequisites

### Requirements

- **Python**: 3.9 or higher
- **OS**: macOS, Linux, or Windows
- **Network**: Required for AI API access (or use YOLO offline mode)

### Check Python Version

```bash
python3 --version
# Should show Python 3.9.x or higher
```

If Python is not installed:
- macOS: `brew install python3`
- Linux: `sudo apt-get install python3`
- Windows: Download from python.org

---

## 🚀 Step 1: Clone the Project

```bash
# Navigate to your desired directory
cd ~/Desktop

# Clone the repository
git clone https://github.com/yizhengyuan/video-autolabeling-pipeline.git

# Enter project directory
cd video-autolabeling-pipeline
```

---

## 📦 Step 2: Install Dependencies

### Option A: Basic Installation (Recommended for beginners)

```bash
pip3 install opencv-python requests Pillow anthropic
```

### Option B: Full Installation (Recommended)

```bash
# Install all dependencies including Label Studio
pip3 install -r requirements.txt
```

### Option C: Using Virtual Environment (Recommended for production)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Step 3: Get API Key

### Option 1: Qwen (Recommended for users in China, free quota available)

1. **Visit** https://dashscope.console.aliyun.com/apiKey
2. **Login** to Alibaba Cloud (register for free if needed)
3. **Create** API Key
4. **Copy** the generated key (format: `sk-xxxxxxxxxxxxx`)

### Option 2: Claude (Recommended for international users, best quality)

1. **Visit** https://console.anthropic.com/
2. **Register** for Anthropic account
3. **Get** API Key
4. **Copy** the key

### Option 3: Skip API Key (Use YOLO)

If you don't want to get an API key, skip to "Step 5" to use YOLO free plan.

---

## ⚙️ Step 4: Configure API Key

### Method A: Temporary Setup (For testing)

```bash
# For Qwen users
export DASHSCOPE_API_KEY="your-key-here"

# For Claude users
export ANTHROPIC_API_KEY="your-key-here"
```

> ⚠️ Note: Need to reset after closing terminal

### Method B: Permanent Setup (For daily use)

**macOS/Linux:**
```bash
# Edit config file
echo 'export DASHSCOPE_API_KEY="your-key-here"' >> ~/.zshrc
# or ~/.bashrc if using bash

# Reload config
source ~/.zshrc
```

**Windows:**
```cmd
# Add to system environment variables
setx DASHSCOPE_API_KEY "your-key-here"
```

---

## 🎯 Step 5: First Run

### Test 1: Image Auto-Labeling (Simplest, Recommended!)

```bash
# 1. Prepare a street scene image
# Use your phone to take a street photo and place it in the project directory

# 2. Run auto-labeling
python3 scripts/image_auto_labeling.py your-image.jpg --provider qwen --visualize

# Example:
python3 scripts/image_auto_labeling.py test.jpg --provider qwen --visualize
```

**Output:**
- `test_labeled.jpg` - Image with bounding boxes (open and view directly!)
- `test_labels.json` - Label Studio format annotation data

### Test 2: YOLO Offline Labeling (No API Key Required)

```bash
# Use YOLO for local labeling (completely free)
python3 scripts/yolo_auto_labeling.py your-image.jpg --visualize

# First run will auto-download YOLO model (~6MB)
```

### Test 3: Video Auto-Labeling

```bash
# 1. Prepare video file
mkdir -p data/videos
cp your-video.mp4 data/videos/

# 2. Run labeling (sample every 30 frames)
python3 scripts/video_auto_labeling.py data/videos/your-video.mp4 \
    --provider qwen \
    --sample-rate 30

# Output: your-video_labels.json
```

---

## 👀 Step 6: View Results

### Method A: View Image Directly (Most Intuitive)

If you used `--visualize` parameter:
```bash
# Open the labeled image
open test_labeled.jpg  # macOS
xdg-open test_labeled.jpg  # Linux
start test_labeled.jpg  # Windows
```

### Method B: Use Label Studio (Professional Tool)

```bash
# 1. Start Label Studio
bash scripts/start_label_studio.sh
# or: label-studio start

# 2. Open browser: http://localhost:8080

# 3. First time: create account (use any credentials)

# 4. Create project
#    - Click "Create Project"
#    - Select "Object Detection with Bounding Boxes"

# 5. Import images
#    - Settings → Cloud Storage → Add Source Folder
#    - or Import → Upload Files

# 6. Import labels
#    - Import → Upload Files
#    - Select generated *_labels.json file
#    - ⚠️ Important: Check "Treat as predictions"

# 7. Review and correct labels
#    - Click task to view AI-generated boxes
#    - Manually adjust inaccurate labels
```

---

## ✅ Verify Success

If you see the following, you've succeeded:

✅ **Image labeling success:**
```
✅ API call successful
✅ Detected X objects
✅ Labels saved: test_labels.json
✅ Visualization saved: test_labeled.jpg
```

✅ **Can see bounding boxes:**
- Opening `*_labeled.jpg` shows colored bounding boxes
- Boxes have category labels (e.g., "car", "person", etc.)

✅ **Label Studio working:**
- Browser opens http://localhost:8080
- Can see imported images and bounding boxes

---

## ❓ Common Issues

### Issue 1: Image Not Found

```bash
# Use absolute path
python3 scripts/image_auto_labeling.py /Users/username/Desktop/test.jpg --provider qwen
```

### Issue 2: API Key Error

```bash
# Check if set successfully
echo $DASHSCOPE_API_KEY
# Should show your key, empty means not set

# Reset
export DASHSCOPE_API_KEY="your-key-here"
```

### Issue 3: Missing Dependencies

```bash
# Install missing libraries
pip3 install opencv-python requests Pillow anthropic

# Or install all dependencies
pip3 install -r requirements.txt
```

### Issue 4: YOLO Model Download Slow

```bash
# YOLO model downloads automatically, if slow:
# 1. Use proxy
# 2. Or manually download to ~/.cache/huggingface/hub/
```

### Issue 5: Inaccurate Labels

**Solutions:**
```bash
# Solution 1: Use better model
python3 scripts/image_auto_labeling.py test.jpg --provider anthropic --visualize

# Solution 2: Adjust detection parameters (YOLO)
python3 scripts/yolo_auto_labeling.py test.jpg --confidence 0.25 --visualize

# Solution 3: Manually correct in Label Studio
```

---

## 🎓 Next Steps

### 1. Understand Different Options

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Qwen** | Fast in China, cheap | Medium accuracy | Daily use |
| **Claude** | Highest accuracy | Needs international network | High-quality labeling |
| **YOLO** | Free, offline | Only 80 categories | General object detection |

### 2. Read Detailed Docs

- **[快速开始.md](docs/快速开始.md)** - More usage scenarios (Chinese)
- **[QWEN_GUIDE.md](docs/QWEN_GUIDE.md)** - Qwen detailed tutorial
- **[YOLO_GUIDE.md](docs/YOLO_GUIDE.md)** - YOLO detailed tutorial

### 3. Batch Processing

```bash
# Batch label multiple images
for img in *.jpg; do
    python3 scripts/image_auto_labeling.py "$img" --provider qwen
done

# Batch label multiple videos
for video in data/videos/*.mp4; do
    python3 scripts/video_auto_labeling.py "$video" --provider qwen
done
```

---

## 💡 Tips

1. **First Time**: Start with images, see results before processing videos
2. **API Costs**: Qwen has free quota, enough for testing; for videos, increase sample rate (--sample-rate 60)
3. **Save Results**: Generated `*_labels.json` files are important, can be imported to Label Studio repeatedly
4. **Backup Data**: labels/ directory is configured not to commit to Git, remember to backup important results yourself

---

## 🎉 Congratulations!

You've learned how to use the AI auto-labeling tool!

**Recommended Workflow:**
1. Use AI to auto-generate initial labels (save 80% time)
2. Review and correct in Label Studio
3. Export training data

Questions? Submit an issue: https://github.com/yizhengyuan/video-autolabeling-pipeline/issues

