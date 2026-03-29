<template>
  <div class="container">
    <header>
      <h1>🚀 Corporate Finance Autopilot</h1>
      <p>Agentic Data Ingestion & Reasoning Pipeline. Not Investment Advice.</p>
    </header>

    <main>
      <div class="search-box">
        <input v-model="ticker" @keyup.enter="runPipeline" placeholder="Enter Ticker (e.g., TSLA, AAPL, NVDA)" :disabled="loading" />
        <button @click="runPipeline" :disabled="loading || !ticker">
          {{ loading ? 'Agent Computing...' : 'Execute Pipeline' }}
        </button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>

      <div v-if="result" class="dashboard">
        <div class="card head-card">
          <h2>{{ result.company_name }} ({{ result.ticker }})</h2>
          <div class="price">${{ result.current_price }}</div>
        </div>

        <div class="card" v-if="result.scenarios && result.scenarios.base_case">
          <h3>📊 Agent Sensitized Scenarios</h3>
          <div class="grid">
            <div class="box up">
              <h4>Upside</h4>
              <div class="target">${{ result.scenarios.upside_case.price }}</div>
              <small>{{ result.scenarios.upside_case.desc }}</small>
            </div>
            <div class="box base">
              <h4>Base</h4>
              <div class="target">${{ result.scenarios.base_case.price }}</div>
              <small>{{ result.scenarios.base_case.desc }}</small>
            </div>
            <div class="box down">
              <h4>Downside</h4>
              <div class="target">${{ result.scenarios.downside_case.price }}</div>
              <small>{{ result.scenarios.downside_case.desc }}</small>
            </div>
          </div>
        </div>

        <div class="card">
          <h3>📝 Strategic Advisory Report</h3>
          <div class="report" v-html="formatText(result.ai_report)"></div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const ticker = ref('')
const loading = ref(false)
const result = ref(null)
const error = ref(null)

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
</script>

<style scoped>
body { font-family: system-ui, sans-serif; background: #f4f4f5; color: #18181b; margin: 0; }
.container { max-width: 800px; margin: 40px auto; padding: 0 20px; }
header { text-align: center; margin-bottom: 30px; }
h1 { margin: 0 0 10px; font-size: 28px; }
p { color: #71717a; margin: 0; }
.search-box { display: flex; gap: 10px; justify-content: center; margin-bottom: 30px; }
input { padding: 12px; font-size: 16px; border: 1px solid #d4d4d8; border-radius: 6px; width: 250px; }
button { padding: 12px 20px; background: #18181b; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
button:disabled { background: #a1a1aa; }
.error { color: #ef4444; text-align: center; margin-bottom: 20px; font-weight: bold; }
.dashboard { display: flex; flex-direction: column; gap: 20px; }
.card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #e4e4e7; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.head-card { text-align: center; }
.head-card h2 { margin: 0 0 10px; }
.price { font-size: 32px; font-weight: bold; color: #10b981; }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }
.box { padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #e4e4e7; }
.up { background: #ecfdf5; border-color: #a7f3d0; }
.base { background: #fafafa; }
.down { background: #fef2f2; border-color: #fecaca; }
.box h4 { margin: 0 0 10px; color: #52525b; }
.target { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
.up .target { color: #059669; }
.down .target { color: #dc2626; }
.box small { font-size: 12px; color: #71717a; line-height: 1.4; display: block; }
.report { line-height: 1.6; color: #3f3f46; font-size: 15px; margin-top: 15px; }
</style>