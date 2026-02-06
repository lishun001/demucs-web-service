#!/bin/bash

# PM2 一键启动脚本 for demucs-web-service

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Demucs Web Service PM2 启动脚本${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""

# 检查 PM2 是否安装
if ! command -v pm2 &> /dev/null; then
    echo -e "${RED}错误: PM2 未安装${NC}"
    echo -e "${YELLOW}请运行以下命令安装 PM2:${NC}"
    echo -e "  npm install -g pm2"
    exit 1
fi

# 检查 FFmpeg 是否安装
echo -e "${YELLOW}→ 检查 FFmpeg 是否安装...${NC}"
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}警告: FFmpeg 未安装${NC}"
    echo -e "${YELLOW}Demucs 需要 FFmpeg 来处理音频文件${NC}"
    
    # 检测操作系统并尝试自动安装
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS 系统
        if command -v brew &> /dev/null; then
            echo -e "${YELLOW}→ 检测到 Homebrew，正在安装 FFmpeg...${NC}"
            brew install ffmpeg
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ FFmpeg 安装成功${NC}"
            else
                echo -e "${RED}错误: FFmpeg 安装失败${NC}"
                echo -e "${YELLOW}请手动运行: brew install ffmpeg${NC}"
                exit 1
            fi
        else
            echo -e "${RED}错误: 未检测到 Homebrew${NC}"
            echo -e "${YELLOW}请先安装 Homebrew，或手动安装 FFmpeg${NC}"
            echo -e "  Homebrew 安装: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo -e "  然后运行: brew install ffmpeg"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux 系统
        if command -v apt-get &> /dev/null; then
            echo -e "${YELLOW}→ 检测到 apt，正在安装 FFmpeg...${NC}"
            sudo apt-get update && sudo apt-get install -y ffmpeg
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ FFmpeg 安装成功${NC}"
            else
                echo -e "${RED}错误: FFmpeg 安装失败${NC}"
                echo -e "${YELLOW}请手动运行: sudo apt-get install ffmpeg${NC}"
                exit 1
            fi
        elif command -v yum &> /dev/null; then
            echo -e "${YELLOW}→ 检测到 yum，正在安装 FFmpeg...${NC}"
            sudo yum install -y ffmpeg
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ FFmpeg 安装成功${NC}"
            else
                echo -e "${RED}错误: FFmpeg 安装失败${NC}"
                echo -e "${YELLOW}请手动运行: sudo yum install ffmpeg${NC}"
                exit 1
            fi
        else
            echo -e "${RED}错误: 无法识别的包管理器${NC}"
            echo -e "${YELLOW}请手动安装 FFmpeg${NC}"
            exit 1
        fi
    else
        echo -e "${RED}错误: 不支持的操作系统${NC}"
        echo -e "${YELLOW}请手动安装 FFmpeg${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ FFmpeg 已安装${NC}"
    # 显示 FFmpeg 版本
    ffmpeg -version | head -n 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}→ 虚拟环境不存在，正在创建...${NC}"
    
    # 创建虚拟环境
    python3.12 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 创建虚拟环境失败${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
    
    # 激活虚拟环境并安装依赖
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}→ 安装项目依赖...${NC}"
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}错误: 安装依赖失败${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✓ 依赖安装完成${NC}"
    else
        echo -e "${YELLOW}警告: 未找到 requirements.txt 文件${NC}"
    fi
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

# 检查虚拟环境中的 Python
if [ ! -f "venv/bin/python" ]; then
    echo -e "${RED}错误: 虚拟环境中未找到 Python${NC}"
    exit 1
fi

# 创建日志目录
echo -e "${YELLOW}→ 创建日志目录...${NC}"
mkdir -p logs

# 创建必要的目录
echo -e "${YELLOW}→ 创建必要的目录...${NC}"
mkdir -p uploads outputs

# 停止已存在的进程
echo -e "${YELLOW}→ 检查并停止已存在的进程...${NC}"
pm2 delete demucs-web-service 2>/dev/null || true

# 启动服务
echo -e "${YELLOW}→ 启动 Demucs Web Service...${NC}"
pm2 start ecosystem.config.js

# 保存 PM2 进程列表
echo -e "${YELLOW}→ 保存 PM2 进程列表...${NC}"
pm2 save

# 显示状态
echo ""
echo -e "${GREEN}✓ 启动完成!${NC}"
echo ""
pm2 status

echo ""
echo -e "${GREEN}常用命令:${NC}"
echo -e "  查看日志:   ${YELLOW}pm2 logs demucs-web-service${NC}"
echo -e "  查看状态:   ${YELLOW}pm2 status${NC}"
echo -e "  停止服务:   ${YELLOW}pm2 stop demucs-web-service${NC}"
echo -e "  重启服务:   ${YELLOW}pm2 restart demucs-web-service${NC}"
echo -e "  删除服务:   ${YELLOW}pm2 delete demucs-web-service${NC}"
echo -e "  监控面板:   ${YELLOW}pm2 monit${NC}"
echo ""
echo -e "${GREEN}服务访问地址: http://localhost:7001${NC}"
echo ""
