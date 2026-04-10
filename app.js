const BASE_URL = 'http://localhost:8000';

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

let currentTaskIdx = 0;

// Fetch state on load
async function fetchState() {
    try {
        const response = await fetch(`${BASE_URL}/`);
        const data = await response.json();
        console.log('Backend connected:', data);
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
        
        // Update UI
        taskIdEl.textContent = obs.metadata.task_id;
        difficultyEl.textContent = obs.metadata.difficulty;
        ticketTextEl.textContent = obs.ticket_text;
        
        // Clear history and scores
        scoreTextEl.textContent = '0.0';
        rewardFeedbackEl.textContent = 'Environment reset.';
        historyListEl.innerHTML = '<div class="history-item">Environment Reset</div>';
        
        // Style badge based on difficulty
        difficultyEl.className = 'badge ' + obs.metadata.difficulty;
    } catch (err) {
        console.error('Reset failed:', err);
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
        scoreTextEl.textContent = data.reward.score.toFixed(1);
        rewardFeedbackEl.textContent = data.reward.feedback;
        
        // Add to history
        const item = document.createElement('div');
        item.className = 'history-item';
        item.innerHTML = `<strong>Action:</strong> ${JSON.stringify(actionData).substring(0, 50)}... <br> <strong>Result:</strong> Score ${data.reward.score}`;
        historyListEl.prepend(item);
        
        return data;
    } catch (err) {
        console.error('Step failed:', err);
    }
}

// Simulate Agent Demo
async function simulateAgent() {
    const taskId = taskIdEl.textContent;
    let action = {};
    
    if (taskId.includes('easy')) {
        action = { "classification": "Billing" };
    } else if (taskId.includes('medium')) {
        action = { "order_id": "44551", "sentiment": "Frustrated" };
    } else if (taskId.includes('hard')) {
        action = { "resolution_steps": ["Apologize for the damage", "Issue a full refund", "Provide a return label"] };
    } else {
        alert("Please reset the environment first!");
        return;
    }
    
    await sendStep(action);
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
