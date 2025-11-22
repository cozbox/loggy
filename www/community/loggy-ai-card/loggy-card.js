// Custom Lovelace card for Loggy AI
class LoggyCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity (analysis sensor)');
    }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateContent();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 16px;
        }
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .card-title {
          font-size: 24px;
          font-weight: 500;
        }
        .stats-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 12px;
          margin-bottom: 16px;
        }
        .stat-box {
          background: var(--primary-background-color);
          border-radius: 8px;
          padding: 12px;
          text-align: center;
        }
        .stat-value {
          font-size: 32px;
          font-weight: bold;
          margin-bottom: 4px;
        }
        .stat-label {
          font-size: 12px;
          color: var(--secondary-text-color);
          text-transform: uppercase;
        }
        .stat-box.errors .stat-value {
          color: var(--error-color);
        }
        .stat-box.warnings .stat-value {
          color: var(--warning-color);
        }
        .stat-box.new-issues .stat-value {
          color: var(--info-color);
        }
        .analysis-container {
          background: var(--primary-background-color);
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 16px;
          max-height: 400px;
          overflow-y: auto;
        }
        .analysis-text {
          white-space: pre-wrap;
          line-height: 1.6;
          font-size: 14px;
        }
        .analysis-text h3 {
          margin-top: 16px;
          margin-bottom: 8px;
        }
        .button-container {
          display: flex;
          gap: 8px;
          justify-content: flex-end;
        }
        .analyze-button {
          background: var(--primary-color);
          color: var(--text-primary-color);
          border: none;
          border-radius: 4px;
          padding: 12px 24px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.3s;
        }
        .analyze-button:hover {
          background: var(--primary-color-dark);
        }
        .analyze-button:disabled {
          background: var(--disabled-text-color);
          cursor: not-allowed;
        }
        .last-run {
          font-size: 12px;
          color: var(--secondary-text-color);
          margin-bottom: 16px;
        }
        .loading {
          text-align: center;
          padding: 20px;
          color: var(--secondary-text-color);
        }
      </style>
      <ha-card>
        <div class="card-header">
          <div class="card-title">🤖 Loggy AI</div>
        </div>
        <div id="content"></div>
      </ha-card>
    `;
    
    // Add event listener only once during initial render
    this._boundTriggerAnalysis = this.triggerAnalysis.bind(this);
  }

  updateContent() {
    if (!this._hass || !this.config) return;

    const entityId = this.config.entity;
    const entity = this._hass.states[entityId];
    
    if (!entity) {
      this.shadowRoot.getElementById('content').innerHTML = `
        <div class="loading">Entity not found: ${entityId}</div>
      `;
      return;
    }

    const errorEntity = this._hass.states[entityId.replace('analysis', 'error_count')];
    const warningEntity = this._hass.states[entityId.replace('analysis', 'warning_count')];
    const newIssuesEntity = this._hass.states[entityId.replace('analysis', 'new_issues_count')];

    const errors = errorEntity ? errorEntity.state : '0';
    const warnings = warningEntity ? warningEntity.state : '0';
    const newIssues = newIssuesEntity ? newIssuesEntity.state : '0';

    const analysisText = entity.attributes.analysis_text || entity.state || 'No analysis available';
    const lastRun = entity.attributes.last_run;

    let lastRunText = '';
    if (lastRun) {
      const lastRunDate = new Date(lastRun);
      lastRunText = `Last analysis: ${lastRunDate.toLocaleString()}`;
    }

    const content = `
      ${lastRunText ? `<div class="last-run">${lastRunText}</div>` : ''}
      <div class="stats-container">
        <div class="stat-box errors">
          <div class="stat-value">${errors}</div>
          <div class="stat-label">🔴 Errors</div>
        </div>
        <div class="stat-box warnings">
          <div class="stat-value">${warnings}</div>
          <div class="stat-label">⚠️ Warnings</div>
        </div>
        <div class="stat-box new-issues">
          <div class="stat-value">${newIssues}</div>
          <div class="stat-label">🆕 New Issues</div>
        </div>
      </div>
      <div class="analysis-container">
        <div class="analysis-text">${this.formatAnalysis(analysisText)}</div>
      </div>
      <div class="button-container">
        <button class="analyze-button" id="analyze-btn">
          ▶️ Analyze Now
        </button>
      </div>
    `;

    this.shadowRoot.getElementById('content').innerHTML = content;

    // Remove previous listener if it exists, then add new one
    const analyzeBtn = this.shadowRoot.getElementById('analyze-btn');
    if (analyzeBtn) {
      analyzeBtn.removeEventListener('click', this._boundTriggerAnalysis);
      analyzeBtn.addEventListener('click', this._boundTriggerAnalysis);
    }
  }

  formatAnalysis(text) {
    // Basic formatting for better readability
    return text
      .replace(/🔴 CRITICAL ISSUES/g, '<strong style="color: var(--error-color);">🔴 CRITICAL ISSUES</strong>')
      .replace(/⚠️ WARNINGS/g, '<strong style="color: var(--warning-color);">⚠️ WARNINGS</strong>')
      .replace(/💡 RECOMMENDATIONS/g, '<strong style="color: var(--info-color);">💡 RECOMMENDATIONS</strong>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }

  triggerAnalysis() {
    this._hass.callService('loggy_ai', 'analyze_logs', {});
    
    const analyzeBtn = this.shadowRoot.getElementById('analyze-btn');
    if (analyzeBtn) {
      analyzeBtn.disabled = true;
      analyzeBtn.textContent = '⏳ Analyzing...';
      
      // Reset button state after a reasonable time
      // Analysis typically takes 10-60 seconds depending on log size
      setTimeout(() => {
        if (analyzeBtn) {
          analyzeBtn.disabled = false;
          analyzeBtn.textContent = '▶️ Analyze Now';
        }
      }, 30000); // 30 seconds to allow for analysis completion
    }
  }

  getCardSize() {
    return 5;
  }
}

customElements.define('loggy-card', LoggyCard);

// Announce the card to Home Assistant
window.customCards = window.customCards || [];
window.customCards.push({
  type: 'loggy-card',
  name: 'Loggy AI Card',
  description: 'Display Loggy AI log analysis results',
  preview: false,
  documentationURL: 'https://github.com/cozbox/loggy',
});