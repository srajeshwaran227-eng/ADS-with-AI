/* ===================================================================
   ADS with AI — Main Script
   Tab switching, file uploads, mock analysis, animated counters,
   scroll reveals, and results page meter animation.
   =================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // ───────────── Mobile Menu ─────────────
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const navLinks = document.getElementById('navLinks');
  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      mobileBtn.textContent = navLinks.classList.contains('open') ? '✕' : '☰';
    });
  }

  // ───────────── Tab Switching ─────────────
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      tabBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      tabContents.forEach(tc => tc.classList.remove('active'));
      const panel = document.getElementById(`tab-${target}`);
      if (panel) {
        panel.classList.add('active');
        panel.style.animation = 'none';
        panel.offsetHeight; // trigger reflow
        panel.style.animation = '';
      }
    });
  });

  // ───────────── File Upload Handling ─────────────
  const types = ['document', 'image', 'video', 'audio'];
  const uploadedFiles = {};

  types.forEach(type => {
    const dropzone = document.getElementById(`dropzone-${type}`);
    const fileInput = document.getElementById(`file-${type}`);
    const fileInfo = document.getElementById(`fileinfo-${type}`);
    const fileName = document.getElementById(`filename-${type}`);
    const fileSize = document.getElementById(`filesize-${type}`);
    const removeBtn = fileInfo ? fileInfo.querySelector('.file-remove') : null;
    const analyzeBtn = document.getElementById(`analyze-${type}`);

    if (!dropzone || !fileInput) return;

    // Click to open file dialog
    dropzone.addEventListener('click', () => fileInput.click());

    // Drag events
    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('drag-over');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('drag-over');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
      if (e.dataTransfer.files.length > 0) {
        handleFile(e.dataTransfer.files[0], type);
      }
    });

    // File input change
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0], type);
      }
    });

    // Remove file
    if (removeBtn) {
      removeBtn.addEventListener('click', () => {
        clearFile(type);
      });
    }

    // Analyze button
    if (analyzeBtn) {
      analyzeBtn.addEventListener('click', () => {
        if (uploadedFiles[type]) {
          runAnalysis(type);
        }
      });
    }
  });

  function handleFile(file, type) {
    uploadedFiles[type] = file;

    const fileInfo = document.getElementById(`fileinfo-${type}`);
    const fileName = document.getElementById(`filename-${type}`);
    const fileSize = document.getElementById(`filesize-${type}`);
    const analyzeBtn = document.getElementById(`analyze-${type}`);

    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = formatFileSize(file.size);
    if (fileInfo) fileInfo.classList.add('visible');
    if (analyzeBtn) analyzeBtn.disabled = false;
  }

  function clearFile(type) {
    delete uploadedFiles[type];
    const fileInput = document.getElementById(`file-${type}`);
    const fileInfo = document.getElementById(`fileinfo-${type}`);
    const analyzeBtn = document.getElementById(`analyze-${type}`);
    const progress = document.getElementById(`progress-${type}`);
    const visual = document.getElementById(`visual-${type}`);

    if (fileInput) fileInput.value = '';
    if (fileInfo) fileInfo.classList.remove('visible');
    if (analyzeBtn) analyzeBtn.disabled = true;
    if (progress) progress.classList.remove('visible');
    if (visual) visual.classList.remove('visible');
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // ───────────── Backend API Configuration ─────────────
  // Change this to your Flask backend URL (default: localhost:5000)
  const API_BASE_URL = 'http://localhost:5000';

  // ───────────── Analysis (API + Fallback) ─────────────
  function runAnalysis(type) {
    const progress = document.getElementById(`progress-${type}`);
    const progressBar = document.getElementById(`progressbar-${type}`);
    const progressText = document.getElementById(`progresstext-${type}`);
    const analyzeBtn = document.getElementById(`analyze-${type}`);
    const visual = document.getElementById(`visual-${type}`);

    if (!progress || !progressBar) return;

    // Show visual for video and audio
    if (visual) visual.classList.add('visible');

    // Disable button
    if (analyzeBtn) {
      analyzeBtn.disabled = true;
      analyzeBtn.innerHTML = '<div class="spinner" style="width:20px;height:20px;border-width:2px;display:inline-block;vertical-align:middle;margin-right:8px;"></div> Analyzing...';
    }

    progress.classList.add('visible');

    // Get step elements
    const stepPrefix = type === 'document' ? 'doc' :
      type === 'image' ? 'img' :
        type === 'video' ? 'vid' : 'aud';

    const stepCount = type === 'document' || type === 'video' ? 5 : 4;
    const steps = [];
    for (let i = 1; i <= stepCount; i++) {
      steps.push(document.getElementById(`step-${stepPrefix}-${i}`));
    }

    // Try real API first, fall back to mock animation
    const file = uploadedFiles[type];
    if (file) {
      _tryBackendAnalysis(type, file, steps, stepCount, progressBar, progressText, analyzeBtn, visual);
    } else {
      _runMockAnimation(type, steps, stepCount, progressBar, progressText);
    }
  }

  /**
   * Attempt to send file to Flask backend.
   * Falls back to mock animation if backend is unreachable.
   */
  async function _tryBackendAnalysis(type, file, steps, stepCount, progressBar, progressText, analyzeBtn, visual) {
    // Start progress animation in parallel with the API call
    let animDone = false;
    let apiResult = null;
    let apiFailed = false;

    // Animate steps while waiting
    let currentStep = 0;
    const stepDuration = 600;

    function advanceUntilApi() {
      if (currentStep > 0 && steps[currentStep - 1]) {
        steps[currentStep - 1].classList.remove('active');
        steps[currentStep - 1].classList.add('done');
        const icon = steps[currentStep - 1].querySelector('.progress-step-icon');
        if (icon) icon.textContent = '✅';
      }

      if (apiResult) {
        // API returned — finish all remaining steps immediately
        for (let i = currentStep; i < stepCount; i++) {
          if (steps[i]) {
            steps[i].classList.add('done');
            const icon = steps[i].querySelector('.progress-step-icon');
            if (icon) icon.textContent = '✅';
          }
        }
        progressBar.style.width = '100%';
        progressText.textContent = '✅ Analysis complete!';
        sessionStorage.setItem('analysisResults', JSON.stringify(apiResult));
        _showRealityReport(type, apiResult);
        return;
      }

      if (apiFailed) {
        // Fall back to mock for remaining steps
        _runMockAnimation(type, steps, stepCount, progressBar, progressText, currentStep);
        return;
      }

      if (currentStep < stepCount) {
        if (steps[currentStep]) {
          steps[currentStep].classList.add('active');
          const icon = steps[currentStep].querySelector('.progress-step-icon');
          if (icon) icon.textContent = '🔄';
        }
        const pct = Math.round(((currentStep + 1) / stepCount) * 100);
        progressBar.style.width = pct + '%';
        progressText.textContent = `Analyzing... ${pct}%`;
        currentStep++;
        setTimeout(advanceUntilApi, stepDuration);
      } else {
        // Animation done but API still pending — just wait
        progressText.textContent = 'Waiting for server response...';
        setTimeout(advanceUntilApi, 500);
      }
    }

    advanceUntilApi();

    // Fire API request
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/analyze/${type}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        console.warn('Backend error:', errData);
        apiFailed = true;
        return;
      }

      const data = await response.json();
      const typeLabels = { document: 'Document', image: 'Image', video: 'Video', audio: 'Audio' };

      apiResult = {
        similarity: data.similarity || 0,
        aiProbability: data.ai_probability || 0,
        confidence: data.confidence || 'Moderate',
        type: typeLabels[type] || 'Document',
        isAI: (data.ai_probability || 0) > 60,
        status: data.status || '',
        timestamp: new Date().toISOString(),
      };
    } catch (err) {
      console.warn('Backend unreachable, using demo mode:', err.message);
      apiFailed = true;
    }
  }

  /**
   * Run the original mock step-by-step animation (used as fallback).
   */
  function _runMockAnimation(type, steps, stepCount, progressBar, progressText, startAt) {
    let currentStep = startAt || 0;
    const stepDuration = 800;

    function advanceStep() {
      if (currentStep > 0 && steps[currentStep - 1]) {
        steps[currentStep - 1].classList.remove('active');
        steps[currentStep - 1].classList.add('done');
        const icon = steps[currentStep - 1].querySelector('.progress-step-icon');
        if (icon) icon.textContent = '✅';
      }

      if (currentStep < stepCount) {
        if (steps[currentStep]) {
          steps[currentStep].classList.add('active');
          const icon = steps[currentStep].querySelector('.progress-step-icon');
          if (icon) icon.textContent = '🔄';
        }
        const pct = Math.round(((currentStep + 1) / stepCount) * 100);
        progressBar.style.width = pct + '%';
        progressText.textContent = `Analyzing... ${pct}%`;
        currentStep++;
        setTimeout(advanceStep, stepDuration);
      } else {
        progressBar.style.width = '100%';
        progressText.textContent = '✅ Analysis complete!';
        const mockResults = generateMockResults(type);
        sessionStorage.setItem('analysisResults', JSON.stringify(mockResults));
        _showRealityReport(type, mockResults);
      }
    }

    advanceStep();
  }

  function generateMockResults(type) {
    const similarity = Math.floor(Math.random() * 40) + 50;
    const aiProb = Math.floor(Math.random() * 50) + 40;
    const confidence = aiProb > 75 ? 'High' : aiProb > 55 ? 'Moderate' : 'Low';
    const typeLabels = {
      document: 'Document',
      image: 'Image',
      video: 'Video',
      audio: 'Audio'
    };

    return {
      similarity,
      aiProbability: aiProb,
      confidence,
      type: typeLabels[type] || 'Document',
      isAI: aiProb > 60,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Populate and reveal the Reality Report panel on the upload page.
   */
  function _showRealityReport(type, results) {
    const report = document.getElementById(`report-${type}`);
    if (!report) return;

    const aiProb = results.aiProbability || results.ai_probability || 0;
    const reality = Math.max(0, 100 - aiProb);
    const confidence = results.confidence || 'Moderate';
    const isAI = aiProb > 60;
    const verdict = isAI ? '⚠️ AI Generated' : '✅ Real / Human Created';

    const elAi = document.getElementById(`report-ai-${type}`);
    const elReality = document.getElementById(`report-reality-${type}`);
    const elConf = document.getElementById(`report-conf-${type}`);
    const elVerdict = document.getElementById(`report-verdict-${type}`);

    if (elAi) elAi.textContent = `${Math.round(aiProb)}%`;
    if (elReality) elReality.textContent = `${Math.round(reality)}%`;
    if (elConf) {
      elConf.textContent = confidence;
      elConf.style.color =
        confidence === 'High' ? 'var(--danger)' :
          confidence === 'Moderate' ? 'var(--warning)' : 'var(--success)';
    }
    if (elVerdict) {
      elVerdict.textContent = verdict;
      elVerdict.style.color = isAI ? 'var(--danger)' : 'var(--success)';
    }

    report.style.display = 'block';

    // Re-enable analysis button
    const analyzeBtn = document.getElementById(`analyze-${type}`);
    if (analyzeBtn) {
      analyzeBtn.disabled = false;
      const labels = { document: '📄 Analyze Document', image: '🖼️ Analyze Image', video: '🎬 Analyze Video', audio: '🎵 Analyze Audio' };
      analyzeBtn.innerHTML = labels[type] || '🔍 Analyze Again';
    }
  }

  // ───────────── Results Page Animations ─────────────
  if (document.getElementById('meterFill')) {
    animateResults();
  }

  function animateResults() {
    let results = null;
    try {
      results = JSON.parse(sessionStorage.getItem('analysisResults'));
    } catch (e) { /* ignore */ }

    // Default demo values
    if (!results) {
      results = {
        similarity: 72,
        aiProbability: 78,
        confidence: 'High',
        type: 'Document',
        isAI: true
      };
    }

    const meterFill = document.getElementById('meterFill');
    const meterValue = document.getElementById('meterValue');
    const similarityScore = document.getElementById('similarityScore');
    const aiProbability = document.getElementById('aiProbability');
    const detectionType = document.getElementById('detectionType');
    const confidenceText = document.getElementById('confidenceText');
    const resultBadge = document.getElementById('resultBadge');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceLabel = document.getElementById('confidenceLabel');

    // Animate circular meter
    const circumference = 2 * Math.PI * 100; // r=100
    const offset = circumference - (results.aiProbability / 100) * circumference;

    setTimeout(() => {
      if (meterFill) {
        meterFill.style.strokeDashoffset = offset;
      }
    }, 300);

    // Animate meter value counter
    animateCounter(meterValue, 0, results.aiProbability, 2000, '%');

    // Animate other values
    setTimeout(() => {
      animateCounter(similarityScore, 0, results.similarity, 1500, '%');
    }, 400);

    setTimeout(() => {
      animateCounter(aiProbability, 0, results.aiProbability, 1500, '%');
    }, 600);

    // Set detection type
    if (detectionType) {
      detectionType.textContent = results.type;
    }

    // Set confidence
    if (confidenceText) {
      setTimeout(() => {
        confidenceText.textContent = results.confidence;
        confidenceText.style.color =
          results.confidence === 'High' ? 'var(--danger)' :
            results.confidence === 'Moderate' ? 'var(--warning)' : 'var(--success)';
      }, 800);
    }

    // Result badge
    if (resultBadge) {
      setTimeout(() => {
        if (results.isAI) {
          resultBadge.className = 'result-badge ai';
          resultBadge.innerHTML = '⚠️ AI Generated';
        } else {
          resultBadge.className = 'result-badge human';
          resultBadge.innerHTML = '✅ Real / Human Created';
        }
      }, 1000);
    }

    // Confidence bar
    if (confidenceBar) {
      const confPct =
        results.confidence === 'High' ? 90 :
          results.confidence === 'Moderate' ? 60 : 30;

      setTimeout(() => {
        confidenceBar.style.width = confPct + '%';
        confidenceBar.className = 'confidence-bar-fill ' +
          (results.confidence === 'High' ? 'high' :
            results.confidence === 'Moderate' ? 'moderate' : 'low');
      }, 500);

      if (confidenceLabel) {
        confidenceLabel.textContent = results.confidence;
        confidenceLabel.style.color =
          results.confidence === 'High' ? 'var(--danger)' :
            results.confidence === 'Moderate' ? 'var(--warning)' : 'var(--success)';
      }
    }

    // Animate metric counters
    document.querySelectorAll('.counter').forEach(el => {
      const target = parseInt(el.dataset.target, 10);
      animateCounter(el, 0, target, 2000, '');
    });
  }

  function animateCounter(element, start, end, duration, suffix) {
    if (!element) return;
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(start + (end - start) * eased);
      element.textContent = current + suffix;
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = end + suffix;
      }
    }

    requestAnimationFrame(update);
  }

  // ───────────── Download Report Mock ─────────────
  const downloadBtn = document.getElementById('downloadReport');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      downloadBtn.innerHTML = '✅ Report Downloaded!';
      downloadBtn.style.background = 'linear-gradient(135deg, #00e676, #00c853)';

      setTimeout(() => {
        downloadBtn.innerHTML = '📥 Download Analysis Report';
        downloadBtn.style.background = '';
      }, 3000);

      // Create a mock text report
      let results = null;
      try { results = JSON.parse(sessionStorage.getItem('analysisResults')); } catch (e) { /* */ }
      if (!results) {
        results = { similarity: 72, aiProbability: 78, confidence: 'High', type: 'Document', isAI: true };
      }

      const reportText = `
════════════════════════════════════════════════
   ADS with AI — Analysis Report
════════════════════════════════════════════════

Detection Type:    ${results.type}
Analysis Date:     ${new Date().toLocaleString()}

────────────────────────────────────────────────
RESULTS
────────────────────────────────────────────────
Similarity Score:  ${results.similarity}%
AI Probability:    ${results.aiProbability}%
Confidence Level:  ${results.confidence}
Verdict:           ${results.isAI ? 'AI Generated' : 'Real / Human Created'}

────────────────────────────────────────────────
Note: This is a demo report. In production,
this would include detailed analysis metrics,
matched sources, and model explanations.
════════════════════════════════════════════════
`;

      const blob = new Blob([reportText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'ADS_with_AI_Report.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  }

  // ───────────── Scroll Reveal Animations ─────────────
  const revealElements = document.querySelectorAll('.reveal');

  function checkReveal() {
    const windowHeight = window.innerHeight;
    revealElements.forEach(el => {
      const elementTop = el.getBoundingClientRect().top;
      if (elementTop < windowHeight - 80) {
        el.classList.add('visible');
      }
    });
  }

  window.addEventListener('scroll', checkReveal);
  checkReveal(); // Initial check

  // ───────────── Stat Number Animation on Scroll ─────────────
  const statNumbers = document.querySelectorAll('.stat-number[data-target]');
  let statsAnimated = false;

  function checkStatAnimation() {
    if (statsAnimated) return;
    statNumbers.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight - 50) {
        statsAnimated = true;
        statNumbers.forEach(stat => {
          const target = parseFloat(stat.dataset.target);
          const isDecimal = target % 1 !== 0;
          animateStatCounter(stat, 0, target, 2500, isDecimal);
        });
      }
    });
  }

  function animateStatCounter(element, start, end, duration, isDecimal) {
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;
      element.textContent = isDecimal ? current.toFixed(1) : Math.floor(current);
      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = isDecimal ? end.toFixed(1) : end;
      }
    }

    requestAnimationFrame(update);
  }

  window.addEventListener('scroll', checkStatAnimation);
  checkStatAnimation();

  // ───────────── Navbar scroll effect ─────────────
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (navbar) {
      if (window.scrollY > 50) {
        navbar.style.boxShadow = '0 4px 30px rgba(0,0,0,0.5), 0 0 50px rgba(180,74,255,0.12)';
      } else {
        navbar.style.boxShadow = '';
      }
    }
  });
});
