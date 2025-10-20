module.exports = {
  apps: [{
    name: "binance_alpha_be",
    script: "/home/ubuntu/binance_alpha_be/venv/bin/python",
    args: "-m uvicorn main:app --host 0.0.0.0 --port 8001",
    cwd: "/home/ubuntu/binance_alpha_be",
    env: {
      NODE_ENV: "production",
    },
    watch: false,
    instances: 1,
    exec_mode: "fork",
    autorestart: true,
    max_memory_restart: "500M"
  }]
}
