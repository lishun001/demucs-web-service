#!/bin/bash

# 查看日志脚本

echo "=========================================="
echo "Demucs Web Service - 日志查看工具"
echo "=========================================="
echo ""

# 检查日志目录是否存在
if [ ! -d "logs" ]; then
    echo "❌ 日志目录不存在，请先运行应用生成日志"
    exit 1
fi

echo "请选择要查看的日志："
echo "1) 应用日志 (logs/app.log) - 查看所有日志"
echo "2) 错误日志 (logs/error.log) - 只查看错误"
echo "3) 实时监控应用日志 (tail -f)"
echo "4) 实时监控错误日志 (tail -f)"
echo "5) 查看最近50行应用日志"
echo "6) 查看最近50行错误日志"
echo "7) 搜索日志内容"
echo ""
read -p "请输入选项 (1-7): " choice

case $choice in
    1)
        if [ -f "logs/app.log" ]; then
            less +G logs/app.log
        else
            echo "❌ logs/app.log 文件不存在"
        fi
        ;;
    2)
        if [ -f "logs/error.log" ]; then
            less +G logs/error.log
        else
            echo "❌ logs/error.log 文件不存在"
        fi
        ;;
    3)
        if [ -f "logs/app.log" ]; then
            echo "正在实时监控应用日志 (按 Ctrl+C 退出)..."
            tail -f logs/app.log
        else
            echo "❌ logs/app.log 文件不存在"
        fi
        ;;
    4)
        if [ -f "logs/error.log" ]; then
            echo "正在实时监控错误日志 (按 Ctrl+C 退出)..."
            tail -f logs/error.log
        else
            echo "❌ logs/error.log 文件不存在"
        fi
        ;;
    5)
        if [ -f "logs/app.log" ]; then
            tail -n 50 logs/app.log
        else
            echo "❌ logs/app.log 文件不存在"
        fi
        ;;
    6)
        if [ -f "logs/error.log" ]; then
            tail -n 50 logs/error.log
        else
            echo "❌ logs/error.log 文件不存在"
        fi
        ;;
    7)
        read -p "请输入搜索关键词: " keyword
        echo ""
        echo "=== 应用日志搜索结果 ==="
        if [ -f "logs/app.log" ]; then
            grep -i "$keyword" logs/app.log --color=always | tail -n 100
        else
            echo "❌ logs/app.log 文件不存在"
        fi
        echo ""
        echo "=== 错误日志搜索结果 ==="
        if [ -f "logs/error.log" ]; then
            grep -i "$keyword" logs/error.log --color=always | tail -n 100
        else
            echo "❌ logs/error.log 文件不存在"
        fi
        ;;
    *)
        echo "❌ 无效的选项"
        exit 1
        ;;
esac
