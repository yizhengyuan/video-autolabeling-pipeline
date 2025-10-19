#!/usr/bin/env python3
"""
测试 Qwen API 配置是否正确
"""

import os
import sys
import requests
import base64

def test_qwen_api():
    """测试 Qwen VL API"""
    
    # 检查环境变量
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("❌ 错误：未设置环境变量 DASHSCOPE_API_KEY")
        print("\n请运行：")
        print('export DASHSCOPE_API_KEY="your-api-key-here"')
        return False
    
    print("✓ 检测到 API Key:", api_key[:20] + "...")
    
    # 创建一个简单的测试图片（1x1 红色像素）
    import tempfile
    from PIL import Image
    
    # 创建测试图片
    test_image = Image.new('RGB', (100, 100), color='red')
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    test_image.save(temp_file.name)
    
    # 读取并编码
    with open(temp_file.name, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    print("✓ 测试图片准备完成")
    
    # 调用 API
    print("\n正在测试 Qwen VL API...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "qwen-vl-max",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请描述这张图片。"
                    }
                ]
            }
        ],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            print("\n✅ API 调用成功！")
            print(f"\n模型响应: {content}")
            print("\n🎉 Qwen API 配置正确，可以开始使用了！")
            
            # 清理临时文件
            os.unlink(temp_file.name)
            return True
        else:
            print(f"\n❌ API 调用失败")
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            
            # 常见错误提示
            if response.status_code == 401:
                print("\n可能原因：")
                print("- API Key 错误或已过期")
                print("- 请检查 https://dashscope.console.aliyun.com/apiKey")
            elif response.status_code == 429:
                print("\n可能原因：")
                print("- 请求频率超限")
                print("- 账户余额不足")
            
            os.unlink(temp_file.name)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 网络请求失败: {e}")
        print("\n可能原因：")
        print("- 网络连接问题")
        print("- 防火墙/代理设置")
        os.unlink(temp_file.name)
        return False
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")
        os.unlink(temp_file.name)
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Qwen VL API 配置测试")
    print("=" * 60)
    print()
    
    # 检查是否安装了 PIL
    try:
        from PIL import Image
    except ImportError:
        print("❌ 缺少依赖：Pillow")
        print("\n请运行：")
        print("pip install Pillow")
        sys.exit(1)
    
    success = test_qwen_api()
    
    print("\n" + "=" * 60)
    
    if success:
        print("\n下一步：运行视频自动标注")
        print("python scripts/video_auto_labeling.py data/videos/your_video.mp4 --provider qwen")
        sys.exit(0)
    else:
        print("\n请修复上述问题后重试")
        sys.exit(1)

