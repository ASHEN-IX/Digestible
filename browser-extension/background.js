// background.js - Service worker for job polling and notifications

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// Job tracking store
let activeJobs = {};

// Poll every 5 seconds
const POLL_INTERVAL = 5000;

let pollIntervalId = null;

// Start polling loop
function startPollingLoop() {
  if (pollIntervalId) return; // Already running

  pollIntervalId = setInterval(async () => {
    await pollActiveJobs();
  }, POLL_INTERVAL);
}

// Stop polling loop
function stopPollingLoop() {
  if (pollIntervalId) {
    clearInterval(pollIntervalId);
    pollIntervalId = null;
  }
}

// Poll all active jobs
async function pollActiveJobs() {
  const jobIds = Object.keys(activeJobs);

  if (jobIds.length === 0) {
    stopPollingLoop();
    return;
  }

  for (const jobId of jobIds) {
    try {
      await checkJobStatus(jobId);
    } catch (error) {
      console.error(`Error checking job ${jobId}:`, error);
    }
  }
}

// Check individual job status
async function checkJobStatus(jobId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/articles/${jobId}`);

    if (!response.ok) {
      console.error(`Failed to fetch job ${jobId}: ${response.status}`);
      return;
    }

    const data = await response.json();

    // Update local storage with latest data
    await updateLocalArticle(jobId, {
      status: data.status,
      title: data.title,
      summary: data.summary,
      updated_at: new Date().toISOString()
    });

    if (data.status === 'COMPLETED') {
      notifyUser(jobId, data.title || 'Your article', 'completed');
      delete activeJobs[jobId];
    } else if (data.status === 'FAILED') {
      notifyUser(jobId, 'Article processing failed', 'failed');
      delete activeJobs[jobId];
    }
    // Continue polling for other statuses
  } catch (error) {
    console.error(`Error checking job ${jobId}:`, error);
  }
}

// Update article in local storage
async function updateLocalArticle(articleId, updates) {
  try {
    const result = await chrome.storage.local.get(['articles']);
    const articles = result.articles || [];

    const articleIndex = articles.findIndex(a => a.id === articleId);
    if (articleIndex >= 0) {
      articles[articleIndex] = { ...articles[articleIndex], ...updates };
      await chrome.storage.local.set({ articles });

      // Notify popup to refresh
      chrome.runtime.sendMessage({
        type: 'ARTICLE_UPDATED',
        articleId: articleId,
        updates: updates
      });
    }
  } catch (error) {
    console.error('Error updating local article:', error);
  }
}

// Notify user of completion or failure
function notifyUser(jobId, title, status) {
  const notificationId = `digestible-${jobId}`;

  let message, iconUrl;
  if (status === 'completed') {
    message = `${title} has been processed and is ready!`;
    iconUrl = 'icon48.png';
  } else {
    message = 'Failed to process your article. Please try again.';
    iconUrl = 'icon48.png';
  }

  chrome.notifications.create(notificationId, {
    type: 'basic',
    iconUrl: iconUrl,
    title: 'Digestible',
    message: message,
    requireInteraction: false
  });

  // Auto-clear notification after 5 seconds
  setTimeout(() => {
    chrome.notifications.clear(notificationId);
  }, 5000);
}

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'TRACK_JOB' && message.jobId) {
    activeJobs[message.jobId] = true;
    startPollingLoop();
    sendResponse({ success: true });
  }
});

// Restore active jobs on extension restart
chrome.runtime.onStartup.addListener(() => {
  chrome.storage.local.get('activeJobs', (result) => {
    if (result.activeJobs) {
      activeJobs = result.activeJobs;
      if (Object.keys(activeJobs).length > 0) {
        startPollingLoop();
      }
    }
  });
});

// Save active jobs before shutdown
chrome.runtime.onSuspend.addListener(() => {
  chrome.storage.local.set({ activeJobs });
});