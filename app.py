from flask import Flask, request, render_template, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import shutil
from pathlib import Path
import threading
import time
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# 配置日志
if not os.path.exists('logs'):
    os.makedirs('logs')

# 设置日志格式
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# 文件处理器 - 保存所有日志
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

# 错误日志处理器 - 只保存错误日志
error_handler = RotatingFileHandler('logs/error.log', maxBytes=10240000, backupCount=10)
error_handler.setFormatter(formatter)
error_handler.setLevel(logging.ERROR)

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)

# 配置应用日志
app.logger.addHandler(file_handler)
app.logger.addHandler(error_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 限制100MB
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['ALLOWED_EXTENSIONS'] = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}

# 任务状态存储
tasks = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def process_audio(task_id, input_file, output_dir):
    """后台处理音频"""
    try:
        app.logger.info(f"[任务 {task_id}] 开始处理音频文件: {input_file}")
        tasks[task_id]['status'] = 'processing'
        tasks[task_id]['progress'] = 10

        # 运行 demucs
        cmd = [
            'python3', '-m', 'demucs.separate',
            input_file,
            '-o', output_dir,
            '--mp3',
            '--two-stems=vocals',
            '-d', 'cpu'
        ]

        app.logger.info(f"[任务 {task_id}] 执行命令: {' '.join(cmd)}")
        tasks[task_id]['progress'] = 30
        result = subprocess.run(cmd, capture_output=True, text=True)

        app.logger.info(f"[任务 {task_id}] 命令返回码: {result.returncode}")
        if result.stdout:
            app.logger.info(f"[任务 {task_id}] 标准输出:\n{result.stdout}")
        if result.stderr:
            app.logger.warning(f"[任务 {task_id}] 标准错误:\n{result.stderr}")

        if result.returncode == 0:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['progress'] = 100

            # 查找输出文件
            output_path = Path(output_dir) / 'htdemucs' / Path(input_file).stem
            app.logger.info(f"[任务 {task_id}] 查找输出路径: {output_path}")
            
            if output_path.exists():
                vocals = output_path / 'vocals.mp3'
                no_vocals = output_path / 'no_vocals.mp3'

                tasks[task_id]['vocals'] = str(vocals) if vocals.exists() else None
                tasks[task_id]['no_vocals'] = str(no_vocals) if no_vocals.exists() else None
                
                app.logger.info(f"[任务 {task_id}] 处理完成 - 人声文件: {tasks[task_id]['vocals']}, 伴奏文件: {tasks[task_id]['no_vocals']}")
            else:
                app.logger.error(f"[任务 {task_id}] 输出路径不存在: {output_path}")
        else:
            error_msg = result.stderr or f"命令执行失败，返回码: {result.returncode}"
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['error'] = error_msg
            app.logger.error(f"[任务 {task_id}] 处理失败: {error_msg}")

    except Exception as e:
        error_msg = str(e)
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = error_msg
        app.logger.exception(f"[任务 {task_id}] 处理异常: {error_msg}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            app.logger.warning("上传请求中没有文件")
            return jsonify({'error': '没有文件'}), 400

        file = request.files['file']
        if file.filename == '':
            app.logger.warning("上传的文件名为空")
            return jsonify({'error': '未选择文件'}), 400

        if not allowed_file(file.filename):
            app.logger.warning(f"不支持的文件格式: {file.filename}")
            return jsonify({'error': '不支持的文件格式'}), 400

        # 生成任务ID
        task_id = str(uuid.uuid4())

        # 保存文件
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], task_id)
        os.makedirs(output_dir, exist_ok=True)

        file.save(input_path)
        file_size = os.path.getsize(input_path)
        app.logger.info(f"文件上传成功 - 任务ID: {task_id}, 文件名: {filename}, 大小: {file_size/1024/1024:.2f}MB")

        # 初始化任务
        tasks[task_id] = {
            'status': 'queued',
            'progress': 0,
            'filename': filename,
            'vocals': None,
            'no_vocals': None
        }

        # 后台处理
        thread = threading.Thread(target=process_audio, args=(task_id, input_path, output_dir))
        thread.start()

        return jsonify({'task_id': task_id})
    
    except Exception as e:
        app.logger.exception(f"文件上传异常: {str(e)}")
        return jsonify({'error': f'上传失败: {str(e)}'}), 500


@app.route('/status/<task_id>')
def get_status(task_id):
    if task_id not in tasks:
        app.logger.warning(f"查询不存在的任务: {task_id}")
        return jsonify({'error': '任务不存在'}), 404

    task = tasks[task_id].copy()

    # 如果完成，添加下载链接
    if task['status'] == 'completed':
        if task['vocals']:
            task['vocals_url'] = url_for('download_file', task_id=task_id, file_type='vocals')
        if task['no_vocals']:
            task['no_vocals_url'] = url_for('download_file', task_id=task_id, file_type='no_vocals')
    elif task['status'] == 'failed':
        app.logger.error(f"[任务 {task_id}] 状态查询 - 任务失败: {task.get('error', '未知错误')}")

    return jsonify(task)


@app.route('/download/<task_id>/<file_type>')
def download_file(task_id, file_type):
    if task_id not in tasks:
        return '任务不存在', 404

    task = tasks[task_id]

    if file_type == 'vocals' and task['vocals']:
        return send_file(task['vocals'], as_attachment=True, download_name=f'vocals_{task["filename"]}')
    elif file_type == 'no_vocals' and task['no_vocals']:
        return send_file(task['no_vocals'], as_attachment=True, download_name=f'no_vocals_{task["filename"]}')

    return '文件不存在', 404


@app.route('/cleanup')
def cleanup():
    """清理超过24小时的文件"""
    current_time = time.time()
    cleaned = 0

    for task_id in list(tasks.keys()):
        # 这里可以添加时间检查逻辑
        # 简单示例：清理所有已完成的任务文件
        pass

    return jsonify({'cleaned': cleaned})


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=7001, debug=False)