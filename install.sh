#!/bin/bash

echo "=== 安装 Demucs Web 服务 ==="

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 安装完成 ==="
echo "运行方式："
echo "  开发环境: python app.py"
echo "  生产环境: gunicorn -w 4 -b 0.0.0.0:5000 app:app"