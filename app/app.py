from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Pravin's Capstone App is Live & Automated!",
        "environment": os.getenv("ENVIRONMENT", "development")
    })

if __name__ == '__main__':
    # ECS Fargate requires the app to listen on 0.0.0.0
    app.run(host='0.0.0.0', port=3000)
