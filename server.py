"""
Lightweight local web server for QQ Show 2000 Outfit Saver.
Uses Python's standard library http.server (no extra pip dependencies required).
"""

import os
import sys
import re
import json
import base64
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import saver

PORT = 8080
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>QQ Show 2000 - Outfit Saver & Layer Compositor</title>
  <link rel="icon" href="https://qqshow2000.com/assets/qqshow_icon-DtnSGaFa.PNG">
  <style>
    :root {
      --bg-color: #f0edf6;
      --window-bg: #ece9d8;
      --window-border: #0055ea;
      --titlebar-start: #0058ee;
      --titlebar-end: #3f95ff;
      --btn-face: #f0f0f0;
      --btn-border: #7f9db9;
      --text: #222;
      --accent: #ff4081;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: radial-gradient(circle at 10% 20%, #ffeaf1 0%, #f1edfc 50%, #e2f1fc 100%);
      color: var(--text);
      min-height: 100vh;
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .main-window {
      width: 100%;
      max-width: 900px;
      background: #ffffff;
      border: 2px solid #5a667d;
      border-radius: 8px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.15), 0 2px 6px rgba(0, 0, 0, 0.08);
      overflow: hidden;
      margin-bottom: 24px;
    }

    .window-header {
      background: linear-gradient(90deg, #595085 0%, #8b7cb6 100%);
      color: white;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      user-select: none;
    }

    .window-title {
      font-weight: 700;
      font-size: 15px;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .window-title a {
      color: inherit;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: opacity 0.15s;
    }

    .window-title a:hover {
      text-decoration: underline;
      opacity: 0.9;
    }

    .window-title img {
      width: 20px;
      height: 20px;
      image-rendering: pixelated;
    }

    .window-body {
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .intro-banner {
      background: #faf7ff;
      border: 1px solid #d9d2ea;
      border-radius: 6px;
      padding: 14px 18px;
      font-size: 14px;
      line-height: 1.5;
      color: #4a3e66;
    }

    .intro-banner strong {
      color: #2e1d52;
    }

    .banner-link {
      color: #595085;
      font-weight: 700;
      text-decoration: underline;
      text-underline-offset: 2px;
      transition: color 0.15s;
    }

    .banner-link:hover {
      color: #ee3a76;
    }

    .banner-link code {
      color: inherit;
      background: rgba(124, 92, 183, 0.08);
      padding: 1px 4px;
      border-radius: 3px;
    }

    .input-section {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .url-input-group {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    .url-input {
      flex: 1;
      min-width: 280px;
      padding: 12px 14px;
      font-size: 15px;
      border: 2px solid #b6b0c9;
      border-radius: 6px;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      font-family: monospace;
    }

    .url-input:focus {
      border-color: #7c5cb7;
      box-shadow: 0 0 0 3px rgba(124, 92, 183, 0.2);
    }

    .btn-primary {
      background: linear-gradient(180deg, #ff6fa0 0%, #ee3a76 100%);
      color: white;
      border: 1px solid #d22862;
      border-radius: 6px;
      padding: 12px 24px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
      box-shadow: 0 2px 4px rgba(238, 58, 118, 0.3);
    }

    .btn-primary:hover {
      background: linear-gradient(180deg, #ff82ad 0%, #fc4a84 100%);
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(238, 58, 118, 0.4);
    }

    .btn-primary:active {
      transform: translateY(1px);
      box-shadow: none;
    }

    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
      transform: none;
    }

    .options-row {
      display: flex;
      gap: 20px;
      flex-wrap: wrap;
      align-items: center;
      padding: 12px 16px;
      background: #fbfbfd;
      border: 1px solid #e5e2ed;
      border-radius: 6px;
    }

    .option-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13.5px;
      color: #444;
    }

    .option-item select {
      padding: 6px 10px;
      border: 1px solid #b8b3c7;
      border-radius: 4px;
      background: white;
      font-size: 13px;
      outline: none;
    }

    .example-chips {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      font-size: 13px;
      color: #666;
    }

    .chip {
      background: #ede8f5;
      color: #554477;
      padding: 4px 10px;
      border-radius: 12px;
      cursor: pointer;
      font-family: monospace;
      font-size: 12px;
      border: 1px solid #d4cde2;
      transition: background 0.15s;
    }

    .chip:hover {
      background: #dfd7ee;
    }

    /* Result Stage */
    .result-section {
      display: none;
      grid-template-columns: 320px 1fr;
      gap: 24px;
      margin-top: 10px;
      padding-top: 20px;
      border-top: 2px dashed #ded9e8;
    }

    @media (max-width: 768px) {
      .result-section {
        grid-template-columns: 1fr;
      }
    }

    .preview-box {
      background: #faf9fd;
      border: 1px solid #dcd7e6;
      border-radius: 8px;
      padding: 18px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 14px;
    }

    .preview-viewport {
      width: 280px;
      height: 452px;
      border-radius: 6px;
      border: 2px solid #c9c4d4;
      display: flex;
      justify-content: center;
      align-items: center;
      overflow: hidden;
      background-color: #f8f8f8;
      background-image: 
        linear-gradient(45deg, #eee 25%, transparent 25%), 
        linear-gradient(-45deg, #eee 25%, transparent 25%), 
        linear-gradient(45deg, transparent 75%, #eee 75%), 
        linear-gradient(-45deg, transparent 75%, #eee 75%);
      background-size: 16px 16px;
      background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
    }

    .preview-viewport img {
      max-width: 100%;
      max-height: 100%;
      display: block;
      image-rendering: pixelated;
    }

    .download-btn {
      width: 100%;
      text-align: center;
      text-decoration: none;
      background: linear-gradient(180deg, #10b981 0%, #059669 100%);
      color: white;
      padding: 12px 16px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 15px;
      border: 1px solid #047857;
      display: block;
      box-shadow: 0 2px 4px rgba(5, 150, 105, 0.3);
      transition: all 0.15s;
    }

    .download-btn:hover {
      background: linear-gradient(180deg, #34d399 0%, #10b981 100%);
      transform: translateY(-1px);
    }

    .details-box {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .meta-card {
      background: #fbfbfd;
      border: 1px solid #e3dfed;
      border-radius: 6px;
      padding: 14px 18px;
    }

    .meta-title {
      font-size: 18px;
      font-weight: 700;
      color: #3b2d56;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .meta-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 10px;
      font-size: 13px;
    }

    .meta-pill {
      background: #ffffff;
      border: 1px solid #dfdae8;
      border-radius: 4px;
      padding: 6px 10px;
    }

    .meta-pill span {
      display: block;
      color: #887e9c;
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 600;
    }

    .meta-pill strong {
      color: #2d2242;
      font-size: 14px;
    }

    .layers-table-card {
      background: #ffffff;
      border: 1px solid #e3dfed;
      border-radius: 6px;
      overflow: hidden;
    }

    .layers-header {
      background: #f4f1f8;
      padding: 10px 14px;
      font-size: 13.5px;
      font-weight: 700;
      color: #493b63;
      border-bottom: 1px solid #e3dfed;
    }

    .layers-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }

    .layers-table th, .layers-table td {
      padding: 8px 12px;
      text-align: left;
      border-bottom: 1px solid #f0ecf6;
    }

    .layers-table th {
      background: #faf8fc;
      color: #716686;
      font-weight: 600;
      font-size: 12px;
    }

    .z-tag {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      background: #efeaf7;
      color: #63459c;
      font-weight: 700;
      font-size: 11.5px;
      font-family: monospace;
    }

    .loading-spinner {
      display: none;
      align-items: center;
      justify-content: center;
      gap: 12px;
      padding: 24px;
      color: #554477;
      font-weight: 600;
    }

    .spinner {
      width: 24px;
      height: 24px;
      border: 3px solid #ded9ea;
      border-top-color: #ee3a76;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    .error-banner {
      display: none;
      background: #fff1f2;
      border: 1px solid #fecdd3;
      color: #be123c;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
    }

    /* History / Faved Fits Section */
    .history-window {
      margin-top: 4px;
    }

    .history-header-right {
      font-size: 12.5px;
      font-style: italic;
      color: #f1edfb;
      white-space: nowrap;
      user-select: none;
    }

    .history-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .history-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 14px;
      background: #faf9fd;
      border: 1px solid #e2dded;
      border-radius: 6px;
      transition: background 0.15s, border-color 0.15s;
    }

    .history-item:hover {
      background: #f4effb;
      border-color: #cbbfe0;
    }

    .history-info {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      min-width: 0;
    }

    .history-id {
      font-family: monospace;
      font-weight: 700;
      color: #554477;
      background: #ece7f6;
      border: 1px solid #dcd5eb;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 13px;
    }

    .history-name {
      font-weight: 600;
      font-size: 14px;
      color: #2e1d52;
    }

    .history-actions {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
      flex-wrap: wrap;
    }

    .btn-action {
      background: #ffffff;
      border: 1px solid #b8b1cb;
      color: #493b63;
      padding: 6px 12px;
      border-radius: 4px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      transition: all 0.15s;
      user-select: none;
    }

    .btn-action:hover {
      background: #f0eaf8;
      border-color: #7c5cb7;
      color: #2e1d52;
      transform: translateY(-1px);
    }

    .btn-action.btn-copy {
      min-width: 78px;
      justify-content: center;
    }

    .btn-action.btn-copy.copied {
      background: #ecfdf5;
      border-color: #10b981;
      color: #059669;
    }

    .btn-action.btn-delete {
      color: #999;
      border-color: transparent;
      padding: 6px 8px;
    }

    .btn-action.btn-delete:hover {
      color: #dc2626;
      background: #fee2e2;
    }

    .history-empty {
      padding: 24px;
      text-align: center;
      color: #887e9c;
      font-size: 13.5px;
      font-style: italic;
      background: #faf9fd;
      border: 1px dashed #ded9e8;
      border-radius: 6px;
    }
  </style>

</head>
<body>

  <div class="main-window">
    <div class="window-header">
      <div class="window-title">
        <a href="https://qqshow2000.com/" target="_blank" rel="noopener noreferrer">
          <img src="https://qqshow2000.com/assets/qqshow_icon-DtnSGaFa.PNG" alt="icon">
          <span>QQ Show 2000</span>
        </a>
        <span style="opacity: 0.9; font-weight: normal;">- Animated Outfit Saver</span>
      </div>
      <div style="font-size: 12px; opacity: 0.85;">v1.0.0</div>
    </div>

    <div class="window-body">
      <div class="intro-banner">
        <strong>Preserve your <a href="https://qqshow2000.com/" target="_blank" rel="noopener noreferrer" class="banner-link">QQ Show avatars</a>:</strong> Paste any outfit link (e.g. <a href="https://qqshow2000.com/?id=e9fn6oxd" target="_blank" rel="noopener noreferrer" class="banner-link"><code>https://qqshow2000.com/?id=e9fn6oxd</code></a>) to download all animated layer GIFs, composite them at their exact z-index stack, align their animation frame cycles, and render a complete animated GIF!
      </div>

      <div class="input-section">
        <div class="options-row">
          <div class="option-item">
            <label for="scaleSelect"><strong>Scale:</strong></label>
            <select id="scaleSelect">
              <option value="1">1x Native (140 × 226)</option>
              <option value="2" selected>2x Crisp (280 × 452)</option>
              <option value="3">3x HD (420 × 678)</option>
              <option value="4">4x Ultra (560 × 904)</option>
            </select>
          </div>

          <div class="option-item">
            <label for="bgSelect"><strong>Background:</strong></label>
            <select id="bgSelect">
              <option value="auto" selected>Auto (Asset bg or #f8f8f8)</option>
              <option value="transparent">Transparent (Checkerboard)</option>
              <option value="canvas">Site Canvas (#f8f8f8)</option>
              <option value="#ffffff">White (#ffffff)</option>
              <option value="#000000">Black (#000000)</option>
            </select>
          </div>
        </div>

        <div class="url-input-group">
          <input 
            type="text" 
            id="urlInput" 
            class="url-input" 
            placeholder="Paste URL or ID (e.g. https://qqshow2000.com/?id=e9fn6oxd)"
            value="https://qqshow2000.com/?id=e9fn6oxd"
          >
          <button id="generateBtn" class="btn-primary" onclick="generateOutfit()">
            <span>Generate GIF</span>
          </button>
        </div>

        <div class="example-chips">
          <span>Examples:</span>
          <span class="chip" onclick="setInput('https://qqshow2000.com/?id=e9fn6oxd')">e9fn6oxd (Full Outfit)</span>
          <span class="chip" onclick="setInput('e9fn6oxd')">Raw ID (e9fn6oxd)</span>
        </div>
      </div>


      <div id="loading" class="loading-spinner">
        <div class="spinner"></div>
        <span>Downloading layer GIFs & calculating animation timeline...</span>
      </div>

      <div id="errorBanner" class="error-banner"></div>

      <div id="resultSection" class="result-section">
        <div class="preview-box">
          <div class="preview-viewport">
            <img id="previewImg" src="" alt="Composited Outfit">
          </div>
          <a id="downloadLink" href="#" download="" class="download-btn">
            💾 Download Animated GIF
          </a>
        </div>

        <div class="details-box">
          <div class="meta-card">
            <div class="meta-title">
              <span id="outfitName">Outfit Name</span>
              <span id="outfitIdTag" class="z-tag">ID: ...</span>
            </div>
            <div class="meta-grid">
              <div class="meta-pill">
                <span>Dimensions</span>
                <strong id="metaDimensions">280 × 452</strong>
              </div>
              <div class="meta-pill">
                <span>Frames</span>
                <strong id="metaFrames">64</strong>
              </div>
              <div class="meta-pill">
                <span>Loop Duration</span>
                <strong id="metaDuration">6.0s</strong>
              </div>
              <div class="meta-pill">
                <span>File Size</span>
                <strong id="metaSize">2.3 MB</strong>
              </div>
            </div>
          </div>

          <div class="layers-table-card">
            <div class="layers-header">
              Composited Layer Stack (<span id="layersCount">0</span> layers)
            </div>
            <table class="layers-table">
              <thead>
                <tr>
                  <th>z-index</th>
                  <th>Category</th>
                  <th>Item Name</th>
                  <th>Frames</th>
                  <th>Cycle</th>
                </tr>
              </thead>
              <tbody id="layersBody">
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- History / Fits You Faved Window -->
  <div class="main-window history-window">
    <div class="window-header">
      <div class="window-title">
        <strong>History</strong> &nbsp;— Fits You Faved
      </div>
      <div class="history-header-right">
        <em>🔒 Private Local Storage (stored only on your device)</em>
      </div>
    </div>

    <div class="window-body">
      <div id="historyContainer" class="history-list">
        <!-- Rendered dynamically from localStorage -->
      </div>
    </div>
  </div>

  <script>
    const FAVES_KEY = 'qqshow_faved_fits';

    function setInput(val) {
      document.getElementById('urlInput').value = val;
    }

    function formatBytes(bytes) {
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / 1048576).toFixed(2) + ' MB';
    }

    function escapeHtml(str) {
      const div = document.createElement('div');
      div.textContent = str;
      return div.innerHTML;
    }

    function getFavedFits() {
      try {
        const raw = localStorage.getItem(FAVES_KEY);
        if (!raw) {
          const initial = [{
            id: 'e9fn6oxd',
            name: 'My Outfit',
            timestamp: Date.now()
          }];
          localStorage.setItem(FAVES_KEY, JSON.stringify(initial));
          return initial;
        }
        return JSON.parse(raw);
      } catch (e) {
        return [];
      }
    }

    function saveFavedFits(fits) {
      try {
        localStorage.setItem(FAVES_KEY, JSON.stringify(fits));
      } catch (e) {
        console.error('Failed to save to localStorage', e);
      }
      renderHistory();
    }

    function addFaveFit(fit) {
      let fits = getFavedFits();
      fits = fits.filter(f => f.id !== fit.id);
      fits.unshift(fit);
      if (fits.length > 50) fits = fits.slice(0, 50);
      saveFavedFits(fits);
    }

    function removeFaveFit(id) {
      let fits = getFavedFits();
      fits = fits.filter(f => f.id !== id);
      saveFavedFits(fits);
    }

    function loadFitToUrl(id) {
      const url = `https://qqshow2000.com/?id=${id}`;
      const input = document.getElementById('urlInput');
      input.value = url;
      input.scrollIntoView({ behavior: 'smooth', block: 'center' });
      input.focus();
    }

    function copyFitUrl(id, btnElement) {
      const url = `https://qqshow2000.com/?id=${id}`;
      navigator.clipboard.writeText(url).then(() => {
        const origText = btnElement.innerHTML;
        btnElement.innerHTML = '✓ Copied!';
        btnElement.classList.add('copied');
        setTimeout(() => {
          btnElement.innerHTML = origText;
          btnElement.classList.remove('copied');
        }, 1500);
      }).catch(err => {
        prompt('Copy this URL:', url);
      });
    }

    function renderHistory() {
      const container = document.getElementById('historyContainer');
      if (!container) return;
      const fits = getFavedFits();

      if (fits.length === 0) {
        container.innerHTML = `
          <div class="history-empty">
            No fits saved yet. Generate an outfit to see it saved here, or <a href="javascript:void(0)" onclick="loadFitToUrl('e9fn6oxd')" class="banner-link">load the example fit (e9fn6oxd)</a>.
          </div>
        `;
        return;
      }

      container.innerHTML = '';
      fits.forEach(fit => {
        const row = document.createElement('div');
        row.className = 'history-item';
        const dateStr = fit.timestamp ? new Date(fit.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '';
        const qqUrl = `https://qqshow2000.com/?id=${fit.id}`;

        row.innerHTML = `
          <div class="history-info">
            <span class="history-id">${fit.id}</span>
            <span class="history-name">${escapeHtml(fit.name || 'Outfit')}</span>
            ${dateStr ? `<span class="history-date">${dateStr}</span>` : ''}
          </div>
          <div class="history-actions">
            <button class="btn-action" onclick="loadFitToUrl('${fit.id}')" title="Send to URL input box above">
              ⬆ Load
            </button>
            <a class="btn-action" href="${qqUrl}" target="_blank" rel="noopener noreferrer" title="Open on qqshow2000.com in a new tab">
              ↗ QQ Show URL
            </a>
            <button class="btn-action btn-copy" onclick="copyFitUrl('${fit.id}', this)" title="Copy URL to clipboard">
              📋 Copy
            </button>
            <button class="btn-action btn-delete" onclick="removeFaveFit('${fit.id}')" title="Remove from favorites">
              ✕
            </button>
          </div>
        `;
        container.appendChild(row);
      });
    }

    async function generateOutfit() {
      const urlInput = document.getElementById('urlInput').value.trim();
      if (!urlInput) return;

      const scale = document.getElementById('scaleSelect').value;
      const bg = document.getElementById('bgSelect').value;
      const btn = document.getElementById('generateBtn');
      const loading = document.getElementById('loading');
      const errBanner = document.getElementById('errorBanner');
      const resultSec = document.getElementById('resultSection');

      btn.disabled = true;
      loading.style.display = 'flex';
      errBanner.style.display = 'none';
      resultSec.style.display = 'none';

      try {
        const resp = await fetch('/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: urlInput,
            scale: parseInt(scale, 10),
            bg_mode: bg
          })
        });

        const data = await resp.json();
        if (!resp.ok || data.error) {
          throw new Error(data.error || 'Failed to generate outfit composite');
        }

        // Render preview & details
        document.getElementById('previewImg').src = data.gif_data_url;
        const dlLink = document.getElementById('downloadLink');
        dlLink.href = data.gif_data_url;
        dlLink.download = data.filename;

        document.getElementById('outfitName').textContent = data.name;
        document.getElementById('outfitIdTag').textContent = 'ID: ' + data.id;
        document.getElementById('metaDimensions').textContent = data.dimensions[0] + ' × ' + data.dimensions[1];
        document.getElementById('metaFrames').textContent = data.frame_count;
        document.getElementById('metaDuration').textContent = (data.total_duration_ms / 1000).toFixed(1) + 's';
        document.getElementById('metaSize').textContent = formatBytes(data.file_size_bytes);

        document.getElementById('layersCount').textContent = data.layers.length;
        const tbody = document.getElementById('layersBody');
        tbody.innerHTML = '';
        data.layers.forEach(l => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><span class="z-tag">${String(l.z_index).padStart(2, '0')}</span></td>
            <td><strong>${l.category}</strong> ${l.is_default ? '<em style="color:#999; font-size:11px;">(default)</em>' : ''}</td>
            <td>${l.name}</td>
            <td>${l.frame_count}</td>
            <td>${l.cycle_ms}ms</td>
          `;
          tbody.appendChild(tr);
        });

        // Automatically save to favorites history
        addFaveFit({
          id: data.id,
          name: data.name,
          timestamp: Date.now()
        });

        resultSec.style.display = 'grid';
      } catch (err) {
        errBanner.textContent = 'Error: ' + err.message;
        errBanner.style.display = 'block';
      } finally {
        btn.disabled = false;
        loading.style.display = 'none';
      }
    }

    window.addEventListener('DOMContentLoaded', renderHistory);
    renderHistory();
  </script>

</body>
</html>
"""


class OutfitSaverHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep server log clean
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path.startswith("/outputs/"):
            # Serve saved GIF file
            file_name = os.path.basename(parsed.path)
            file_path = os.path.join(OUTPUT_DIR, file_name)
            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/gif")
                self.send_header("Content-Length", str(os.path.getsize(file_path)))
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/generate":
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            try:
                body = json.loads(body_bytes.decode("utf-8"))
                raw_url = body.get("url", "")
                scale = int(body.get("scale", 2))
                bg_mode = body.get("bg_mode", "auto")

                outfit_id = saver.extract_outfit_id(raw_url)
                
                # Output filename
                clean_id = re.sub(r'[^a-zA-Z0-9_-]', '', outfit_id)
                out_filename = f"qqshow_{clean_id}_{scale}x.gif"
                out_filepath = os.path.join(OUTPUT_DIR, out_filename)

                result = saver.composite_outfit(
                    outfit_id=clean_id,
                    output_path=out_filepath,
                    scale=scale,
                    bg_mode=bg_mode,
                )

                # Read output file and convert to data URI for instant web display
                with open(out_filepath, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                data_url = f"data:image/gif;base64,{b64}"

                response_payload = {
                    "id": result["id"],
                    "name": result["name"],
                    "dimensions": result["dimensions"],
                    "scale": result["scale"],
                    "frame_count": result["frame_count"],
                    "total_duration_ms": result["total_duration_ms"],
                    "file_size_bytes": result["file_size_bytes"],
                    "layers": result["layers"],
                    "filename": out_filename,
                    "download_url": f"/outputs/{out_filename}",
                    "gif_data_url": data_url,
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_payload).encode("utf-8"))
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        else:
            self.send_error(404, "Unknown API endpoint")


def run_server(port=PORT):
    server_address = ("", port)
    httpd = HTTPServer(server_address, OutfitSaverHandler)
    print(f"\n=======================================================")
    print(f"✨ QQ Show 2000 Outfit Saver Web UI is running at:")
    print(f"👉 http://localhost:{port}")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
