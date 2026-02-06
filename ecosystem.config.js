const path = require('path');

// 获取当前项目目录的绝对路径
const projectDir = __dirname;
const venvPath = path.join(projectDir, 'venv');
const venvBinPath = path.join(venvPath, 'bin');

module.exports = {
  apps: [{
    name: 'demucs-web-service',
    script: 'app.py',
    interpreter: path.join(venvBinPath, 'python'),
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '2G',
    env: {
      FLASK_ENV: 'production',
      PYTHONUNBUFFERED: '1',
      VIRTUAL_ENV: venvPath,
      PATH: venvBinPath + ':' + process.env.PATH
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    cwd: projectDir
  }]
}
