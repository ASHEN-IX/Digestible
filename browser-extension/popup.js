// popup.js - Enhanced browser extension for Digestible

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM elements
let articlesList, articleModal, articleDetail, closeBtn, articleCount;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Get DOM elements
  const form = document.getElementById('submit-form');
  const urlInput = document.getElementById('article-url');
  const submitBtn = document.getElementById('submit-btn');
  const submitStatus = document.getElementById('submit-status');
  articlesList = document.getElementById('articles-list');
  articleModal = document.getElementById('article-modal');
  articleDetail = document.getElementById('article-detail');
  closeBtn = document.querySelector('.close');
  articleCount = document.getElementById('article-count');

  // Pre-fill with current tab URL
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    if (tabs[0] && tabs[0].url) {
      urlInput.value = tabs[0].url;
    }
  });

  // Load and display saved articles
  loadArticles();

  // Handle form submission
  form.addEventListener('submit', handleSubmit);

  // Handle modal close
  closeBtn.addEventListener('click', () => {
    articleModal.style.display = 'none';
  });

  // Close modal when clicking outside
  window.addEventListener('click', (event) => {
    if (event.target === articleModal) {
      articleModal.style.display = 'none';
    }
  });
});

// Handle article submission
async function handleSubmit(e) {
  e.preventDefault();

  const url = document.getElementById('article-url').value.trim();
  if (!url) return;

  const submitBtn = document.getElementById('submit-btn');
  const submitStatus = document.getElementById('submit-status');

  submitBtn.disabled = true;
  submitBtn.textContent = '💾 Saving...';
  submitStatus.textContent = '';

  try {
    // Submit to backend API
    const response = await fetch(`${API_BASE_URL}/api/v1/articles`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    });

    if (response.ok) {
      const data = await response.json();

      // Create local article record
      const article = {
        id: data.id,
        url: url,
        status: 'PENDING',
        created_at: new Date().toISOString(),
        title: 'Processing...',
        summary: 'Article is being processed...'
      };

      // Save to local storage
      await saveArticleLocally(article);

      submitStatus.textContent = '✅ Article saved! Processing in background...';
      submitStatus.className = 'status success';

      // Start tracking in background
      chrome.runtime.sendMessage({
        type: "TRACK_JOB",
        jobId: data.id
      });

      // Refresh articles list
      loadArticles();

      // Clear form
      document.getElementById('article-url').value = '';

      // Close popup after success
      setTimeout(() => window.close(), 2000);

    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch (error) {
    console.error('Submission error:', error);
    console.log('API Base URL:', API_BASE_URL);
    console.log('Error details:', error.message);
    submitStatus.textContent = `❌ Error: ${error.message}`;
    submitStatus.className = 'status error';
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = '💾 Save Article';
  }
}

// Load articles from local storage
async function loadArticles() {
  try {
    const result = await chrome.storage.local.get(['articles']);
    const articles = result.articles || [];

    // Update count
    articleCount.textContent = `(${articles.length})`;

    if (articles.length === 0) {
      articlesList.innerHTML = '<div class="empty-state">No articles saved yet. Save your first article above!</div>';
      return;
    }

    // Sort by creation date (newest first)
    articles.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    // Render articles
    articlesList.innerHTML = articles.map(article => `
      <div class="article-item" data-id="${article.id}">
        <div class="article-header">
          <h3 class="article-title">${article.title || 'Processing...'}</h3>
          <span class="article-status status-${article.status.toLowerCase()}">${article.status}</span>
        </div>
        <div class="article-url">${article.url}</div>
        <div class="article-date">${formatDate(article.created_at)}</div>
      </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.article-item').forEach(item => {
      item.addEventListener('click', () => showArticleDetail(item.dataset.id));
    });

  } catch (error) {
    console.error('Error loading articles:', error);
    articlesList.innerHTML = '<div class="error">Error loading articles</div>';
  }
}

// Save article to local storage
async function saveArticleLocally(article) {
  try {
    const result = await chrome.storage.local.get(['articles']);
    const articles = result.articles || [];

    // Check if article already exists
    const existingIndex = articles.findIndex(a => a.id === article.id);
    if (existingIndex >= 0) {
      articles[existingIndex] = { ...articles[existingIndex], ...article };
    } else {
      articles.push(article);
    }

    await chrome.storage.local.set({ articles });
  } catch (error) {
    console.error('Error saving article:', error);
  }
}

// Update article in local storage
async function updateArticleLocally(articleId, updates) {
  try {
    const result = await chrome.storage.local.get(['articles']);
    const articles = result.articles || [];

    const articleIndex = articles.findIndex(a => a.id === articleId);
    if (articleIndex >= 0) {
      articles[articleIndex] = { ...articles[articleIndex], ...updates };
      await chrome.storage.local.set({ articles });
      loadArticles(); // Refresh display
    }
  } catch (error) {
    console.error('Error updating article:', error);
  }
}

// Show article detail in modal
async function showArticleDetail(articleId) {
  try {
    const result = await chrome.storage.local.get(['articles']);
    const articles = result.articles || [];
    const article = articles.find(a => a.id === articleId);

    if (!article) return;

    articleDetail.innerHTML = `
      <h2>${article.title || 'Processing...'}</h2>
      <div class="article-meta">
        <strong>URL:</strong> <a href="${article.url}" target="_blank">${article.url}</a><br>
        <strong>Status:</strong> <span class="status-${article.status.toLowerCase()}">${article.status}</span><br>
        <strong>Saved:</strong> ${formatDate(article.created_at)}
      </div>
      <div class="article-summary">
        <h3>Summary</h3>
        <div class="summary-content">${article.summary || 'Article is being processed...'}</div>
      </div>
      ${article.status === 'COMPLETED' ? `<div class="article-actions">
        <button id="read-original-btn" data-url="${article.url}">📖 Read Original</button>
        <button id="play-audio-btn" data-article-id="${articleId}">🔊 Play Audio Summary</button>
        <audio id="article-audio" controls style="width: 100%; margin-top: 10px; display: none;"></audio>
      </div>` : ''}
    `;

    // Add event listeners
    const readBtn = document.getElementById('read-original-btn');
    if (readBtn) {
      readBtn.addEventListener('click', () => {
        chrome.tabs.create({ url: article.url });
      });
    }

    const playBtn = document.getElementById('play-audio-btn');
    const audioElement = document.getElementById('article-audio');
    if (playBtn && audioElement) {
      playBtn.addEventListener('click', async () => {
        try {
          // Set audio source to the API endpoint
          audioElement.src = `${API_BASE_URL}/api/v1/articles/${articleId}/audio`;
          audioElement.style.display = 'block';
          audioElement.play();

          // Update button text
          playBtn.textContent = '🔊 Playing...';
          playBtn.disabled = true;

          // Re-enable button when audio ends
          audioElement.addEventListener('ended', () => {
            playBtn.textContent = '🔊 Play Audio Summary';
            playBtn.disabled = false;
          });

        } catch (error) {
          console.error('Error playing audio:', error);
          playBtn.textContent = '❌ Audio Error';
        }
      });
    }

    articleModal.style.display = 'block';

  } catch (error) {
    console.error('Error showing article detail:', error);
  }
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// Listen for updates from background script
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'ARTICLE_UPDATED') {
    updateArticleLocally(message.articleId, message.updates);
  }
});