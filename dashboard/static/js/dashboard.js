// Digestible Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
 // Initialize dashboard
 loadArticles();
 loadStats();

 // Article submission form
 const articleForm = document.getElementById('article-form');
 if (articleForm) {
  articleForm.addEventListener('submit', submitArticle);
 }
});

async function submitArticle(event) {
 event.preventDefault();

 const urlInput = document.getElementById('article-url');
 const submitBtn = document.getElementById('submit-btn');
 const spinner = submitBtn.querySelector('.spinner-border');

 const url = urlInput.value.trim();
 if (!url) return;

 // Show loading state
 submitBtn.disabled = true;
 spinner.classList.remove('d-none');

 try {
  const response = await fetch('/api/articles/', {
   method: 'POST',
   headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken(),
   },
   body: JSON.stringify({ url: url }),
  });

  const data = await response.json();

  if (response.ok) {
   showAlert('Article submitted successfully!', 'success');
   urlInput.value = '';
   loadArticles(); // Refresh articles list
  } else {
   showAlert(data.error || 'Failed to submit article', 'danger');
  }
 } catch (error) {
  console.error('Error:', error);
  showAlert('Network error. Please try again.', 'danger');
 } finally {
  submitBtn.disabled = false;
  spinner.classList.add('d-none');
 }
}

async function loadArticles() {
 const container = document.getElementById('articles-container');
 if (!container) return;

 try {
  const response = await fetch('/api/articles/');
  const data = await response.json();

  if (response.ok && data.results) {
   renderArticles(data.results);
  } else {
   container.innerHTML = '<p class="text-muted">No articles found.</p>';
  }
 } catch (error) {
  console.error('Error loading articles:', error);
  container.innerHTML = '<p class="text-danger">Error loading articles.</p>';
 }
}

async function loadStats() {
 try {
  const response = await fetch('/api/articles/stats/');
  const stats = await response.json();

  document.getElementById('total-count').textContent = stats.total || 0;
  document.getElementById('completed-count').textContent = stats.completed || 0;
 } catch (error) {
  console.error('Error loading stats:', error);
 }
}

function renderArticles(articles) {
 const container = document.getElementById('articles-container');

 if (articles.length === 0) {
  container.innerHTML = '<p class="text-muted">No articles yet. Submit your first article above!</p>';
  return;
 }

 const html = articles.map(article => `
  <div class="card article-card mb-3">
   <div class="card-body">
    <div class="d-flex justify-content-between align-items-start">
     <div class="flex-grow-1">
      <h5 class="card-title">
       ${article.title || 'Processing...'}
      </h5>
      <p class="card-text text-muted small">${article.url}</p>
      ${article.summary ? `<p class="card-text">${article.summary.substring(0, 200)}...</p>` : ''}
     </div>
     <span class="badge status-badge status-${article.status.toLowerCase()} ms-2">
      ${article.status}
     </span>
    </div>
    <div class="mt-2">
     <small class="text-muted">
      Created: ${new Date(article.created_at).toLocaleDateString()}
      ${article.completed_at ? ` | Completed: ${new Date(article.completed_at).toLocaleDateString()}` : ''}
     </small>
    </div>
   </div>
  </div>
 `).join('');

 container.innerHTML = html;
}

function showAlert(message, type = 'info') {
 const alertDiv = document.createElement('div');
 alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
 alertDiv.innerHTML = `
  ${message}
  <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
 `;

 const container = document.querySelector('.container');
 container.insertBefore(alertDiv, container.firstChild);

 // Auto-dismiss after 5 seconds
 setTimeout(() => {
  alertDiv.remove();
 }, 5000);
}

function getCsrfToken() {
 const token = document.querySelector('[name=csrfmiddlewaretoken]');
 return token ? token.value : '';
}