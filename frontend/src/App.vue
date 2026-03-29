<template>
  <div class="container">
    <header class="app-header">
      <div class="logo-area">
        <span class="pulse-dot"></span>
        <h1>Autopilot OS <span>// Finance Agent</span></h1>
      </div>
      <p class="subtitle">AI-Driven Research & Automated Reporting</p>
    </header>

    <main>
      <div class="search-box">
        <div class="input-wrapper">
          <span class="icon">🔍</span>
          <input
            v-model="ticker"
            @keyup.enter="runPipeline"
            placeholder="Enter Ticker (e.g., TSLA, MSFT)"
            :disabled="loading"
          />
        </div>
        <button
          @click="runPipeline"
          :disabled="loading || !ticker"
          :class="{ 'btn-loading': loading }"
        >
          {{ loading ? 'Agent Operating...' : 'Execute Pipeline' }}
        </button>
      </div>

      <div v-if="error" class="error-banner">⚠️ {{ error }}</div>

      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>1. Ingesting Real-time Market Data...</p>
        <p class="fade-text">2. Agent selecting execution tools...</p>
      </div>

      <div v-if="result && !loading" class="dashboard fade-in">
        <!-- 头部卡片，包含PDF导出按钮 -->
        <div
          class="card head-card"
          style="display: flex; justify-content: space-between; align-items: center; width: 100%"
        >
          <div>
            <div class="company-badge">{{ result.ticker }}</div>
            <h2>{{ result.company_name }}</h2>
            <div class="price-display">
              <span class="currency">$</span>{{ result.current_price }}
            </div>
          </div>
          <button @click="downloadPDF" class="export-btn" :disabled="exporting">
            {{ exporting ? 'Generating...' : '📄 Export PDF Report' }}
          </button>
        </div>

        <!-- 新闻卡片 -->
        <div class="card news-card" v-if="result.news && result.news.length > 0">
          <div class="card-header">
            <h3>📰 Live Market Context</h3>
            <span class="tag">Tool Generated</span>
          </div>
          <ul class="news-list">
            <li v-for="(item, idx) in result.news" :key="idx">
              <span class="news-publisher">{{ item.publisher }}</span>
              <span class="news-title">{{ item.title }}</span>
            </li>
          </ul>
        </div>

        <!-- AI报告卡片 -->
        <div class="card report-card">
          <div class="card-header">
            <h3>🧠 Strategic Advisory Synthesis</h3>
            <span class="tag dark">LLM Reasoned</span>
          </div>
          <div class="report-content" v-html="formatText(result.ai_report)"></div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const ticker = ref('')
const loading = ref(false)
const exporting = ref(false)
const error = ref(null)
const result = ref(null)

const formatText = (text) => text?.replace(/\n/g, '<br/>') || ''


const runPipeline = async () => {
  if (!ticker.value) return
  loading.value = true
  error.value = null
  result.value = null

  try {
    const res = await fetch('http://localhost:8000/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ticker: ticker.value.trim().toUpperCase() })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Pipeline Failed')
    result.value = data.data
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 导出PDF功能
const downloadPDF = async () => {
  if (!result.value) return
  exporting.value = true
  try {
    const res = await fetch('http://localhost:8000/api/export_pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker: result.value.ticker,
        company_name: result.value.company_name,
        current_price: result.value.current_price,
        ai_report: result.value.ai_report
      })
    })

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${result.value.ticker}_Strategic_Report.pdf`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  } catch (err) {
    alert("Export failed: " + err.message)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
:root {
  --bg-color: #f8fafc;
  --surface: #ffffff;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --primary: #0f172a;
  --border: #e2e8f0;
}

body {
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--bg-color);
  color: var(--text-main);
  margin: 0;
}

.container {
  max-width: 900px;
  margin: 40px auto;
  padding: 0 20px;
}

/* Header */
.app-header {
  margin-bottom: 40px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background-color: #10b981;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

h1 span {
  color: var(--text-muted);
  font-weight: 400;
}

.subtitle {
  color: var(--text-muted);
  margin: 0;
  font-size: 14px;
}

/* Search Box */
.search-box {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.icon {
  position: absolute;
  left: 14px;
  color: #94a3b8;
}

input {
  width: 100%;
  padding: 14px 14px 14px 40px;
  font-size: 16px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

input:focus {
  border-color: #94a3b8;
}

button {
  padding: 0 24px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  white-space: nowrap;
}

button:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.btn-loading {
  animation: pulse-btn 1.5s infinite alternate;
}

@keyframes pulse-btn {
  from {
    opacity: 1;
  }
  to {
    opacity: 0.8;
  }
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text-muted);
  font-family: monospace;
}

.spinner {
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid var(--primary);
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.fade-text {
  opacity: 0.5;
  margin-top: 8px;
}

/* Cards */
.error-banner {
  background: #fee2e2;
  color: #b91c1c;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
  margin-bottom: 20px;
}

.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-main);
}

.tag {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 4px;
  background: #f1f5f9;
  color: #475569;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tag.dark {
  background: #1e293b;
  color: white;
}

/* Head Card */
.head-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.company-badge {
  background: #eff6ff;
  color: #2563eb;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.head-card h2 {
  margin: 0 0 8px;
  font-size: 28px;
}

.price-display {
  font-size: 36px;
  font-weight: 700;
}

.currency {
  color: var(--text-muted);
  font-size: 24px;
  margin-right: 4px;
  font-weight: 500;
}

/* News */
.news-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.news-list li {
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-bottom: 1px solid #f1f5f9;
  padding-bottom: 12px;
}

.news-list li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.news-publisher {
  font-size: 11px;
  font-weight: 700;
  color: #3b82f6;
  text-transform: uppercase;
}

.news-title {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

/* Report */
.report-content {
  font-size: 15px;
  line-height: 1.7;
  color: #334155;
}

/* Export Button */
.export-btn {
  background: #10b981;
  color: white;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.2);
  white-space: nowrap;
}

.export-btn:hover {
  background: #059669;
  transform: translateY(-1px);
}

.export-btn:disabled {
  background: #a7f3d0;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>