# 日志系统说明

## 日志文件位置

应用已配置详细的日志记录系统，日志文件保存在 `logs/` 目录下：

- **`logs/app.log`** - 完整的应用日志（包括 INFO、WARNING、ERROR 级别）
- **`logs/error.log`** - 仅错误日志（ERROR 级别）

## 日志内容

### 记录的信息包括：

1. **文件上传日志**
   - 上传成功/失败
   - 文件名、任务ID、文件大小
   - 格式验证结果

2. **任务处理日志**
   - 任务开始/完成/失败
   - Demucs 命令执行详情
   - 命令返回码、标准输出、错误输出
   - 输出文件路径

3. **错误日志**
   - 异常堆栈信息
   - 失败原因详细说明
   - Demucs 错误信息

## 查看日志的方法

### 方法1：使用提供的脚本（推荐）

```bash
# 添加执行权限
chmod +x view_logs.sh

# 运行脚本
./view_logs.sh
```

脚本提供以下选项：
1. 查看完整应用日志
2. 查看错误日志
3. 实时监控应用日志
4. 实时监控错误日志
5. 查看最近50行应用日志
6. 查看最近50行错误日志
7. 搜索日志内容

### 方法2：直接使用命令行

```bash
# 查看完整应用日志
cat logs/app.log

# 查看错误日志
cat logs/error.log

# 查看最后50行
tail -n 50 logs/app.log

# 实时监控日志（按 Ctrl+C 退出）
tail -f logs/app.log

# 搜索特定任务的日志
grep "任务 <task_id>" logs/app.log

# 搜索错误信息
grep "ERROR" logs/app.log

# 搜索失败的任务
grep "处理失败" logs/app.log
```

### 方法3：使用 PM2 查看日志

如果使用 PM2 启动：

```bash
# 查看应用日志
pm2 logs demucs-api

# 查看错误日志
pm2 logs demucs-api --err

# 实时查看日志
pm2 logs demucs-api --lines 100
```

## 常见错误日志分析

### 错误1：Demucs 命令执行失败

```
[任务 xxx] 处理失败: 命令执行失败，返回码: 1
```

**可能原因：**
- Demucs 未正确安装
- 音频文件格式不支持或损坏
- 磁盘空间不足
- 系统资源不足（内存、CPU）

**排查步骤：**
1. 查看完整的 stderr 输出
2. 检查 Demucs 安装：`python3 -m demucs.separate --help`
3. 检查磁盘空间：`df -h`
4. 尝试手动处理文件

### 错误2：输出路径不存在

```
[任务 xxx] 输出路径不存在: outputs/xxx/htdemucs/...
```

**可能原因：**
- Demucs 处理过程中崩溃
- 文件权限问题
- 输出目录被误删

**排查步骤：**
1. 检查 Demucs 的完整输出
2. 检查 outputs 目录权限
3. 查看是否有磁盘写入错误

### 错误3：文件上传失败

```
文件上传异常: ...
```

**可能原因：**
- 文件过大（超过100MB限制）
- 磁盘空间不足
- 文件格式不支持
- 网络传输中断

**排查步骤：**
1. 检查文件大小
2. 检查支持的格式：mp3, wav, flac, m4a, ogg
3. 查看详细的异常堆栈

## 日志示例

### 成功处理的日志：

```
[2026-02-06 18:15:20] INFO: 文件上传成功 - 任务ID: abc123, 文件名: song.mp3, 大小: 5.23MB
[2026-02-06 18:15:21] INFO: [任务 abc123] 开始处理音频文件: uploads/abc123_song.mp3
[2026-02-06 18:15:21] INFO: [任务 abc123] 执行命令: python3 -m demucs.separate uploads/abc123_song.mp3 -o outputs/abc123 --mp3 --two-stems=vocals -d cpu
[2026-02-06 18:16:45] INFO: [任务 abc123] 命令返回码: 0
[2026-02-06 18:16:45] INFO: [任务 abc123] 查找输出路径: outputs/abc123/htdemucs/song
[2026-02-06 18:16:45] INFO: [任务 abc123] 处理完成 - 人声文件: outputs/abc123/htdemucs/song/vocals.mp3, 伴奏文件: outputs/abc123/htdemucs/song/no_vocals.mp3
```

### 失败处理的日志：

```
[2026-02-06 18:20:10] INFO: 文件上传成功 - 任务ID: def456, 文件名: bad.mp3, 大小: 2.10MB
[2026-02-06 18:20:11] INFO: [任务 def456] 开始处理音频文件: uploads/def456_bad.mp3
[2026-02-06 18:20:11] INFO: [任务 def456] 执行命令: python3 -m demucs.separate uploads/def456_bad.mp3 -o outputs/def456 --mp3 --two-stems=vocals -d cpu
[2026-02-06 18:20:12] INFO: [任务 def456] 命令返回码: 1
[2026-02-06 18:20:12] WARNING: [任务 def456] 标准错误:
Error: Invalid audio file format
[2026-02-06 18:20:12] ERROR: [任务 def456] 处理失败: Error: Invalid audio file format
```

## 日志文件管理

### 自动轮转

日志文件配置了自动轮转：
- 单个日志文件最大 10MB
- 保留最近 10 个备份文件
- 超过大小后自动创建新文件

### 手动清理

```bash
# 清理所有日志
rm -rf logs/*.log*

# 清理旧的备份日志
rm -rf logs/*.log.*

# 清空日志内容但保留文件
> logs/app.log
> logs/error.log
```

## 调试技巧

### 1. 追踪特定任务

```bash
# 提取某个任务的所有日志
grep "任务 abc123" logs/app.log
```

### 2. 统计错误类型

```bash
# 统计各类错误出现次数
grep "ERROR" logs/app.log | awk -F': ' '{print $NF}' | sort | uniq -c | sort -rn
```

### 3. 查看最近的错误

```bash
# 查看最近10个错误
grep "ERROR" logs/app.log | tail -n 10
```

### 4. 按时间范围筛选

```bash
# 查看特定日期的日志
grep "2026-02-06" logs/app.log

# 查看特定时间段的日志
grep "2026-02-06 18:" logs/app.log
```

## 集成到 PM2

在 [`ecosystem.config.js`](ecosystem.config.js) 中已配置 PM2 日志：

```javascript
error_file: './logs/pm2-error.log',
out_file: './logs/pm2-out.log',
log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
```

PM2 的日志包含：
- 应用的标准输出（console.log）
- 应用的标准错误（console.error）
- 进程重启信息

应用内部的日志系统（`logs/app.log`, `logs/error.log`）提供更详细的日志记录。
