let charts = {};

function initCharts() {
    Chart.defaults.color = '#8b949e';
    Chart.defaults.font.family = 'Inter';
    
    const markupCtx = document.getElementById('markupChart').getContext('2d');
    charts.markup = new Chart(markupCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], borderColor: '#58a6ff' }] },
        options: {
            animation: {
                duration: 800
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { 
                    title: { display: true, text: 'Average Markup (%)' },
                    grid: { color: 'rgba(48, 54, 61, 0.5)' }
                },
                x: { 
                    title: { display: true, text: 'Episodes' },
                    grid: { display: false },
                    ticks: { maxTicksLimit: 8 }
                }
            }
        }
    });

    const profitCtx = document.getElementById('profitChart').getContext('2d');
    charts.profit = new Chart(profitCtx, {
        type: 'line',
        data: { labels: [], datasets: [{ data: [], borderColor: '#2ea043' }] },
        options: {
            animation: {
                duration: 800
            },
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { 
                    title: { display: true, text: 'Moving Average Profit' },
                    grid: { color: 'rgba(48, 54, 61, 0.5)' }
                },
                x: { 
                    title: { display: true, text: 'Episodes' },
                    grid: { display: false },
                    ticks: { maxTicksLimit: 8 }
                }
            }
        }
    });

    const qCtx = document.getElementById('qChart').getContext('2d');
    charts.qValues = new Chart(qCtx, {
        type: 'line',
        data: { labels: [], datasets: [] },
        options: {
            animation: {
                duration: 800
            },
            responsive: true,
            maintainAspectRatio: false,
            elements: { point: { radius: 2, hitRadius: 10, hoverRadius: 5 } },
            interaction: { mode: 'index', intersect: false },
            scales: {
                y: { 
                    title: { display: true, text: 'Expected Q-Value' },
                    grid: { color: 'rgba(48, 54, 61, 0.5)' }
                },
                x: { 
                    title: { display: true, text: 'Markup Actions' },
                    grid: { color: 'rgba(48, 54, 61, 0.5)' },
                    ticks: {
                        callback: function(value, index, ticks) {
                            return this.getLabelForValue(value) + '%';
                        }
                    }
                }
            }
        }
    });
}

function updateCharts(data) {
    // Update Markup Chart
    const ep_labels = data.episodes;
    
    charts.markup.data = {
        labels: ep_labels,
        datasets: [{
            label: 'Avg Markup Strategy',
            data: data.markups.map(v => v * 100),
            borderColor: '#58a6ff',
            backgroundColor: 'rgba(88, 166, 255, 0.15)',
            fill: true,
            tension: 0.2,
            pointRadius: 0
        }]
    };
    charts.markup.update();

    // Update Profit Chart
    charts.profit.data = {
        labels: ep_labels,
        datasets: [{
            label: 'Avg Rolling Profit',
            data: data.profits,
            borderColor: '#2ea043',
            backgroundColor: 'rgba(46, 160, 67, 0.15)',
            fill: true,
            tension: 0.2,
            pointRadius: 0
        }]
    };
    charts.profit.update();

    // Update Q-Value Chart
    const qDatasets = [];
    // Deep dark theme friendly colors
    const colors = ['#f85149', '#58a6ff', '#3fb950', '#d29922', '#bc8cff', '#ffa657', '#ff7b72', '#a5d6ff', '#7ee787', '#e3b341'];
    
    let agentKeys = Object.keys(data.q_values);
    agentKeys.forEach((agent, index) => {
        qDatasets.push({
            label: 'Contractor ' + agent.split('_')[1],
            data: data.q_values[agent],
            borderColor: colors[index % colors.length],
            borderWidth: 2,
            tension: 0.3,
            backgroundColor: 'transparent'
        });
    });

    charts.qValues.data = {
        labels: data.markup_actions.map(m => (m * 100).toFixed(0)),
        datasets: qDatasets
    };
    charts.qValues.update();
}

async function runSimulation(e) {
    if(e) e.preventDefault();
    
    const btn = document.getElementById('sim-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('btn-spinner');
    
    btn.disabled = true;
    btnText.textContent = 'Learning...';
    spinner.classList.remove('hidden');
    
    const params = {
        auction_type: document.getElementById('auctionType').value,
        num_contractors: parseInt(document.getElementById('numContractors').value),
        episodes: parseInt(document.getElementById('episodes').value),
        min_cost: parseFloat(document.getElementById('minCost').value),
        max_cost: parseFloat(document.getElementById('maxCost').value)
    };

    try {
        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) throw new Error('Simulation failed');
        const data = await response.json();
        
        updateCharts(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to simulation backend. Make sure the server is running.');
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Run Simulation';
        spinner.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    document.getElementById('sim-form').addEventListener('submit', runSimulation);
    // Optionally trigger a default run
    runSimulation();
});
