#!/bin/bash

# Label Studio 启动脚本
# 本脚本会自动创建虚拟环境、安装并启动 Label Studio

set -e  # 遇到错误时退出

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Label Studio 快速启动脚本${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}[1/4] 检查 Python 版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3，请先安装 Python 3.9 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ 找到 Python $PYTHON_VERSION${NC}"
echo ""

# 创建虚拟环境（如果不存在）
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}[2/4] 创建虚拟环境...${NC}"
    python3 -m venv $VENV_DIR
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
else
    echo -e "${YELLOW}[2/4] 虚拟环境已存在，跳过创建${NC}"
fi
echo ""

# 激活虚拟环境
echo -e "${YELLOW}[3/4] 激活虚拟环境...${NC}"
source $VENV_DIR/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

# 检查是否已安装 Label Studio
if ! python -c "import label_studio" &> /dev/null; then
    echo -e "${YELLOW}[4/4] 安装 Label Studio...${NC}"
    pip install --upgrade pip --quiet
    pip install label-studio
    echo -e "${GREEN}✓ Label Studio 安装成功${NC}"
else
    echo -e "${YELLOW}[4/4] Label Studio 已安装，检查更新...${NC}"
    pip install --upgrade label-studio --quiet
    echo -e "${GREEN}✓ Label Studio 已是最新版本${NC}"
fi
echo ""

# 启动 Label Studio
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}🚀 正在启动 Label Studio...${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""
echo -e "${GREEN}访问地址: ${NC}http://localhost:8080"
echo -e "${GREEN}按 Ctrl+C 停止服务${NC}"
echo ""

# 启动服务
label-studio start
