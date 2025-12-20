// background.js - Service worker for job polling and notifications

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
    const response = await fetch(`http://localhost:8000/api/v1/articles/${jobId}`);

    if (!response.ok) {
      console.error(`Failed to fetch job ${jobId}: ${response.status}`);
      return;
    }

    const data = await response.json();

    if (data.status === 'COMPLETED') {
      notifyUser(jobId, data.title || 'Your article');
      delete activeJobs[jobId];
    } else if (data.status === 'FAILED') {
      notifyUserFailure(jobId);
      delete activeJobs[jobId];
    }
    // Continue polling for other statuses
  } catch (error) {
    console.error(`Error checking job ${jobId}:`, error);
  }
}

// Notify user of completion
function notifyUser(jobId, title) {
  const notificationId = `digestible-${jobId}`;

  chrome.notifications.create(notificationId, {
    type: 'basic',
    iconUrl: 'icon48.png', // Extension icon
    title: 'Digestible',
    message: `${title} is ready. Click to read or listen.`
  });

  // Handle notification click
  chrome.notifications.onClicked.addListener((clickedId) => {
    if (clickedId === notificationId) {
      chrome.tabs.create({
        url: `http://localhost:8001/articles/${jobId}` // Adjust URL as needed
      });
      chrome.notifications.clear(notificationId);
    }
  });
}

// Notify user of failure
function notifyUserFailure(jobId) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icon48.png',
    title: 'Digestible',
    message: 'Failed to process your article. Please try again.'
  });
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