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

### 一键启动（推荐）

启动脚本会自动处理所有环境配置：

```bash
# 1. 安装 PM2（首次）
npm install -g pm2

# 2. 一键启动
chmod +x start.sh
./start.sh
```

**自动处理功能**：
- ✓ 自动检测虚拟环境
- ✓ 不存在时自动创建虚拟环境
- ✓ 自动安装 requirements.txt 中的依赖
- ✓ 启动 PM2 服务

### 手动安装（可选）

如果需要手动控制虚拟环境创建：

```bash
# 1. 安装 PM2
npm install -g pm2

# 2. 创建虚拟环境
python3 -m venv venv

# 3. 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt
deactivate

# 4. 启动服务
./start.sh
# 或直接使用 PM2
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
1. **必须创建虚拟环境**：PM2 配置使用 `./venv/bin/python` 作为解释器
2. 确保虚拟环境中已安装所有依赖（`requirements.txt`）
3. 确保已安装 demucs 模块
4. 首次运行需要授予 start.sh 执行权限：`chmod +x start.sh`
5. 日志文件会随着时间增长，建议定期清理或配置日志轮转
6. 如果更新了依赖，需要在虚拟环境中重新安装后重启服务

## 虚拟环境说明
- PM2 会使用项目目录下的 `venv/bin/python` 作为 Python 解释器
- 环境变量 `VIRTUAL_ENV` 已在 PM2 配置中设置
- PATH 已配置为优先使用虚拟环境中的可执行文件
