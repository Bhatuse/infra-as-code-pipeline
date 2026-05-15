from flask import Flask, jsonify, render_template_string
import psutil
import os
import time

app = Flask(__name__)
START_TIME = time.time()

# HTML Template with Tailwind and Chart.js
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRE Dashboard | Pravin</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
    </style>
</head>
<body class="p-8">
    <div class="max-w-4xl mx-auto">
        <header class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                System Health Monitor
            </h1>
            <span class="px-4 py-1 rounded-full text-xs font-mono glass text-cyan-400 border-cyan-500/30">
                ENV: {{ env_name }}
            </span>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-slate-400 mb-4 uppercase tracking-wider text-sm font-semibold">CPU Usage</h3>
                <canvas id="cpuChart"></canvas>
            </div>
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-slate-400 mb-4 uppercase tracking-wider text-sm font-semibold">Memory (MB)</h3>
                <canvas id="memChart"></canvas>
            </div>
        </div>
    </div>

    <script>
        const createChart = (id, label, color) => new Chart(document.getElementById(id), {
            type: 'line',
            data: { labels: [], datasets: [{ label, borderColor: color, data: [], fill: true, backgroundColor: color + '22', tension: 0.4 }] },
            options: { scales: { y: { beginAtZero: true, grid: { color: '#334155' } }, x: { display: false } } }
        });

        const cpuChart = createChart('cpuChart', 'CPU %', '#22d3ee');
        const memChart = createChart('memChart', 'RAM MB', '#818cf8');

        async function updateStats() {
            const res = await fetch('/stats');
            const data = await res.json();
            
            [cpuChart, memChart].forEach((chart, i) => {
                const val = i === 0 ? data.cpu_usage_percent : data.memory_usage_mb;
                if (chart.data.labels.length > 20) chart.data.labels.shift(), chart.data.datasets[0].data.shift();
                chart.data.labels.push('');
                chart.data.datasets[0].data.push(val);
                chart.update();
            });
        }
        setInterval(updateStats, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML, env_name=os.getenv("ENV_NAME", "dev"))

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/stats')
def get_stats():
    return jsonify({
        "cpu_usage_percent": psutil.cpu_percent(),
        "memory_usage_mb": int(psutil.virtual_memory().used / (1024 * 1024))
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
