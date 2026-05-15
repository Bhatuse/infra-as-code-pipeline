from flask import Flask, jsonify
import psutil
import os
import time
from datetime import datetime

app = Flask(__name__)

# Track when the app started for Uptime calculation
START_TIME = time.time()

@app.route('/')
def health_check():
    """Main health check endpoint for the ALB."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Pravin's SRE Dashboard is Online"
    }), 200

@app.route('/stats')
def get_stats():
    """Returns real-time system stats from inside the Fargate container."""
    uptime_seconds = int(time.time() - START_TIME)
    
    stats = {
        "environment": os.getenv("ENV_NAME", "development"),
        "uptime": f"{uptime_seconds} seconds",
        "cpu_usage_percent": psutil.cpu_percent(interval=None),
        "memory_usage_mb": int(psutil.virtual_memory().used / (1024 * 1024)),
        "container_metadata": {
            "os": os.name,
            "region": os.getenv("AWS_REGION", "ap-south-1")
        }
    }
    return jsonify(stats)

if __name__ == '__main__':
    # Using port 3000 as per your infra config
    app.run(host='0.0.0.0', port=3000)
