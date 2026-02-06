module.exports = {
  apps: [{
    name: 'demucs-web-service',
    script: 'app.py',
    interpreter: './venv/bin/python',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '2G',
    env: {
      FLASK_ENV: 'production',
      PYTHONUNBUFFERED: '1',
      VIRTUAL_ENV: '/Users/a1104/Documents/self/vocal_remove/demucs-web-service/venv',
      PATH: '/Users/a1104/Documents/self/vocal_remove/demucs-web-service/venv/bin:' + process.env.PATH
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true,
    cwd: '/Users/a1104/Documents/self/vocal_remove/demucs-web-service'
  }]
}
