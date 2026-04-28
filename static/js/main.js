// ============================================================
//  GrammarLens - main.js
//  Handles all frontend interaction with the Flask API
// ============================================================

// ---- Character Counter ----
const textInput    = document.getElementById('textInput');
const charCounter  = document.getElementById('charCounter');

textInput.addEventListener('input', () => {
  const len = textInput.value.length;
  charCounter.textContent = `${len} / 2000`;
  charCounter.style.color = len > 1800 ? '#ef4444' : 'var(--text-3)';
});

// ---- Load Example ----
function loadExample(type) {
  const examples = {
    incorrect: [
      "She don't know nothing about the project and he are not helping nobody.",
      "He goed to the store and buyed a apple for hisself.",
      "They was very happy because there going to win the match.",
      "I has been waiting since two hours and nobody are here.",
      "She writed a letter but he don't replied yet.",
    ],
    correct: [
      "She does not know anything about the project and he is not helping anyone.",
      "He went to the store and bought an apple for himself.",
      "The students submitted their assignments on time and scored well.",
    ]
  };
  const list = examples[type] || examples.incorrect;
  textInput.value = list[Math.floor(Math.random() * list.length)];
  textInput.dispatchEvent(new Event('input'));
  textInput.focus();
}

// ---- Clear All ----
function clearAll() {
  textInput.value = '';
  textInput.dispatchEvent(new Event('input'));
  document.getElementById('results').style.display = 'none';
  document.getElementById('errorMsg').classList.remove('visible');
  textInput.focus();
}

// ---- Switch Tab ----
function switchTab(btn, targetId) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(targetId).classList.add('active');
}

// ---- Animate Score Circle ----
function animateScore(score, color) {
  const circle     = document.getElementById('scoreProgress');
  const numEl      = document.getElementById('scoreNumber');
  const circumf    = 326.7;
  const offset     = circumf - (score / 100) * circumf;

  circle.style.stroke          = color;
  circle.style.strokeDashoffset = offset;

  // count-up animation
  let current = 0;
  const step  = Math.ceil(score / 40);
  const timer = setInterval(() => {
    current = Math.min(current + step, score);
    numEl.textContent = current;
    if (current >= score) clearInterval(timer);
  }, 30);
}

// ---- Render Spelling Results ----
function renderSpelling(errors) {
  const el = document.getElementById('spellingResults');
  document.getElementById('spellCount').textContent = errors.length;

  if (errors.length === 0) {
    el.innerHTML = `
      <div class="no-issues">
        <span class="big-icon">✅</span>
        <strong>No spelling errors found!</strong>
        <p>Your spelling looks great.</p>
      </div>`;
    return;
  }

  el.innerHTML = errors.map(e => `
    <div class="spell-card">
      <div class="spell-icon">🔤</div>
      <div class="spell-body">
        <div>
          <span class="spell-word">${escapeHtml(e.word)}</span>
          <span class="spell-arrow">→</span>
          <span class="spell-fix">${escapeHtml(e.suggestion)}</span>
        </div>
        ${e.candidates.length > 0 ? `
        <div class="spell-candidates">
          Other suggestions:
          ${e.candidates.map(c => `<span>${escapeHtml(c)}</span>`).join('')}
        </div>` : ''}
      </div>
    </div>
  `).join('');
}

// ---- Render Grammar Results ----
function renderGrammar(issues) {
  const el = document.getElementById('grammarResults');
  document.getElementById('grammarCount').textContent = issues.length;

  if (issues.length === 0) {
    el.innerHTML = `
      <div class="no-issues">
        <span class="big-icon">🎉</span>
        <strong>No grammar issues found!</strong>
        <p>Your grammar looks correct.</p>
      </div>`;
    return;
  }

  el.innerHTML = issues.map(g => `
    <div class="grammar-card">
      <div class="grammar-type">${escapeHtml(g.type)}</div>
      <div class="grammar-message">${escapeHtml(g.message)}</div>
      <div class="grammar-example">${escapeHtml(g.example)}</div>
    </div>
  `).join('');
}

// ---- Render Score Stats ----
function renderStats(data) {
  document.getElementById('scoreStats').innerHTML = `
    <div class="stat-box">
      <div class="stat-num">${data.word_count}</div>
      <div class="stat-label">Words</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">${data.sentence_count}</div>
      <div class="stat-label">Sentences</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">${data.spelling_errors.length}</div>
      <div class="stat-label">Spell Errors</div>
    </div>
    <div class="stat-box">
      <div class="stat-num">${data.grammar_issues.length}</div>
      <div class="stat-label">Grammar Issues</div>
    </div>
  `;
}

// ---- Render Summary ----
function renderSummary(data) {
  const totalErrors = data.spelling_errors.length + data.grammar_issues.length;
  let verdictHtml   = '';
  let verdictBg     = '';

  if (data.score >= 90) {
    verdictBg  = 'rgba(34,197,94,.08)';
    verdictHtml = `
      <strong style="color:#22c55e">🌟 Excellent writing!</strong><br/>
      Your text has no significant issues. Well done!`;
  } else if (data.score >= 75) {
    verdictBg  = 'rgba(59,130,246,.08)';
    verdictHtml = `
      <strong style="color:#3b82f6">👍 Good writing!</strong><br/>
      Minor issues detected. Fix the highlighted problems to improve your score.`;
  } else if (data.score >= 60) {
    verdictBg  = 'rgba(245,158,11,.08)';
    verdictHtml = `
      <strong style="color:#f59e0b">📝 Fair writing.</strong><br/>
      Several issues found. Review the Spelling and Grammar tabs and make corrections.`;
  } else {
    verdictBg  = 'rgba(239,68,68,.08)';
    verdictHtml = `
      <strong style="color:#ef4444">⚠️ Needs improvement.</strong><br/>
      Many errors detected. Go through each tab and correct all highlighted issues.`;
  }

  document.getElementById('summaryResults').innerHTML = `
    <div class="summary-grid">
      <div class="summary-item">
        <div class="summary-item-label">Quality Score</div>
        <div class="summary-item-value" style="color:${data.grade_color}">${data.score}/100</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">ML Verdict</div>
        <div class="summary-item-value" style="font-size:.85rem">${escapeHtml(data.ml_label)}</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Model Confidence</div>
        <div class="summary-item-value">${data.ml_confidence}%</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Total Errors</div>
        <div class="summary-item-value" style="color:${totalErrors > 0 ? '#ef4444' : '#22c55e'}">${totalErrors}</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Characters</div>
        <div class="summary-item-value">${data.char_count}</div>
      </div>
      <div class="summary-item">
        <div class="summary-item-label">Avg Word Length</div>
        <div class="summary-item-value">${data.avg_word_len}</div>
      </div>
    </div>
    <div class="summary-verdict" style="background:${verdictBg}; border-color:${data.grade_color}">
      ${verdictHtml}
    </div>
  `;
}

// ---- Main Analyze Function ----
async function analyzeText() {
  const text = textInput.value.trim();

  // Validate
  if (!text) {
    showError('Please enter some text to analyze.');
    return;
  }
  if (text.length < 3) {
    showError('Text is too short. Please enter at least 3 characters.');
    return;
  }

  // UI state
  showLoading(true);
  hideError();
  document.getElementById('results').style.display = 'none';

  try {
    const response = await fetch('/analyze', {
      method  : 'POST',
      headers : { 'Content-Type': 'application/json' },
      body    : JSON.stringify({ text })
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.error || 'An error occurred. Please try again.');
      return;
    }

    // Populate results
    document.getElementById('gradeLabel').textContent  = data.grade;
    document.getElementById('gradeLabel').style.color  = data.grade_color;
    document.getElementById('mlBadge').textContent     = data.ml_label;
    document.getElementById('mlConf').textContent      = `Model confidence: ${data.ml_confidence}%`;

    renderStats(data);
    renderSpelling(data.spelling_errors);
    renderGrammar(data.grammar_issues);
    renderSummary(data);

    // Show results
    document.getElementById('results').style.display = 'block';
    animateScore(data.score, data.grade_color);

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    showError('Network error. Make sure the Flask server is running on port 5000.');
    console.error('Fetch error:', err);
  } finally {
    showLoading(false);
  }
}

// ---- Helpers ----
function showLoading(state) {
  const el = document.getElementById('loadingBar');
  el.classList.toggle('active', state);
}

function showError(msg) {
  const el = document.getElementById('errorMsg');
  el.textContent = '⚠ ' + msg;
  el.classList.add('visible');
  el.style.display = 'block';
}

function hideError() {
  const el = document.getElementById('errorMsg');
  el.classList.remove('visible');
  el.style.display = 'none';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ---- Allow Enter key (Ctrl+Enter) to analyze ----
textInput.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') {
    analyzeText();
  }
});
