module.exports = {
  apps: [
    {
      name: 'secureredlab-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: '/home/user/webapp/SecureRedLab/frontend',
      env: {
        NODE_ENV: 'development',
        PORT: 5173
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
}
