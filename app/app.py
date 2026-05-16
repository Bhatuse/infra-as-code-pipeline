from flask import Flask, jsonify, render_template_string
import psutil
import os
import time
import platform

app = Flask(__name__)
START_TIME = time.time()

_last_net = psutil.net_io_counters()
_last_net_time = time.time()

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OPS / {{ hostname }}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --black: #000000;
    --white: #ffffff;
    --dim: rgba(255,255,255,0.35);
    --faint: rgba(255,255,255,0.07);
    --border: rgba(255,255,255,0.08);
    --border-hover: rgba(255,255,255,0.18);
    --mono: 'Space Mono', monospace;
    --sans: 'Syne', sans-serif;
  }

  html, body {
    height: 100%;
    background: var(--black);
    color: var(--white);
    font-family: var(--sans);
    font-size: 14px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }

  body {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    padding: 0;
    overflow-x: hidden;
  }

  /* ── TOP NAV ── */
  nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 40px;
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: rgba(0,0,0,0.85);
    backdrop-filter: blur(20px);
    z-index: 100;
  }

  .nav-brand {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .nav-logo {
    width: 28px;
    height: 28px;
    border: 1px solid var(--border-hover);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .nav-logo svg { width: 14px; height: 14px; }

  .nav-title {
    font-family: var(--mono);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }

  .nav-center {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--dim);
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--white);
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }

  .nav-right {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .env-badge {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 10px;
    border: 1px solid var(--border-hover);
    border-radius: 3px;
    color: var(--dim);
  }

  .uptime-val {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--dim);
  }

  /* ── MAIN ── */
  main {
    flex: 1;
    padding: 40px;
    max-width: 1400px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  /* ── SECTION LABEL ── */
  .section-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
  }

  /* ── METRIC CARDS ── */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }

  .metric-card {
    background: var(--black);
    padding: 28px 28px 24px;
    position: relative;
    transition: background 0.2s;
    cursor: default;
  }

  .metric-card:hover { background: var(--faint); }

  .metric-label {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .metric-icon {
    width: 18px;
    height: 18px;
    opacity: 0.3;
  }

  .metric-value {
    font-family: var(--mono);
    font-size: 42px;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
    transition: all 0.3s;
  }

  .metric-unit {
    font-size: 16px;
    font-weight: 400;
    opacity: 0.4;
    margin-left: 3px;
  }

  .metric-sub {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--dim);
    margin-bottom: 16px;
  }

  /* Mini sparkline bar */
  .metric-bar-track {
    width: 100%;
    height: 2px;
    background: var(--border);
    border-radius: 1px;
    overflow: hidden;
  }

  .metric-bar-fill {
    height: 100%;
    background: var(--white);
    border-radius: 1px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* ── CHARTS GRID ── */
  .charts-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }

  .chart-card {
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 28px;
    position: relative;
    transition: border-color 0.2s;
  }

  .chart-card:hover { border-color: var(--border-hover); }

  .chart-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 24px;
  }

  .chart-title {
    font-family: var(--mono);
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--dim);
  }

  .chart-live-val {
    font-family: var(--mono);
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--white);
    line-height: 1;
  }

  .chart-live-unit {
    font-size: 11px;
    opacity: 0.4;
    font-weight: 400;
    margin-left: 2px;
  }

  .chart-wrap {
    position: relative;
    height: 160px;
  }

  /* ── NETWORK SPLIT ── */
  .net-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 6px;
  }

  .net-half {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .net-dir {
    font-family: var(--mono);
    font-size: 9px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--dim);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .net-dir::before {
    content: '';
    display: inline-block;
    width: 12px;
    height: 1px;
    background: currentColor;
  }

  .net-val {
    font-family: var(--mono);
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .net-unit {
    font-size: 12px;
    opacity: 0.4;
    font-weight: 400;
  }

  .net-chart-wrap {
    height: 80px;
    margin-top: 16px;
  }

  /* ── DISK CARD ── */
  .disk-ring-wrap {
    display: flex;
    align-items: center;
    gap: 28px;
    margin-top: 8px;
  }

  .disk-canvas-wrap {
    position: relative;
    width: 140px;
    height: 140px;
    flex-shrink: 0;
  }

  .disk-center-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
  }

  .disk-pct {
    font-family: var(--mono);
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1;
  }

  .disk-pct-label {
    font-family: var(--mono);
    font-size: 9px;
    color: var(--dim);
    letter-spacing: 0.1em;
  }

  .disk-stats {
    display: flex;
    flex-direction: column;
    gap: 14px;
    flex: 1;
  }

  .disk-stat-row {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .disk-stat-label {
    font-family: var(--mono);
    font-size: 9px;
    color: var(--dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
  }

  .disk-stat-val {
    font-family: var(--mono);
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.01em;
  }

  .disk-stat-bar {
    height: 1px;
    background: var(--border);
    border-radius: 1px;
    overflow: hidden;
    margin-top: 4px;
  }

  .disk-stat-fill {
    height: 100%;
    background: var(--white);
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* ── FOOTER ── */
  footer {
    padding: 20px 40px;
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 10px;
    color: rgba(255,255,255,0.2);
    letter-spacing: 0.08em;
  }

  /* ── ANIMATIONS ── */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .metric-card, .chart-card {
    animation: fadeIn 0.4s ease both;
  }

  .metric-card:nth-child(1) { animation-delay: 0.05s; }
  .metric-card:nth-child(2) { animation-delay: 0.1s; }
  .metric-card:nth-child(3) { animation-delay: 0.15s; }
  .metric-card:nth-child(4) { animation-delay: 0.2s; }

  /* ── RESPONSIVE ── */
  @media (max-width: 900px) {
    main { padding: 20px; }
    nav { padding: 16px 20px; }
    .metrics-grid { grid-template-columns: 1fr 1fr; }
    .charts-grid { grid-template-columns: 1fr; }
    .metric-value { font-size: 32px; }
  }
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <div class="nav-brand">
    <div class="nav-logo">
      <svg viewBox="0 0 14 14" fill="none" stroke="white" stroke-width="1.5">
        <rect x="1" y="1" width="5" height="5" rx="1"/>
        <rect x="8" y="1" width="5" height="5" rx="1"/>
        <rect x="1" y="8" width="5" height="5" rx="1"/>
        <rect x="8" y="8" width="5" height="5" rx="1"/>
      </svg>
    </div>
    <span class="nav-title">OPS / MONITOR</span>
  </div>
  <div class="nav-center">
    <div class="status-dot"></div>
    <span>LIVE &mdash; {{ hostname }}</span>
  </div>
  <div class="nav-right">
    <span class="env-badge">{{ env_name }}</span>
    <span class="uptime-val" id="uptime-display">UP 00:00:00</span>
  </div>
</nav>

<!-- MAIN -->
<main>

  <!-- METRIC CARDS -->
  <div>
    <div class="section-label">System Metrics</div>
    <div class="metrics-grid">

      <!-- CPU -->
      <div class="metric-card">
        <div class="metric-label">
          CPU
          <svg class="metric-icon" viewBox="0 0 18 18" fill="none" stroke="white" stroke-width="1.3">
            <rect x="4" y="4" width="10" height="10" rx="1"/>
            <path d="M6 1v3M9 1v3M12 1v3M6 14v3M9 14v3M12 14v3M1 6h3M1 9h3M1 12h3M14 6h3M14 9h3M14 12h3"/>
          </svg>
        </div>
        <div class="metric-value" id="cpu-val">0<span class="metric-unit">%</span></div>
        <div class="metric-sub" id="cpu-cores">— cores</div>
        <div class="metric-bar-track"><div class="metric-bar-fill" id="cpu-bar" style="width:0%"></div></div>
      </div>

      <!-- MEMORY -->
      <div class="metric-card">
        <div class="metric-label">
          Memory
          <svg class="metric-icon" viewBox="0 0 18 18" fill="none" stroke="white" stroke-width="1.3">
            <rect x="1" y="5" width="16" height="8" rx="1"/>
            <path d="M4 5V3M7 5V3M10 5V3M13 5V3M4 13v2M7 13v2M10 13v2M13 13v2"/>
            <rect x="3" y="7" width="2" height="4" rx="0.5" fill="white" stroke="none"/>
            <rect x="7" y="7" width="2" height="4" rx="0.5" fill="white" stroke="none"/>
          </svg>
        </div>
        <div class="metric-value" id="mem-val">0<span class="metric-unit">%</span></div>
        <div class="metric-sub" id="mem-detail">— / — GB</div>
        <div class="metric-bar-track"><div class="metric-bar-fill" id="mem-bar" style="width:0%"></div></div>
      </div>

      <!-- DISK -->
      <div class="metric-card">
        <div class="metric-label">
          Disk
          <svg class="metric-icon" viewBox="0 0 18 18" fill="none" stroke="white" stroke-width="1.3">
            <ellipse cx="9" cy="13" rx="7" ry="3"/>
            <path d="M2 9c0-1.66 3.13-3 7-3s7 1.34 7 3"/>
            <path d="M2 5c0-1.66 3.13-3 7-3s7 1.34 7 3"/>
            <path d="M2 5v8M16 5v8"/>
          </svg>
        </div>
        <div class="metric-value" id="disk-val">0<span class="metric-unit">%</span></div>
        <div class="metric-sub" id="disk-detail">— / — GB</div>
        <div class="metric-bar-track"><div class="metric-bar-fill" id="disk-bar" style="width:0%"></div></div>
      </div>

      <!-- NETWORK -->
      <div class="metric-card">
        <div class="metric-label">
          Network
          <svg class="metric-icon" viewBox="0 0 18 18" fill="none" stroke="white" stroke-width="1.3">
            <circle cx="9" cy="9" r="7"/>
            <path d="M9 2c0 0-4 3-4 7s4 7 4 7"/>
            <path d="M9 2c0 0 4 3 4 7s-4 7-4 7"/>
            <path d="M2 9h14"/>
          </svg>
        </div>
        <div class="metric-value" id="net-total">0<span class="metric-unit">kb/s</span></div>
        <div class="metric-sub" id="net-detail">↑ 0 &nbsp; ↓ 0 kb/s</div>
        <div class="metric-bar-track"><div class="metric-bar-fill" id="net-bar" style="width:0%"></div></div>
      </div>

    </div>
  </div>

  <!-- CHARTS -->
  <div>
    <div class="section-label">History</div>
    <div class="charts-grid">

      <!-- CPU Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">CPU Usage</div>
          </div>
          <div>
            <span class="chart-live-val" id="cpu-chart-val">0</span>
            <span class="chart-live-unit">%</span>
          </div>
        </div>
        <div class="chart-wrap">
          <canvas id="cpuChart"></canvas>
        </div>
      </div>

      <!-- Memory Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Memory Usage</div>
          </div>
          <div>
            <span class="chart-live-val" id="mem-chart-val">0</span>
            <span class="chart-live-unit">%</span>
          </div>
        </div>
        <div class="chart-wrap">
          <canvas id="memChart"></canvas>
        </div>
      </div>

      <!-- Disk Donut -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Disk I/O</div>
          </div>
        </div>
        <div class="disk-ring-wrap">
          <div class="disk-canvas-wrap">
            <canvas id="diskChart" width="140" height="140"></canvas>
            <div class="disk-center-text">
              <div class="disk-pct" id="disk-ring-val">0%</div>
              <div class="disk-pct-label">USED</div>
            </div>
          </div>
          <div class="disk-stats">
            <div class="disk-stat-row">
              <div class="disk-stat-label">Used</div>
              <div class="disk-stat-val" id="disk-used-val">—</div>
              <div class="disk-stat-bar">
                <div class="disk-stat-fill" id="disk-used-fill" style="width:0%"></div>
              </div>
            </div>
            <div class="disk-stat-row">
              <div class="disk-stat-label">Free</div>
              <div class="disk-stat-val" id="disk-free-val">—</div>
              <div class="disk-stat-bar">
                <div class="disk-stat-fill" id="disk-free-fill" style="width:100%"></div>
              </div>
            </div>
            <div class="disk-stat-row">
              <div class="disk-stat-label">Total</div>
              <div class="disk-stat-val" id="disk-total-val">—</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Network Chart -->
      <div class="chart-card">
        <div class="chart-header">
          <div>
            <div class="chart-title">Network I/O</div>
          </div>
        </div>
        <div class="net-row">
          <div class="net-half">
            <div class="net-dir">Outbound</div>
            <div><span class="net-val" id="net-sent-val">0</span> <span class="net-unit">kb/s</span></div>
          </div>
          <div class="net-half">
            <div class="net-dir">Inbound</div>
            <div><span class="net-val" id="net-recv-val">0</span> <span class="net-unit">kb/s</span></div>
          </div>
        </div>
        <div class="net-chart-wrap">
          <canvas id="netChart"></canvas>
        </div>
      </div>

    </div>
  </div>

</main>

<footer>
  <span>SRE OPERATIONS DASHBOARD</span>
  <span id="ts-display">—</span>
  <span>REFRESH INTERVAL 2s</span>
</footer>

<script>
  // ── Chart defaults ──────────────────────────────────────
  const CHART_OPTS = (label, color='rgba(255,255,255,0.9)') => ({
    type: 'line',
    data: {
      labels: Array(40).fill(''),
      datasets: [{
        label,
        data: Array(40).fill(null),
        borderColor: color,
        borderWidth: 1.5,
        pointRadius: 0,
        fill: true,
        backgroundColor: (ctx) => {
          const g = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height);
          g.addColorStop(0, 'rgba(255,255,255,0.08)');
          g.addColorStop(1, 'rgba(255,255,255,0)');
          return g;
        },
        tension: 0.4,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: {
          min: 0, max: 100,
          display: true,
          grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
          ticks: {
            color: 'rgba(255,255,255,0.25)',
            font: { family: "'Space Mono', monospace", size: 9 },
            maxTicksLimit: 4,
            callback: v => v + '%'
          },
          border: { display: false }
        }
      }
    }
  });

  const cpuChart = new Chart(document.getElementById('cpuChart'), CHART_OPTS('CPU'));
  const memChart = new Chart(document.getElementById('memChart'), CHART_OPTS('MEM'));

  // Network chart — dual dataset
  const netChart = new Chart(document.getElementById('netChart'), {
    type: 'line',
    data: {
      labels: Array(40).fill(''),
      datasets: [
        {
          label: 'Sent',
          data: Array(40).fill(null),
          borderColor: 'rgba(255,255,255,0.9)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.4,
        },
        {
          label: 'Recv',
          data: Array(40).fill(null),
          borderColor: 'rgba(255,255,255,0.35)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false,
          tension: 0.4,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: {
          min: 0,
          display: true,
          grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
          ticks: {
            color: 'rgba(255,255,255,0.25)',
            font: { family: "'Space Mono', monospace", size: 9 },
            maxTicksLimit: 4,
            callback: v => v + 'k'
          },
          border: { display: false }
        }
      }
    }
  });

  // Disk donut chart
  const diskDoughnut = new Chart(document.getElementById('diskChart'), {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [0, 100],
        backgroundColor: ['rgba(255,255,255,0.9)', 'rgba(255,255,255,0.06)'],
        borderWidth: 0,
        hoverOffset: 0,
      }]
    },
    options: {
      responsive: false,
      cutout: '78%',
      animation: { duration: 600, easing: 'easeInOutQuart' },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
    }
  });

  // ── Push to chart ────────────────────────────────────────
  function pushData(chart, value, datasetIdx=0) {
    chart.data.datasets[datasetIdx].data.push(value);
    chart.data.datasets[datasetIdx].data.shift();
    chart.update('none');
  }

  // ── Uptime counter ────────────────────────────────────────
  let uptimeSeconds = 0;
  function formatUptime(s) {
    const h = String(Math.floor(s / 3600)).padStart(2, '0');
    const m = String(Math.floor((s % 3600) / 60)).padStart(2, '0');
    const sec = String(s % 60).padStart(2, '0');
    return `UP ${h}:${m}:${sec}`;
  }

  // ── Main update loop ─────────────────────────────────────
  async function update() {
    try {
      const res = await fetch('/stats');
      const d = await res.json();

      // — CPU —
      const cpu = d.cpu.percent;
      document.getElementById('cpu-val').innerHTML = `${cpu}<span class="metric-unit">%</span>`;
      document.getElementById('cpu-cores').textContent = `${d.cpu.cores} cores`;
      document.getElementById('cpu-bar').style.width = `${cpu}%`;
      document.getElementById('cpu-chart-val').textContent = cpu;
      pushData(cpuChart, cpu);

      // — Memory —
      const mem = d.memory.percent;
      document.getElementById('mem-val').innerHTML = `${mem}<span class="metric-unit">%</span>`;
      document.getElementById('mem-detail').textContent = `${d.memory.used_gb} / ${d.memory.total_gb} GB`;
      document.getElementById('mem-bar').style.width = `${mem}%`;
      document.getElementById('mem-chart-val').textContent = mem;
      pushData(memChart, mem);

      // — Disk —
      const disk = d.disk.percent;
      const diskFree = parseFloat((d.disk.total_gb - d.disk.used_gb).toFixed(1));
      document.getElementById('disk-val').innerHTML = `${disk}<span class="metric-unit">%</span>`;
      document.getElementById('disk-detail').textContent = `${d.disk.used_gb} / ${d.disk.total_gb} GB`;
      document.getElementById('disk-bar').style.width = `${disk}%`;
      document.getElementById('disk-ring-val').textContent = `${disk}%`;
      document.getElementById('disk-used-val').textContent = `${d.disk.used_gb} GB`;
      document.getElementById('disk-free-val').textContent = `${diskFree} GB`;
      document.getElementById('disk-total-val').textContent = `${d.disk.total_gb} GB`;
      document.getElementById('disk-used-fill').style.width = `${disk}%`;
      document.getElementById('disk-free-fill').style.width = `${100 - disk}%`;
      diskDoughnut.data.datasets[0].data = [disk, 100 - disk];
      diskDoughnut.update();

      // — Network —
      const sent = d.network.sent_kbps;
      const recv = d.network.recv_kbps;
      const total = parseFloat((sent + recv).toFixed(1));
      const netMax = Math.max(total, 1);
      document.getElementById('net-total').innerHTML = `${total}<span class="metric-unit">kb/s</span>`;
      document.getElementById('net-detail').innerHTML = `↑ ${sent} &nbsp; ↓ ${recv} kb/s`;
      document.getElementById('net-bar').style.width = `${Math.min(total / 10, 100)}%`;
      document.getElementById('net-sent-val').textContent = sent;
      document.getElementById('net-recv-val').textContent = recv;
      pushData(netChart, sent, 0);
      pushData(netChart, recv, 1);
      netChart.options.scales.y.max = Math.max(netMax * 1.3, 10);
      netChart.update('none');

      // — Uptime —
      uptimeSeconds = d.uptime_seconds;
      document.getElementById('uptime-display').textContent = formatUptime(uptimeSeconds);

      // — Timestamp —
      document.getElementById('ts-display').textContent = new Date().toISOString().replace('T', ' ').split('.')[0] + ' UTC';

    } catch(e) {
      console.error('Fetch error:', e);
    }
  }

  // Tick uptime locally every second
  setInterval(() => {
    uptimeSeconds++;
    document.getElementById('uptime-display').textContent = formatUptime(uptimeSeconds);
  }, 1000);

  update();
  setInterval(update, 2000);
</script>
</body>
</html>"""


@app.route('/')
def dashboard():
    return render_template_string(
        DASHBOARD_HTML,
        env_name=os.getenv("ENV_NAME", "production").upper(),
        hostname=platform.node()
    )


@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200


@app.route('/stats')
def get_stats():
    global _last_net, _last_net_time

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count(logical=True)

    # Memory
    mem = psutil.virtual_memory()

    # Disk
    disk = psutil.disk_usage('/')

    # Network rate
    net_now = psutil.net_io_counters()
    net_time_now = time.time()
    elapsed = max(net_time_now - _last_net_time, 0.001)

    sent_kbps = round((net_now.bytes_sent - _last_net.bytes_sent) / elapsed / 1024, 1)
    recv_kbps = round((net_now.bytes_recv - _last_net.bytes_recv) / elapsed / 1024, 1)

    _last_net = net_now
    _last_net_time = net_time_now

    return jsonify({
        "cpu": {
            "percent": round(cpu_percent, 1),
            "cores": cpu_count
        },
        "memory": {
            "percent": round(mem.percent, 1),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "total_gb": round(mem.total / (1024 ** 3), 2)
        },
        "disk": {
            "percent": round(disk.percent, 1),
            "used_gb": round(disk.used / (1024 ** 3), 1),
            "total_gb": round(disk.total / (1024 ** 3), 1)
        },
        "network": {
            "sent_kbps": max(sent_kbps, 0),
            "recv_kbps": max(recv_kbps, 0)
        },
        "uptime_seconds": int(time.time() - START_TIME)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
