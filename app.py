from flask import Flask, request, render_template, send_file, jsonify, url_for
from werkzeug.utils import secure_filename
import os
import subprocess
import uuid
import shutil
from pathlib import Path
import threading
import time

app = Flask(__name__)
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

        tasks[task_id]['progress'] = 30
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            tasks[task_id]['status'] = 'completed'
            tasks[task_id]['progress'] = 100

            # 查找输出文件
            output_path = Path(output_dir) / 'htdemucs' / Path(input_file).stem
            if output_path.exists():
                vocals = output_path / 'vocals.mp3'
                no_vocals = output_path / 'no_vocals.mp3'

                tasks[task_id]['vocals'] = str(vocals) if vocals.exists() else None
                tasks[task_id]['no_vocals'] = str(no_vocals) if no_vocals.exists() else None
        else:
            tasks[task_id]['status'] = 'failed'
            tasks[task_id]['error'] = result.stderr

    except Exception as e:
        tasks[task_id]['status'] = 'failed'
        tasks[task_id]['error'] = str(e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 保存文件
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
    output_dir = os.path.join(app.config['OUTPUT_FOLDER'], task_id)
    os.makedirs(output_dir, exist_ok=True)

    file.save(input_path)

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


@app.route('/status/<task_id>')
def get_status(task_id):
    if task_id not in tasks:
        return jsonify({'error': '任务不存在'}), 404

    task = tasks[task_id].copy()

    # 如果完成，添加下载链接
    if task['status'] == 'completed':
        if task['vocals']:
            task['vocals_url'] = url_for('download_file', task_id=task_id, file_type='vocals')
        if task['no_vocals']:
            task['no_vocals_url'] = url_for('download_file', task_id=task_id, file_type='no_vocals')

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