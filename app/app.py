from flask import Flask, jsonify
import os

app = Flask(__name__

@app.route('/')
def home():
    # This is our health check endpoint
    # Intentionally breaking it for the Rollback Test
    return "I am broken!", 500

if __name__ == '__main__':
    # ECS Fargate requires the app to listen on 0.0.0.0
    app.run(host='0.0.0.0', port=3000)
