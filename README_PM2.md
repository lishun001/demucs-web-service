# PM2 一键启动说明

## 文件说明

### 1. ecosystem.config.js
PM2 配置文件，包含以下配置：
- **应用名称**: demucs-web-service
- **解析器**: python3
- **实例数**: 1
- **自动重启**: 是
- **内存限制**: 2GB
- **日志路径**: ./logs/

### 2. start.sh
一键启动脚本，功能包括：
- 检查 PM2 是否安装
- 创建必要的目录（logs, uploads, outputs）
- 停止旧进程
- 启动新进程
- 保存 PM2 进程列表
- 显示常用命令提示

## 使用方法

### 安装 PM2（首次使用）
```bash
npm install -g pm2
```

### 启动服务
```bash
# 方法一：使用一键启动脚本（推荐）
chmod +x start.sh
./start.sh

# 方法二：直接使用 PM2
pm2 start ecosystem.config.js
```

### 常用命令
```bash
# 查看服务状态
pm2 status

# 查看实时日志
pm2 logs demucs-web-service

# 查看特定行数的日志
pm2 logs demucs-web-service --lines 100

# 停止服务
pm2 stop demucs-web-service

# 重启服务
pm2 restart demucs-web-service

# 删除服务
pm2 delete demucs-web-service

# 监控面板
pm2 monit

# 保存进程列表
pm2 save

# 设置开机自启（可选）
pm2 startup
pm2 save
```

## 访问服务
启动成功后，访问：http://localhost:7001

## 日志文件位置
- 错误日志: `./logs/err.log`
- 输出日志: `./logs/out.log`

## 注意事项
1. 确保已安装 Python 3 及相关依赖（requirements.txt）
2. 确保已安装 demucs 模块
3. 首次运行需要授予 start.sh 执行权限：`chmod +x start.sh`
4. 日志文件会随着时间增长，建议定期清理或配置日志轮转
