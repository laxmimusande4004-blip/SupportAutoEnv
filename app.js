// Auto-detect backend URL (works on localhost AND HuggingFace Spaces)
const BASE_URL = window.location.origin;

// DOM Elements
const taskIdEl = document.getElementById('task-id');
const difficultyEl = document.getElementById('difficulty');
const scoreTextEl = document.getElementById('score-text');
const rewardFeedbackEl = document.getElementById('reward-feedback');
const ticketTextEl = document.getElementById('ticket-text');
const resetBtn = document.getElementById('reset-btn');
const demoBtn = document.getElementById('demo-btn');
const stepBtn = document.getElementById('step-btn');
const manualActionEl = document.getElementById('manual-step');
const historyListEl = document.getElementById('history-list');

let currentTaskId = '';
let totalScore = 0;
let tasksCompleted = 0;

// Fetch state on load
async function fetchState() {
    try {
        const response = await fetch(`${BASE_URL}/api`);
        const data = await response.json();
        console.log('Backend connected:', data);
        document.getElementById('env-status').innerHTML = '<span class="pulse"></span> Connected';
    } catch (err) {
        console.error('Failed to connect to backend:', err);
        document.getElementById('env-status').innerHTML = '<span class="pulse" style="background-color: #ef4444; box-shadow: 0 0 10px #ef4444;"></span> Disconnected';
    }
}

// Reset Environment
async function resetEnv() {
    try {
        const response = await fetch(`${BASE_URL}/reset`, { method: 'POST' });
        const obs = await response.json();
        
        currentTaskId = obs.metadata.task_id;
        
        // Update UI
        taskIdEl.textContent = obs.metadata.task_id;
        difficultyEl.textContent = obs.metadata.difficulty;
        ticketTextEl.textContent = obs.ticket_text;
        
        // Clear scores
        scoreTextEl.textContent = '0.0';
        rewardFeedbackEl.textContent = 'Environment reset. Ready for action.';
        
        // Add to history
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `<strong>🔄 Reset</strong> → Task: ${obs.metadata.task_id} (${obs.metadata.difficulty})`;
        historyListEl.prepend(item);
        
        // Style badge based on difficulty
        difficultyEl.className = 'badge ' + obs.metadata.difficulty;
    } catch (err) {
        console.error('Reset failed:', err);
        rewardFeedbackEl.textContent = 'Reset failed. Is the backend running?';
    }
}

// Send Step
async function sendStep(actionData) {
    try {
        const response = await fetch(`${BASE_URL}/step`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(actionData)
        });
        const data = await response.json();
        
        // Update UI
        const score = data.reward.score;
        scoreTextEl.textContent = score.toFixed(2);
        rewardFeedbackEl.textContent = data.reward.feedback;
        
        // Track totals
        totalScore += score;
        tasksCompleted++;
        
        // Color the score
        scoreTextEl.style.color = score >= 0.8 ? '#10b981' : score >= 0.5 ? '#f59e0b' : '#ef4444';
        
        // Add to history
        const item = document.createElement('div');
        item.className = 'history-item';
        const emoji = score >= 0.8 ? '✅' : score >= 0.5 ? '⚠️' : '❌';
        item.innerHTML = `${emoji} <strong>${currentTaskId}</strong>: Score ${score.toFixed(2)}<br><small>${data.reward.feedback}</small>`;
        historyListEl.prepend(item);
        
        return data;
    } catch (err) {
        console.error('Step failed:', err);
        rewardFeedbackEl.textContent = 'Step failed. Check your action JSON.';
    }
}

// Simulate Agent Demo — smart actions based on current task
async function simulateAgent() {
    const taskId = taskIdEl.textContent;
    let action = {};
    
    if (taskId === 'easy_1') {
        action = { "classification": "Billing" };
    } else if (taskId === 'easy_2') {
        action = { "classification": "Account" };
    } else if (taskId === 'easy_3') {
        action = { "classification": "Technical" };
    } else if (taskId === 'medium_1') {
        action = { "order_id": "44551", "sentiment": "Frustrated" };
    } else if (taskId === 'medium_2') {
        action = { "order_id": "78832", "sentiment": "Neutral" };
    } else if (taskId === 'medium_3') {
        action = { "order_id": "91204", "sentiment": "Frustrated" };
    } else if (taskId === 'hard_1') {
        action = { "resolution_steps": ["Apologize sincerely for the damage and inconvenience", "Issue a full refund for the broken blender", "Send a prepaid return label for the damaged item", "Offer a free replacement with expedited shipping"] };
    } else if (taskId === 'hard_2') {
        action = { "resolution_steps": ["Apologize for the double charge and damaged item", "Immediately process a full refund for both charges", "Investigate the billing error with the payments team", "Escalate to a senior manager for review and follow-up"] };
    } else if (taskId === 'hard_3') {
        action = { "resolution_steps": ["Apologize for the unauthorized subscription downgrade", "Restore premium subscription access immediately", "Offer compensation with one month free premium", "Escalate to the subscriptions team for a root cause investigation"] };
    } else {
        alert("Please reset the environment first!");
        return;
    }
    
    // Show what action is being sent
    manualActionEl.value = JSON.stringify(action, null, 2);
    await sendStep(action);
}

// Run All Tasks Demo
async function runAllTasks() {
    demoBtn.disabled = true;
    demoBtn.textContent = 'Running...';
    totalScore = 0;
    tasksCompleted = 0;
    
    for (let i = 0; i < 9; i++) {
        await resetEnv();
        await new Promise(r => setTimeout(r, 300)); // Small delay for UI
        await simulateAgent();
        await new Promise(r => setTimeout(r, 300));
    }
    
    // Show final results
    const avg = totalScore / tasksCompleted;
    rewardFeedbackEl.textContent = `All ${tasksCompleted} tasks done! Average: ${avg.toFixed(2)}`;
    scoreTextEl.textContent = avg.toFixed(2);
    
    demoBtn.disabled = false;
    demoBtn.textContent = 'Simulate Agent';
}

// Event Listeners
resetBtn.addEventListener('click', resetEnv);
demoBtn.addEventListener('click', simulateAgent);
stepBtn.addEventListener('click', () => {
    try {
        const action = JSON.parse(manualActionEl.value);
        sendStep(action);
    } catch (err) {
        alert('Invalid JSON in manual action box.');
    }
});

// Init
fetchState();
resetEnv();
