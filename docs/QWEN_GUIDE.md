# 通义千问 Qwen VL 自动标注指南

本指南详细介绍如何使用阿里云通义千问（Qwen）多模态大模型进行视频和图片的自动标注。

---

## 🌟 为什么选择 Qwen？

### 优势对比

| 特点 | Qwen VL Max | GPT-4V | Claude 3.5 |
|------|------------|--------|-----------|
| 🌐 **国内访问** | ✅ 无需翻墙，速度快 | ❌ 需要翻墙 | ❌ 需要翻墙 |
| 💰 **价格** | ¥0.02/图 | $0.01/图 | $0.003/图 |
| 🇨🇳 **中文理解** | ✅ 优秀 | 良好 | 良好 |
| ⚡ **响应速度** | 快（1-2s/帧） | 慢（3s/帧） | 中等（2s/帧） |
| 🎯 **准确度** | 85-90% | 85-90% | 90-95% |
| 🆓 **免费额度** | ✅ 新用户有免费试用 | ❌ 无 | ❌ 无 |

### 推荐场景

- ✅ 国内团队开发，需要稳定访问
- ✅ 大批量标注，看重成本效益
- ✅ 中文场景识别（如中文路标、中文文字）
- ✅ 快速原型开发和测试

---

## 🚀 快速开始

### 第一步：获取 API 密钥

1. 访问阿里云 DashScope 控制台：https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 进入「API-KEY 管理」页面
4. 点击「创建新的 API-KEY」
5. 复制生成的 API Key（格式：`sk-xxxxxxxxxxxxxxxx`）

> 💡 **新用户福利**：通常会赠送一定额度的免费调用次数

### 第二步：设置环境变量

```bash
# 在终端中设置（临时）
export DASHSCOPE_API_KEY="sk-your-dashscope-api-key-here"

# 或者添加到 ~/.zshrc 或 ~/.bashrc（永久）
echo 'export DASHSCOPE_API_KEY="sk-your-dashscope-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 第三步：安装依赖

```bash
# 确保已安装必要的包
pip install opencv-python requests
```

### 第四步：运行自动标注

```bash
# 对视频进行自动标注
python scripts/video_auto_labeling.py data/videos/your_video.mp4 --provider qwen

# 调整采样率（每15帧标注一次，适合中速场景）
python scripts/video_auto_labeling.py data/videos/your_video.mp4 --provider qwen --sample-rate 15

# 指定输出文件名
python scripts/video_auto_labeling.py data/videos/your_video.mp4 \
    --provider qwen \
    --output qwen_labels.json
```

---

## 🎛️ 模型选择

Qwen 提供多个视觉模型版本，你可以在脚本中修改模型配置：

### 可用模型

| 模型名称 | 适用场景 | 价格 | 性能 |
|---------|---------|------|------|
| `qwen-vl-max` | 高精度任务 | ¥0.02/图 | 最佳 |
| `qwen-vl-plus` | 平衡性能和成本 | ¥0.008/图 | 良好 |
| `qwen-vl-turbo` | 大批量快速处理 | ¥0.003/图 | 较快 |

### 修改模型配置

编辑 `scripts/video_auto_labeling.py`：

```python
"qwen": {
    "model": "qwen-vl-max",  # 改为 qwen-vl-plus 或 qwen-vl-turbo
    "api_key_env": "DASHSCOPE_API_KEY",
    "endpoint": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
}
```

---

## 💡 使用技巧

### 1. 优化采样率

根据视频内容选择合适的采样率：

```bash
# 快速运动场景（如赛车、追逐）
--sample-rate 10

# 正常交通场景
--sample-rate 25

# 静态或缓慢场景（如监控视频）
--sample-rate 60
```

### 2. 批量处理脚本

创建 `batch_qwen_label.sh`：

```bash
#!/bin/bash
# 批量处理多个视频

for video in data/videos/*.mp4; do
    echo "处理视频: $video"
    python scripts/video_auto_labeling.py "$video" \
        --provider qwen \
        --sample-rate 30 \
        --output "labels/$(basename $video .mp4)_qwen.json"
    
    # 避免频繁调用，休息1秒
    sleep 1
done

echo "✓ 批量处理完成！"
```

运行：
```bash
chmod +x batch_qwen_label.sh
./batch_qwen_label.sh
```

### 3. 自定义标注类别

编辑 `scripts/video_auto_labeling.py` 中的 `OBJECT_CATEGORIES`：

```python
# 交通场景
OBJECT_CATEGORIES = [
    "行人", "汽车", "摩托车", "自行车", 
    "交通标志", "交通信号灯", "施工区域", "其他"
]

# 或者改为工业场景
OBJECT_CATEGORIES = [
    "工人", "安全帽", "反光衣", "机械设备",
    "危险区域", "警告标志", "原材料", "其他"
]
```

---

## 🔧 故障排查

### 问题1：API Key 错误

```
ValueError: 请设置环境变量: DASHSCOPE_API_KEY
```

**解决方法**：
```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY

# 如果为空，重新设置
export DASHSCOPE_API_KEY="your-key-here"
```

### 问题2：API 调用失败

```
API请求失败: 401, {"error": "Invalid API key"}
```

**可能原因**：
- API Key 错误或过期
- API Key 权限不足
- 账户余额不足

**解决方法**：
- 检查 API Key 是否正确
- 登录控制台查看账户状态
- 充值或申请免费额度

### 问题3：请求限流

```
API请求失败: 429, {"error": "Rate limit exceeded"}
```

**解决方法**：
- 在脚本中添加延迟（修改代码添加 `time.sleep(1)`）
- 降低采样率
- 升级 API 套餐

### 问题4：JSON 解析失败

```
JSON解析失败，原始响应: ...
```

**原因**：模型有时返回格式不标准的 JSON

**解决方法**：
- 多尝试几次（大多数情况会成功）
- 调整 prompt 提示词使其更明确
- 联系技术支持反馈问题

---

## 💰 成本优化建议

### 1. 选择合适的模型

```bash
# 测试阶段使用 turbo（便宜）
--provider qwen  # 配置文件中改为 qwen-vl-turbo

# 生产环境使用 max（准确）
--provider qwen  # 配置文件中使用 qwen-vl-max
```

### 2. 智能采样

不是所有帧都需要标注：

```python
# 可以在脚本中添加关键帧检测
# 只对场景变化较大的帧进行标注
```

### 3. 分阶段标注

```bash
# 先用低采样率快速标注
python scripts/video_auto_labeling.py video.mp4 --provider qwen --sample-rate 60

# 对关键片段再用高采样率
python scripts/video_auto_labeling.py video_key_segment.mp4 --provider qwen --sample-rate 10
```

---

## 📊 效果示例

### 30秒视频（30fps，共900帧）成本对比

| 采样率 | 标注帧数 | Qwen VL Max | Qwen VL Plus | Qwen VL Turbo |
|--------|---------|-------------|--------------|---------------|
| 10 | 90帧 | ¥1.80 | ¥0.72 | ¥0.27 |
| 30 | 30帧 | ¥0.60 | ¥0.24 | ¥0.09 |
| 60 | 15帧 | ¥0.30 | ¥0.12 | ¥0.045 |

### 准确度参考

- **Qwen VL Max**: 85-90% 准确度
- **Qwen VL Plus**: 80-85% 准确度  
- **Qwen VL Turbo**: 75-80% 准确度

> 💡 建议：先用 Plus 或 Turbo 快速标注，关键项目再用 Max

---

## 🔗 相关资源

- **官方文档**: https://help.aliyun.com/zh/dashscope/
- **API 参考**: https://help.aliyun.com/zh/dashscope/developer-reference/api-details
- **价格说明**: https://help.aliyun.com/zh/dashscope/product-overview/billing-policy
- **控制台**: https://dashscope.console.aliyun.com/

---

## 🤝 需要帮助？

如果遇到问题，请提供以下信息：
- 使用的模型版本（max/plus/turbo）
- 错误信息完整输出
- 视频特征（帧率、时长、场景类型）
- 期望的标注效果

我会帮你优化配置！

---

## 🆚 与其他模型对比

### Qwen vs GPT-4V

**选 Qwen 的理由**：
- ✅ 国内访问稳定
- ✅ 中文场景理解好
- ✅ 价格更低（约为 GPT-4V 的 1/5）

**选 GPT-4V 的理由**：
- ✅ 复杂推理能力更强
- ✅ 全球场景泛化性好

### Qwen vs Claude

**选 Qwen 的理由**：
- ✅ 访问无障碍
- ✅ 响应速度更快
- ✅ 价格相近但体验更好

**选 Claude 的理由**：
- ✅ 准确度略高（90-95%）
- ✅ JSON 格式输出更稳定

---

## 📝 总结

Qwen VL 是国内团队做视频标注的**最佳选择**：

1. ⚡ **快** - 无需翻墙，响应迅速
2. 💰 **省** - 价格实惠，新用户有免费额度
3. 🎯 **准** - 85-90% 准确度，满足大多数场景
4. 🇨🇳 **稳** - 阿里云基础设施，服务稳定

赶快试试吧！

