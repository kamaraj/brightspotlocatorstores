// Dashboard JavaScript

// Global variables
let currentResults = null;
let timingChart = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    initializeEventListeners();
    initializeSidebarToggle();
});

// Initialize all event listeners
function initializeEventListeners() {
    // Form submission
    document.getElementById('analysisForm').addEventListener('submit', handleFormSubmit);

    // Sample address buttons
    document.querySelectorAll('.sample-address').forEach(button => {
        button.addEventListener('click', function () {
            document.getElementById('address').value = this.dataset.address;
        });
    });

    // Export buttons
    document.getElementById('exportJSON')?.addEventListener('click', exportJSON);
    document.getElementById('exportCSV')?.addEventListener('click', exportCSV);
    document.getElementById('printReport')?.addEventListener('click', () => window.print());
}

// Initialize sidebar toggle functionality
function initializeSidebarToggle() {
    const toggleBtn = document.getElementById('sidebarToggle');
    const closeBtn = document.getElementById('sidebarClose');
    const sidebar = document.getElementById('sidebarPanel');
    const mainContent = document.getElementById('mainContent');

    // Create overlay for mobile
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.id = 'sidebarOverlay';
    document.body.appendChild(overlay);

    // Toggle sidebar
    function toggleSidebar() {
        const isMobile = window.innerWidth < 992;

        if (isMobile) {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        } else {
            const isCollapsed = sidebar.classList.contains('collapsed');

            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');

            // Update button icon and position
            const icon = toggleBtn.querySelector('i');
            if (!isCollapsed) {
                // Collapsing - change to right arrow
                icon.className = 'bi bi-chevron-right';
                // Position at far left
                setTimeout(() => {
                    toggleBtn.style.left = '20px';
                }, 100);
            } else {
                // Expanding - change to left arrow
                icon.className = 'bi bi-chevron-left';
                // Position back to original
                toggleBtn.style.left = '20px';
            }
        }
    }

    // Close sidebar
    function closeSidebar() {
        const isMobile = window.innerWidth < 992;

        if (isMobile) {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        } else {
            if (!sidebar.classList.contains('collapsed')) {
                sidebar.classList.add('collapsed');
                mainContent.classList.add('expanded');

                const icon = toggleBtn.querySelector('i');
                icon.className = 'bi bi-chevron-right';
                toggleBtn.style.left = '20px';
            }
        }
    }

    // Event listeners
    toggleBtn.addEventListener('click', toggleSidebar);
    closeBtn.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);

    // Handle window resize
    let resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
            const isMobile = window.innerWidth < 992;
            if (!isMobile) {
                overlay.classList.remove('show');
                sidebar.classList.remove('show');
            } else {
                // Reset desktop states on mobile
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
            }
        }, 250);
    });
}

// Handle form submission
async function handleFormSubmit(e) {
    e.preventDefault();

    const address = document.getElementById('address').value.trim();
    const radius = parseFloat(document.getElementById('radius').value);

    if (!address) {
        showError('Please enter an address');
        return;
    }

    // Show loading state
    showLoading(true);
    hideError();

    try {
        // Call API
        const response = await fetch('/api/v1/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                address: address,
                radius_miles: radius
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        currentResults = data;

        // Display results
        displayResults(data);

    } catch (error) {
        console.error('Analysis error:', error);

        // Try to extract detailed error message
        let errorMessage = error.message;
        if (error.message.includes('400')) {
            try {
                const errorData = await response.json();
                if (errorData.detail) {
                    if (typeof errorData.detail === 'object') {
                        errorMessage = errorData.detail.message || errorData.detail.error || 'Invalid address';
                        if (errorData.detail.suggestions) {
                            errorMessage += `\n\n${errorData.detail.suggestions}`;
                        }
                    } else {
                        errorMessage = errorData.detail;
                    }
                }
            } catch (e) {
                // Keep original error message
            }
        }

        showError(`Failed to analyze location: ${errorMessage}`);
    } finally {
        showLoading(false);
    }
}

// Display analysis results
function displayResults(data) {
    // Check for error in response
    if (data.error) {
        showError(`Analysis failed: ${data.error}`);
        // Still show results container with error state
    }

    // Hide welcome message, show results
    document.getElementById('welcomeMessage').classList.add('d-none');
    document.getElementById('resultsContainer').classList.remove('d-none');

    // Update overall score
    const overallScore = data.overall_score || 0;
    document.getElementById('overallScore').textContent = overallScore.toFixed(1);

    // Show corrected address if different from original
    const addressElement = document.getElementById('analyzedAddress');
    if (data.address_validation && data.address_validation.corrected) {
        addressElement.innerHTML = `
            <span class="text-muted small">Original:</span> ${data.original_address}<br>
            <span class="text-success small"><i class="bi bi-check-circle-fill"></i> Corrected:</span> ${data.address}
        `;
    } else {
        addressElement.textContent = data.address || 'Unknown Location';
    }

    document.getElementById('analysisTimestamp').querySelector('span').textContent =
        new Date(data.analysis_timestamp || data.timestamp).toLocaleString();

    // Update progress bar
    updateProgressBar(overallScore);

    // Update recommendation
    updateRecommendation(overallScore, data.recommendation);

    // Update performance metrics
    updatePerformanceMetrics(data);

    // Update category scores
    if (data.categories) {
        updateCategoryScores(data.categories);
        // Update detailed tabs with XAI
        updateDetailedTabs(data.categories);
    } else {
        console.warn('No category data available in results');
    }

    // Update timing chart - handle both old and new formats
    const performanceReport = data.performance_report ||
        (data.performance && data.performance.collection_breakdown ? data.performance.collection_breakdown : null);
    updateTimingChart(performanceReport);

    // Scroll to results
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
}

// Update progress bar
function updateProgressBar(score) {
    const progressBar = document.getElementById('overallProgressBar');
    const progressText = document.getElementById('overallProgressText');

    progressBar.style.width = `${score}%`;
    progressBar.setAttribute('aria-valuenow', score);
    progressText.textContent = `${score.toFixed(1)}/100`;

    // Set color based on score
    progressBar.className = 'progress-bar';
    if (score >= 75) {
        progressBar.classList.add('bg-success');
    } else if (score >= 60) {
        progressBar.classList.add('bg-info');
    } else if (score >= 45) {
        progressBar.classList.add('bg-warning');
    } else {
        progressBar.classList.add('bg-danger');
    }
}

// Update recommendation badge and text
function updateRecommendation(score, recommendation) {
    const badge = document.getElementById('recommendationBadge');
    const text = document.getElementById('recommendationText');

    let badgeClass = 'badge ';
    let badgeText = '';
    let recommendationText = recommendation || '';

    if (score >= 75) {
        badgeClass += 'bg-success';
        badgeText = 'EXCELLENT ⭐⭐⭐⭐⭐';
    } else if (score >= 60) {
        badgeClass += 'bg-info';
        badgeText = 'GOOD ⭐⭐⭐⭐';
    } else if (score >= 45) {
        badgeClass += 'bg-warning';
        badgeText = 'FAIR ⭐⭐⭐';
    } else {
        badgeClass += 'bg-danger';
        badgeText = 'POOR ⭐⭐';
    }

    badge.className = badgeClass;
    badge.textContent = badgeText;
    text.textContent = recommendationText;
}

// Update performance metrics
function updatePerformanceMetrics(data) {
    // Handle both old and new field names
    const totalTimeMs = data.total_analysis_time_ms ||
        (data.performance && data.performance.total_time_seconds ? data.performance.total_time_seconds * 1000 : 0);
    const dataPoints = data.data_points_collected || 66;
    const successRate = data.performance_report ?
        `${data.performance_report.successful_steps}/${data.performance_report.steps_count}` :
        (data.performance && data.performance.collection_breakdown ?
            `${data.performance.collection_breakdown.successful_steps}/${data.performance.collection_breakdown.steps_count}` : '--');

    document.getElementById('totalTime').textContent = totalTimeMs.toFixed(2);
    document.getElementById('dataPoints').textContent = dataPoints;
    document.getElementById('successRate').textContent = successRate;
}

// Update category scores
function updateCategoryScores(categories) {
    const container = document.getElementById('categoryScores');
    container.innerHTML = '';

    const categoryInfo = {
        demographics: { icon: 'bi-people-fill', color: 'primary', name: 'Demographics', points: 15 },
        competition: { icon: 'bi-buildings', color: 'success', name: 'Competition', points: 12 },
        accessibility: { icon: 'bi-car-front-fill', color: 'info', name: 'Accessibility', points: 10 },
        safety: { icon: 'bi-shield-check-fill', color: 'warning', name: 'Safety', points: 11 },
        economic: { icon: 'bi-currency-dollar', color: 'danger', name: 'Economic', points: 10 },
        regulatory: { icon: 'bi-file-text-fill', color: 'secondary', name: 'Regulatory', points: 8 }
    };

    if (!categories) return;
    for (const [key, category] of Object.entries(categories)) {
        const info = categoryInfo[key];
        if (!info) continue;

        const score = category.score || 0;
        const collectionTime = category.collection_time_ms || 0;

        const card = `
            <div class="col-md-4 mb-3">
                <div class="card category-score-card score-card ${getScoreClass(score)}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="mb-0">
                                <i class="bi ${info.icon} text-${info.color}"></i> 
                                ${info.name}
                            </h6>
                            <span class="badge bg-${info.color}">${info.points} pts</span>
                        </div>
                        <h2 class="mb-0">${score.toFixed(1)}/100</h2>
                        <div class="progress mt-2" style="height: 8px;">
                            <div class="progress-bar bg-${info.color}" role="progressbar" 
                                 style="width: ${score}%;" aria-valuenow="${score}" 
                                 aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <small class="text-muted mt-2 d-block">
                            <i class="bi bi-clock"></i> ${collectionTime.toFixed(2)} ms
                        </small>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML += card;
    }
}

// Get score class based on value
function getScoreClass(score) {
    if (score >= 75) return 'score-excellent';
    if (score >= 60) return 'score-good';
    if (score >= 45) return 'score-fair';
    return 'score-poor';
}

// Update detailed tabs
function updateDetailedTabs(categories) {
    console.log("updateDetailedTabs called with categories:", categories);
    for (const [key, category] of Object.entries(categories)) {
        console.log(`Processing category ${key}:`, category);
        const tabContent = document.getElementById(key);
        if (!tabContent) {
            console.log(`Tab content for ${key} not found`);
            continue;
        }

        const categoryName = key.charAt(0).toUpperCase() + key.slice(1);
        const score = category.score || 0;
        const collectionTime = category.collection_time_ms || 0;
        const metricsCount = category.metrics_count || 0;
        console.log(`${key} - metricsCount from backend:`, metricsCount);

        // Get data source details for transparency
        const dataSourceDetails = category.data_source_details || {};
        const overallType = dataSourceDetails.overall_type || 'unknown';
        const accuracy = dataSourceDetails.accuracy || 'unknown';
        const metricsSourceInfo = dataSourceDetails.metrics || {};

        // Get data point keys (excluding metadata and _explanation keys)
        const excludeKeys = ['success', 'address', 'coordinates', 'data_source', 'note',
            'jurisdiction', 'state', 'centers_details', 'radius_miles',
            'search_radius_miles', 'centers_analyzed', 'total_population',
            'land_area_sqmi', 'score', 'collection_time_ms', 'metrics_count',
            'explanation', 'error', 'metrics', 'data_source_details'];
        const dataPoints = Object.keys(category).filter(k =>
            !excludeKeys.includes(k) && !k.endsWith('_explanation'));
        console.log(`${key} - dataPoints filtered:`, dataPoints);

        // Generate data source badge HTML
        const dataSourceBadge = getDataSourceBadge(overallType, accuracy);

        let html = `
            <!-- Category Header -->
            <div class="alert alert-info border-start border-5 mb-4">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h4 class="mb-2"><i class="bi ${getCategoryIcon(key)}"></i> ${categoryName} Analysis</h4>
                        <p class="mb-1"><strong>Category Score:</strong> <span class="badge bg-primary">${score.toFixed(1)}/100</span></p>
                        <p class="mb-1"><strong>Data Points Collected:</strong> ${metricsCount} metrics</p>
                        <p class="mb-1"><strong>Collection Time:</strong> ${collectionTime.toFixed(2)}ms</p>
                        <p class="mb-0"><strong>Data Quality:</strong> ${dataSourceBadge}</p>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="circular-progress" style="width: 120px; height: 120px; margin: 0 auto;">
                            <svg viewBox="0 0 120 120">
                                <circle cx="60" cy="60" r="54" fill="none" stroke="#e9ecef" stroke-width="8"/>
                                <circle cx="60" cy="60" r="54" fill="none" stroke="${getScoreColor(score)}" 
                                        stroke-width="8" stroke-dasharray="${(score / 100) * 339.292} 339.292" 
                                        transform="rotate(-90 60 60)" stroke-linecap="round"/>
                                <text x="60" y="65" text-anchor="middle" font-size="24" font-weight="bold" fill="${getScoreColor(score)}">
                                    ${score.toFixed(0)}
                                </text>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- XAI Toggle Button -->
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0">📊 Detailed Metrics</h5>
                <div>
                    <button class="btn btn-sm btn-outline-secondary me-2" onclick="toggleDataSourceView('${key}')">
                        <i class="bi bi-database"></i> <span id="ds-toggle-${key}">Show</span> Data Sources
                    </button>
                    <button class="btn btn-sm btn-outline-primary" onclick="toggleXAIView('${key}')">
                        <i class="bi bi-lightbulb"></i> <span id="xai-toggle-${key}">Show</span> AI Explanations
                    </button>
                </div>
            </div>
            
            <!-- Data Points with XAI -->
            <div class="row">
        `;

        // Render each data point as a card with XAI
        for (const dataKey of dataPoints) {
            const value = category[dataKey];
            const displayName = dataKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            const displayValue = formatValue(value);

            // Get metric-level data source info
            const metricSource = metricsSourceInfo[dataKey] || {};
            const metricType = metricSource.type || 'unknown';
            const metricSourceName = metricSource.source || 'Unknown';
            const metricNote = metricSource.note || '';
            const metricBadge = getMetricSourceBadge(metricType);

            // Get XAI explanation from backend response or use frontend fallback
            const backendXai = category[`${dataKey}_explanation`];
            const xai = backendXai && backendXai.explanation ? {
                what: backendXai.explanation.what || 'Data metric for analysis',
                how: backendXai.explanation.how || 'Calculated from data sources',
                why: backendXai.explanation.why || 'Contributes to location assessment',
                where: backendXai.explanation.source || 'Data sources',
                when: 'Real-time or recent data',
                source: backendXai.explanation.source || 'Multiple sources',
                confidence: backendXai.explanation.confidence || 'MEDIUM',
                interpretation: backendXai.interpretation || 'See details'
            } : getXAIForDataPoint(key, dataKey, value);

            html += `
                <div class="col-md-6 mb-3">
                    <div class="card h-100 data-point-card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="card-title mb-0">${displayName}</h6>
                                <div>
                                    <span class="badge ${getValueBadgeClass(xai.interpretation)}">${xai.interpretation}</span>
                                </div>
                            </div>
                            <h3 class="text-primary mb-3">${displayValue}</h3>
                            
                            <!-- Data Source Badge (hidden by default) -->
                            <div class="ds-content ds-content-${key}" style="display: none;">
                                <div class="alert alert-light py-2 px-3 mb-0">
                                    <div class="d-flex align-items-center">
                                        ${metricBadge}
                                        <small class="ms-2">${metricSourceName}</small>
                                    </div>
                                    ${metricNote ? `<small class="text-muted d-block mt-1">ℹ️ ${metricNote}</small>` : ''}
                                </div>
                            </div>
                            
                            <!-- XAI Section (hidden by default) -->
                            <div class="xai-content xai-content-${key}" style="display: none;">
                                <hr class="my-3">
                                <div class="xai-details">
                                    <div class="mb-2">
                                        <strong><i class="bi bi-question-circle"></i> What:</strong>
                                        <p class="small mb-0 ms-4">${xai.what}</p>
                                    </div>
                                    <div class="mb-2">
                                        <strong><i class="bi bi-gear"></i> How:</strong>
                                        <p class="small mb-0 ms-4"><code>${xai.how}</code></p>
                                    </div>
                                    <div class="mb-2">
                                        <strong><i class="bi bi-lightbulb"></i> Why:</strong>
                                        <p class="small mb-0 ms-4">${xai.why}</p>
                                    </div>
                                    <div class="mb-2">
                                        <strong><i class="bi bi-search"></i> Where:</strong>
                                        <p class="small mb-0 ms-4">${xai.where}</p>
                                    </div>
                                    <div class="mb-0">
                                        <strong><i class="bi bi-clock-history"></i> When:</strong>
                                        <p class="small mb-0 ms-4">${xai.when}</p>
                                    </div>
                                    <hr class="my-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">
                                            <strong>Source:</strong> ${xai.source}
                                        </small>
                                        <span class="badge ${getConfidenceBadgeClass(xai.confidence)}">${xai.confidence}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        html += `
            </div>
            
            <!-- Category Summary -->
            <div class="card bg-light mt-4">
                <div class="card-body">
                    <h5><i class="bi bi-bar-chart"></i> Category Summary</h5>
                    <p class="mb-0">${getCategorySummary(key, score, metricsCount)}</p>
                </div>
            </div>
        `;

        tabContent.innerHTML = html;
    }
}

// Toggle XAI view for a category
function toggleXAIView(category) {
    const xaiElements = document.querySelectorAll(`.xai-content-${category}`);
    const toggleText = document.getElementById(`xai-toggle-${category}`);

    xaiElements.forEach(el => {
        if (el.style.display === 'none') {
            el.style.display = 'block';
            toggleText.textContent = 'Hide';
        } else {
            el.style.display = 'none';
            toggleText.textContent = 'Show';
        }
    });
}

// Toggle Data Source view for a category
function toggleDataSourceView(category) {
    const dsElements = document.querySelectorAll(`.ds-content-${category}`);
    const toggleText = document.getElementById(`ds-toggle-${category}`);

    dsElements.forEach(el => {
        if (el.style.display === 'none') {
            el.style.display = 'block';
            toggleText.textContent = 'Hide';
        } else {
            el.style.display = 'none';
            toggleText.textContent = 'Show';
        }
    });
}

// Get data source badge for category header
function getDataSourceBadge(type, accuracy) {
    const typeInfo = {
        'real_api': { icon: '✅', label: 'Real API Data', class: 'bg-success' },
        'mixed': { icon: '⚠️', label: 'Mixed (Real + Estimated)', class: 'bg-warning text-dark' },
        'estimated': { icon: '📊', label: 'Estimated/Proxy', class: 'bg-secondary' },
        'proxy': { icon: '🔄', label: 'Proxy Data', class: 'bg-info' },
        'unknown': { icon: '❓', label: 'Unknown', class: 'bg-dark' }
    };

    const accuracyInfo = {
        'high': { label: 'High Accuracy', class: 'bg-success' },
        'moderate': { label: 'Moderate Accuracy', class: 'bg-warning text-dark' },
        'low': { label: 'Low Accuracy', class: 'bg-danger' },
        'unknown': { label: '', class: '' }
    };

    const t = typeInfo[type] || typeInfo['unknown'];
    const a = accuracyInfo[accuracy] || accuracyInfo['unknown'];

    return `<span class="badge ${t.class} me-1">${t.icon} ${t.label}</span>` +
        (a.label ? `<span class="badge ${a.class}">${a.label}</span>` : '');
}

// Get metric-level source badge
function getMetricSourceBadge(type) {
    const badges = {
        'real_api': '<span class="badge bg-success">✅ Real API</span>',
        'derived': '<span class="badge bg-info">📐 Derived</span>',
        'estimated': '<span class="badge bg-warning text-dark">📊 Estimated</span>',
        'proxy': '<span class="badge bg-secondary">🔄 Proxy</span>',
        'unknown': '<span class="badge bg-dark">❓ Unknown</span>'
    };
    return badges[type] || badges['unknown'];
}

// Get category icon
function getCategoryIcon(category) {
    const icons = {
        demographics: 'bi-people-fill',
        competition: 'bi-buildings',
        accessibility: 'bi-car-front-fill',
        safety: 'bi-shield-check-fill',
        economic: 'bi-currency-dollar',
        regulatory: 'bi-file-text-fill'
    };
    return icons[category] || 'bi-info-circle';
}

// Get score color
function getScoreColor(score) {
    if (score >= 75) return '#198754';  // green
    if (score >= 60) return '#0dcaf0';  // cyan
    if (score >= 45) return '#ffc107';  // yellow
    return '#dc3545';  // red
}

// Get value badge class
function getValueBadgeClass(interpretation) {
    const classes = {
        'EXCELLENT': 'bg-success',
        'GOOD': 'bg-info',
        'FAIR': 'bg-warning',
        'POOR': 'bg-danger',
        'NEUTRAL': 'bg-secondary'
    };
    return classes[interpretation] || 'bg-secondary';
}

// Get confidence badge class
function getConfidenceBadgeClass(confidence) {
    const classes = {
        'HIGH': 'bg-success',
        'MEDIUM': 'bg-warning',
        'LOW': 'bg-danger'
    };
    return classes[confidence] || 'bg-secondary';
}

// Get category summary
function getCategorySummary(category, score, metricsCount) {
    const summaries = {
        demographics: `This location has ${metricsCount} demographic indicators analyzed. A score of ${score.toFixed(1)} suggests ${score >= 70 ? 'strong market potential with favorable population characteristics' : score >= 50 ? 'moderate market potential' : 'limited market potential'}. Key factors include children population, household income, and employment rates.`,
        competition: `Analyzed ${metricsCount} competition metrics. Score of ${score.toFixed(1)} indicates ${score >= 70 ? 'low competition with good market opportunity' : score >= 50 ? 'moderate competition' : 'high competition with saturated market'}. Consider market gaps and competitor quality.`,
        accessibility: `Evaluated ${metricsCount} accessibility factors. Score of ${score.toFixed(1)} shows ${score >= 70 ? 'excellent accessibility for parents' : score >= 50 ? 'adequate accessibility' : 'limited accessibility'}. Transit access and commute times are critical.`,
        safety: `Assessed ${metricsCount} safety indicators. Score of ${score.toFixed(1)} reflects ${score >= 70 ? 'very safe environment' : score >= 50 ? 'moderately safe conditions' : 'safety concerns exist'}. Crime rates and environmental factors matter.`,
        economic: `Analyzed ${metricsCount} economic factors. Score of ${score.toFixed(1)} indicates ${score >= 70 ? 'favorable economics with good profit potential' : score >= 50 ? 'viable economics' : 'challenging economic conditions'}. Real estate costs and labor availability are key.`,
        regulatory: `Reviewed ${metricsCount} regulatory requirements. Score of ${score.toFixed(1)} shows ${score >= 70 ? 'favorable regulatory environment' : score >= 50 ? 'standard regulations' : 'complex regulatory landscape'}. Licensing and zoning impact operations.`
    };
    return summaries[category] || `Analyzed ${metricsCount} data points with a score of ${score.toFixed(1)}.`;
}

// Get XAI for specific data point
function getXAIForDataPoint(category, dataKey, value) {
    const xaiDatabase = {
        // Demographics XAI
        'children_0_5_count': {
            what: 'Total number of children aged 0-5 years in the census area',
            how: 'Sum of Census Bureau variables: B01001_003E (males under 5) + B01001_027E (females under 5)',
            why: 'This is your direct target market. Higher count means more potential customers for childcare services.',
            where: 'Collected from U.S. Census Bureau American Community Survey (ACS) 5-Year estimates for the specified location',
            when: 'Retrieved in real-time from latest available ACS dataset (typically 2-3 years lag)',
            source: 'U.S. Census Bureau ACS 5-Year Estimates',
            confidence: 'HIGH',
            interpretation: value > 500 ? 'EXCELLENT' : value > 200 ? 'GOOD' : value > 50 ? 'FAIR' : 'POOR'
        },
        'children_5_9_count': {
            what: 'Number of children aged 5-9 years (school-age)',
            how: 'Sum of Census variables for ages 5-9 by gender',
            why: 'Indicates future demand as these children may have younger siblings, and shows established family presence',
            where: 'U.S. Census Bureau data for the geographic area',
            when: 'Real-time retrieval from latest ACS dataset',
            source: 'U.S. Census Bureau ACS',
            confidence: 'HIGH',
            interpretation: value > 600 ? 'EXCELLENT' : value > 300 ? 'GOOD' : value > 100 ? 'FAIR' : 'POOR'
        },
        'median_household_income': {
            what: 'Median annual household income in dollars',
            how: 'Direct Census variable B19013_001E - middle value of household income distribution',
            why: 'Higher income indicates greater ability to pay for quality childcare services. Typical childcare costs 10-20% of income.',
            where: 'Census tract or ZIP code level data',
            when: 'Latest ACS 5-Year estimate',
            source: 'U.S. Census Bureau',
            confidence: 'HIGH',
            interpretation: value > 80000 ? 'EXCELLENT' : value > 60000 ? 'GOOD' : value > 40000 ? 'FAIR' : 'POOR'
        },
        'unemployment_rate': {
            what: 'Percentage of labor force that is unemployed',
            how: '(unemployed / (employed + unemployed)) × 100',
            why: 'Lower unemployment means more working parents needing childcare. High unemployment reduces demand and affordability.',
            where: 'Local labor market statistics',
            when: 'Current employment data',
            source: 'Census Bureau labor statistics',
            confidence: 'HIGH',
            interpretation: value < 4 ? 'EXCELLENT' : value < 6 ? 'GOOD' : value < 10 ? 'FAIR' : 'POOR'
        },
        'population_density_children': {
            what: 'Number of children (0-5) per square mile',
            how: 'children_0_5_count / land_area_square_miles',
            why: 'Higher density means concentrated demand - easier to serve more customers with smaller service radius',
            where: 'Calculated from census geography and population',
            when: 'Derived from current data',
            source: 'Calculated from Census data',
            confidence: 'HIGH',
            interpretation: value > 100 ? 'EXCELLENT' : value > 50 ? 'GOOD' : value > 20 ? 'FAIR' : 'POOR'
        },

        // Competition XAI
        'existing_centers_count': {
            what: 'Number of childcare centers within specified radius',
            how: 'Google Places API search with keywords: "daycare", "childcare center", "preschool" - deduplicated by place_id',
            why: 'Direct competition indicator. More centers = more competition for customers and staff',
            where: 'Within the specified mile radius from target location',
            when: 'Real-time Google Places data at time of query',
            source: 'Google Places API',
            confidence: 'HIGH',
            interpretation: value < 5 ? 'EXCELLENT' : value < 10 ? 'GOOD' : value < 20 ? 'FAIR' : 'POOR'
        },
        'market_saturation_index': {
            what: 'Childcare centers per square mile (density)',
            how: 'existing_centers_count / (π × radius_miles²)',
            why: 'Measures competitive intensity. Values >2.0 suggest saturated market. <1.0 indicates opportunity.',
            where: 'Calculated for search area',
            when: 'Computed from current competitor count',
            source: 'Calculated from Places API',
            confidence: 'HIGH',
            interpretation: value < 1 ? 'EXCELLENT' : value < 2 ? 'GOOD' : value < 3 ? 'FAIR' : 'POOR'
        },
        'avg_competitor_rating': {
            what: 'Average Google rating of competing centers (1-5 stars)',
            how: 'Sum of all competitor ratings / count of centers with ratings',
            why: 'Quality benchmark. You need to match or exceed this to compete effectively. Low average suggests opportunity.',
            where: 'Averaged across all competitors in radius',
            when: 'Current Google ratings',
            source: 'Google Places ratings',
            confidence: 'HIGH',
            interpretation: value < 3.5 ? 'EXCELLENT' : value < 4.0 ? 'GOOD' : value < 4.5 ? 'FAIR' : 'POOR'
        },
        'market_gap_score': {
            what: 'Unmet demand percentage (0-100, higher = more opportunity)',
            how: '((estimated_demand - current_supply) / estimated_demand) × 100, where demand = children × 8% need rate',
            why: 'Identifies market opportunity. Score >60 = undersupplied market. <30 = oversupplied.',
            where: 'Market area analysis',
            when: 'Calculated from current data',
            source: 'Calculated from population and capacity',
            confidence: 'MEDIUM',
            interpretation: value > 60 ? 'EXCELLENT' : value > 40 ? 'GOOD' : value > 20 ? 'FAIR' : 'POOR'
        },

        // Accessibility XAI
        'transit_score': {
            what: 'Public transit accessibility score (0-100)',
            how: 'Quantity (40pts) + Proximity (50pts) + Quality (10pts) based on transit stations within 1 mile',
            why: 'Many working parents rely on transit. Higher score = more accessible to car-free families.',
            where: 'Within 1-mile radius of location',
            when: 'Current transit infrastructure',
            source: 'Google Places + Distance calculations',
            confidence: 'HIGH',
            interpretation: value > 70 ? 'EXCELLENT' : value > 50 ? 'GOOD' : value > 30 ? 'FAIR' : 'POOR'
        },
        'avg_commute_minutes': {
            what: 'Average commute time from major employment centers',
            how: 'Google Distance Matrix API with real-time traffic to downtown, business districts, hospitals',
            why: 'Drop-off convenience is critical. <20 minutes is ideal for working parents. >30 min reduces demand.',
            where: 'From location to major employers in area',
            when: 'Real-time traffic conditions',
            source: 'Google Distance Matrix API',
            confidence: 'HIGH',
            interpretation: value < 20 ? 'EXCELLENT' : value < 30 ? 'GOOD' : value < 45 ? 'FAIR' : 'POOR'
        },

        // Safety XAI
        'crime_rate_index': {
            what: 'Crime risk score (0-100, lower is safer)',
            how: 'Proxy: (risky_places × 5) - (safe_places × 2) + base_60. Risky = bars, nightclubs. Safe = schools, libraries.',
            why: 'Parent safety concern. Score <30 = very safe. >70 = high crime concern. Affects enrollment.',
            where: 'Area surrounding location',
            when: 'Current place data analysis',
            source: 'Estimated from Google Places (proxy)',
            confidence: 'MEDIUM',
            interpretation: value < 30 ? 'EXCELLENT' : value < 50 ? 'GOOD' : value < 70 ? 'FAIR' : 'POOR'
        },
        'air_quality_index': {
            what: 'Air quality score (0-500 AQI scale, lower is better)',
            how: 'Base 60 + (pollution_sources × 3) - (parks × 5). Sources: gas stations, factories.',
            why: "Children's respiratory health. AQI <50 = good, <100 = acceptable, >150 = unhealthy.",
            where: 'Local environment',
            when: 'Current environmental factors',
            source: 'Estimated from pollution sources',
            confidence: 'LOW',
            interpretation: value < 50 ? 'EXCELLENT' : value < 100 ? 'GOOD' : value < 150 ? 'FAIR' : 'POOR'
        },

        // Economic XAI
        'real_estate_cost_per_sqft': {
            what: 'Commercial real estate cost in dollars per square foot',
            how: 'Base $120 + (premium_amenities × $20). Amenities: schools, parks, transit. Capped $50-400.',
            why: 'Major fixed cost. Typical center needs 3000-5000 sqft. Low cost improves profit margins.',
            where: 'Local commercial market',
            when: 'Current market conditions',
            source: 'Estimated from neighborhood amenities',
            confidence: 'MEDIUM',
            interpretation: value < 150 ? 'EXCELLENT' : value < 200 ? 'GOOD' : value < 300 ? 'FAIR' : 'POOR'
        },
        'childcare_worker_availability_score': {
            what: 'Labor market score (0-100, higher = more available workers)',
            how: '50 + (schools_nearby × 5) - (existing_centers × 3). Schools = potential employee pipeline.',
            why: 'Staffing is critical. Ratio requirements: 1:4 (infants), 1:8 (toddlers). Score >60 = adequate pool.',
            where: 'Local labor market',
            when: 'Current analysis',
            source: 'Calculated from educational institutions',
            confidence: 'MEDIUM',
            interpretation: value > 60 ? 'EXCELLENT' : value > 45 ? 'GOOD' : value > 30 ? 'FAIR' : 'POOR'
        },

        // Regulatory XAI
        'licensing_complexity_score': {
            what: 'Regulatory burden score (0-100, lower = easier)',
            how: 'State requirements: staff qualifications, building codes, inspections. Complex states score higher.',
            why: 'Higher complexity = longer time to license, more costs. Score <40 = business-friendly.',
            where: 'State/local jurisdiction',
            when: 'Current regulations',
            source: 'State licensing databases',
            confidence: 'HIGH',
            interpretation: value < 40 ? 'EXCELLENT' : value < 60 ? 'GOOD' : value < 75 ? 'FAIR' : 'POOR'
        },

        // Additional Demographics Metrics
        'age_distribution_pct': {
            what: 'Percentage of population in target age groups (0-5 years)',
            how: '(children_0_5_count / total_population) × 100',
            why: 'Shows concentration of your target market. 6-8% is typical for suburban areas. Higher % = better demand concentration.',
            where: 'Census tract population statistics',
            when: 'Latest ACS 5-year estimates',
            source: 'U.S. Census Bureau',
            confidence: 'HIGH',
            interpretation: value > 7 ? 'EXCELLENT' : value > 5 ? 'GOOD' : value > 3 ? 'FAIR' : 'POOR'
        },
        'income_distribution_pct': {
            what: 'Percentage of households in upper-middle to high income brackets',
            how: '(households earning >$75k / total households) × 100',
            why: 'Indicates affordability. Childcare costs $200-2000/month. Higher income % = can sustain premium pricing.',
            where: 'Household income distribution data',
            when: 'Current ACS estimates',
            source: 'Census Bureau income tables',
            confidence: 'HIGH',
            interpretation: value > 60 ? 'EXCELLENT' : value > 40 ? 'GOOD' : value > 25 ? 'FAIR' : 'POOR'
        },
        'dual_income_rate': {
            what: 'Percentage of households where both parents work',
            how: '(married couple families with both working / all married couple families) × 100',
            why: 'Core target market. Dual-income families have highest childcare need AND affordability. Rate >70% is ideal.',
            where: 'Employment characteristics by household type',
            when: 'Latest labor force statistics',
            source: 'Census employment data',
            confidence: 'HIGH',
            interpretation: value > 70 ? 'EXCELLENT' : value > 60 ? 'GOOD' : value > 50 ? 'FAIR' : 'POOR'
        },
        'family_household_rate': {
            what: 'Percentage of households that are families (vs singles/roommates)',
            how: '(family households / total households) × 100. Family = married couple or single parent with children.',
            why: 'Family-dense neighborhoods have established community, schools, parks - ideal for childcare centers.',
            where: 'Household composition statistics',
            when: 'Current ACS data',
            source: 'Census household tables',
            confidence: 'HIGH',
            interpretation: value > 70 ? 'EXCELLENT' : value > 60 ? 'GOOD' : value > 50 ? 'FAIR' : 'POOR'
        },
        'birth_rate': {
            what: 'Births per 1,000 population annually',
            how: 'Estimated from ratio of children 0-1 to total population × 1000',
            why: 'Forward indicator of demand. Birth rate >15 means growing childcare need. <10 suggests declining demand.',
            where: 'Vital statistics for area',
            when: 'Derived from recent population data',
            source: 'Calculated from Census age distributions',
            confidence: 'MEDIUM',
            interpretation: value > 15 ? 'EXCELLENT' : value > 12 ? 'GOOD' : value > 9 ? 'FAIR' : 'POOR'
        },
        'employment_to_population_ratio': {
            what: 'Percentage of working-age adults who are employed',
            how: '(employed persons / population 16+) × 100',
            why: 'High employment = more parents needing childcare during work hours. Ratio >65% indicates strong labor market.',
            where: 'Local employment statistics',
            when: 'Current labor force data',
            source: 'Census employment tables',
            confidence: 'HIGH',
            interpretation: value > 65 ? 'EXCELLENT' : value > 60 ? 'GOOD' : value > 55 ? 'FAIR' : 'POOR'
        },
        'education_attainment_bachelors': {
            what: "Percentage of adults 25+ with bachelor's degree or higher",
            how: "(adults with bachelor's or advanced degree / adults 25+) × 100",
            why: 'Education correlates with income and childcare utilization. >40% bachelor+ indicates professional workforce.',
            where: 'Educational attainment statistics',
            when: 'Latest ACS education data',
            source: 'Census education tables',
            confidence: 'HIGH',
            interpretation: value > 40 ? 'EXCELLENT' : value > 30 ? 'GOOD' : value > 20 ? 'FAIR' : 'POOR'
        },
        'poverty_rate': {
            what: 'Percentage of population below federal poverty line',
            how: '(persons in poverty / total population) × 100. Poverty line ~$28k for family of 4.',
            why: 'High poverty reduces childcare affordability. Rate <10% is ideal. >20% indicates affordability challenges.',
            where: 'Income and poverty statistics',
            when: 'Current ACS poverty data',
            source: 'Census poverty tables',
            confidence: 'HIGH',
            interpretation: value < 10 ? 'EXCELLENT' : value < 15 ? 'GOOD' : value < 20 ? 'FAIR' : 'POOR'
        },

        // Additional Competition Metrics
        'avg_competitor_reviews': {
            what: 'Average number of Google reviews per competitor',
            how: 'Total reviews across all competitors / number of competitors',
            why: 'Engagement indicator. >50 reviews = established, visible competitors. <20 = new/unknown market.',
            where: 'Google Places review data',
            when: 'Current review counts',
            source: 'Google Places API',
            confidence: 'HIGH',
            interpretation: value < 30 ? 'EXCELLENT' : value < 60 ? 'GOOD' : value < 100 ? 'FAIR' : 'POOR'
        },
        'top_competitor_name': {
            what: 'Name of highest-rated childcare center nearby',
            how: 'Competitor with highest rating; ties broken by review count',
            why: 'Your main competition benchmark. Study their pricing, programs, reviews to differentiate.',
            where: 'Top result from Places search',
            when: 'Current market leader',
            source: 'Google Places',
            confidence: 'HIGH',
            interpretation: 'NEUTRAL'
        },
        'competitive_intensity_score': {
            what: 'Market competition level (0-100, higher = more intense)',
            how: 'Weighted: saturation (40%) + avg rating (30%) + review volume (30%)',
            why: 'Combines quantity and quality of competition. Score >70 = very competitive. <40 = opportunity market.',
            where: 'Calculated from all competitor data',
            when: 'Real-time calculation',
            source: 'Derived from Places API',
            confidence: 'HIGH',
            interpretation: value < 40 ? 'EXCELLENT' : value < 60 ? 'GOOD' : value < 75 ? 'FAIR' : 'POOR'
        },
        'estimated_market_demand': {
            what: 'Estimated number of childcare slots needed in area',
            how: 'children_0_5 × 0.08 (8% typical utilization rate)',
            why: 'Total market size. Compare to current supply to find gaps. Demand >500 = substantial market.',
            where: 'Service area population',
            when: 'Based on current population',
            source: 'Calculated from demographics',
            confidence: 'MEDIUM',
            interpretation: value > 500 ? 'EXCELLENT' : value > 300 ? 'GOOD' : value > 150 ? 'FAIR' : 'POOR'
        },
        'estimated_current_supply': {
            what: 'Estimated total childcare capacity from competitors',
            how: 'existing_centers × 60 (assumed average center capacity)',
            why: 'Current market supply. Compare to demand. Supply >90% of demand = saturated.',
            where: 'All competitors in radius',
            when: 'Current competitor count',
            source: 'Estimated from center count',
            confidence: 'MEDIUM',
            interpretation: value < 300 ? 'EXCELLENT' : value < 500 ? 'GOOD' : value < 800 ? 'FAIR' : 'POOR'
        },
        'centers_within_1_mile': {
            what: 'Number of childcare centers within 1-mile radius',
            how: 'Google Places search filtered by distance ≤1 mile',
            why: 'Immediate competition. Parents prefer centers within 1 mile of home/work. <3 is ideal.',
            where: '1-mile radius circle from location',
            when: 'Current Places data',
            source: 'Google Places API',
            confidence: 'HIGH',
            interpretation: value < 3 ? 'EXCELLENT' : value < 6 ? 'GOOD' : value < 10 ? 'FAIR' : 'POOR'
        },
        'centers_within_2_miles': {
            what: 'Number of childcare centers within 2-mile radius',
            how: 'Google Places search filtered by distance ≤2 miles',
            why: 'Extended competition zone. Shows market density. <8 centers suggests room for growth.',
            where: '2-mile radius circle from location',
            when: 'Current Places data',
            source: 'Google Places API',
            confidence: 'HIGH',
            interpretation: value < 8 ? 'EXCELLENT' : value < 15 ? 'GOOD' : value < 25 ? 'FAIR' : 'POOR'
        },

        // Additional Accessibility Metrics
        'transit_stations_count': {
            what: 'Number of public transit stations within 1 mile',
            how: 'Count of bus stops, train stations, metro stations from Google Places',
            why: 'More stations = better access for car-free parents. 5+ stations = excellent transit access.',
            where: '1-mile search radius',
            when: 'Current transit infrastructure',
            source: 'Google Places transit data',
            confidence: 'HIGH',
            interpretation: value > 5 ? 'EXCELLENT' : value > 2 ? 'GOOD' : value > 0 ? 'FAIR' : 'POOR'
        },
        'closest_transit_distance_miles': {
            what: 'Distance to nearest public transit station in miles',
            how: 'Minimum distance from location to any transit station',
            why: 'Closer transit = more accessible. <0.25 miles (5-min walk) is ideal for drop-off convenience.',
            where: 'Nearest station distance',
            when: 'Current location analysis',
            source: 'Google Maps distance calculation',
            confidence: 'HIGH',
            interpretation: value < 0.25 ? 'EXCELLENT' : value < 0.5 ? 'GOOD' : value < 1.0 ? 'FAIR' : 'POOR'
        },
        'parking_availability_score': {
            what: 'Parking convenience score (0-100, higher = better)',
            how: 'Based on parking lots, street parking, parking structures within 500 ft',
            why: 'Most parents drive. Easy parking enables quick drop-off/pickup. Score >70 = ample parking.',
            where: 'Immediate vicinity',
            when: 'Current parking infrastructure',
            source: 'Google Places parking data',
            confidence: 'MEDIUM',
            interpretation: value > 70 ? 'EXCELLENT' : value > 50 ? 'GOOD' : value > 30 ? 'FAIR' : 'POOR'
        },
        'major_highways_nearby': {
            what: 'Number of major highways within 2 miles',
            how: 'Count of interstate and state highways identified via Google',
            why: 'Highway access enables longer commutes. Good for parents commuting from suburbs to urban jobs.',
            where: '2-mile radius',
            when: 'Current road network',
            source: 'Google Maps road data',
            confidence: 'HIGH',
            interpretation: value > 2 ? 'EXCELLENT' : value > 0 ? 'GOOD' : 'FAIR'
        },
        'highway_distance_miles': {
            what: 'Distance to nearest major highway in miles',
            how: 'Minimum distance to interstate or major state highway',
            why: 'Closer highway = broader service area for commuting parents. <1 mile is ideal.',
            where: 'Nearest highway distance',
            when: 'Current location',
            source: 'Google Maps',
            confidence: 'HIGH',
            interpretation: value < 1 ? 'EXCELLENT' : value < 2 ? 'GOOD' : value < 5 ? 'FAIR' : 'POOR'
        },
        'public_transit_modes_count': {
            what: 'Number of different transit types available (bus, train, metro, etc.)',
            how: 'Unique transit types counted from station search',
            why: 'More modes = more access options. 3+ modes indicates comprehensive transit network.',
            where: 'Transit options in area',
            when: 'Current transit availability',
            source: 'Google Places transit types',
            confidence: 'HIGH',
            interpretation: value > 2 ? 'EXCELLENT' : value > 1 ? 'GOOD' : value > 0 ? 'FAIR' : 'POOR'
        },
        'peak_traffic_multiplier': {
            what: 'Rush hour delay factor (1.0 = no delay, 2.0 = double time)',
            how: 'Google Distance Matrix: travel_time_with_traffic / travel_time_without_traffic',
            why: 'Higher multiplier = worse congestion. Parents avoid centers with difficult rush-hour access. <1.5 is acceptable.',
            where: 'Commute routes to location',
            when: 'Real-time traffic analysis',
            source: 'Google Distance Matrix API',
            confidence: 'HIGH',
            interpretation: value < 1.5 ? 'EXCELLENT' : value < 2.0 ? 'GOOD' : value < 2.5 ? 'FAIR' : 'POOR'
        },
        'accessibility_score': {
            what: 'Overall location accessibility rating (0-100)',
            how: 'Weighted average: transit (30%), commute (30%), parking (25%), highways (15%)',
            why: 'Composite convenience measure. Score >70 = highly accessible. <40 = access challenges.',
            where: 'Combined accessibility factors',
            when: 'Calculated from all access metrics',
            source: 'Calculated composite',
            confidence: 'HIGH',
            interpretation: value > 70 ? 'EXCELLENT' : value > 55 ? 'GOOD' : value > 40 ? 'FAIR' : 'POOR'
        },

        // Additional Safety Metrics
        'police_stations_nearby': {
            what: 'Number of police stations within 2 miles',
            how: 'Google Places search for police departments and stations',
            why: 'Police presence indicates safety. 2+ stations = good emergency response capability.',
            where: '2-mile radius',
            when: 'Current facility locations',
            source: 'Google Places',
            confidence: 'HIGH',
            interpretation: value > 2 ? 'EXCELLENT' : value > 1 ? 'GOOD' : value > 0 ? 'FAIR' : 'POOR'
        },
        'fire_stations_nearby': {
            what: 'Number of fire stations within 2 miles',
            how: 'Google Places search for fire departments',
            why: 'Fire safety and emergency response. Licensing often requires station within certain distance. 1-2 is ideal.',
            where: '2-mile radius',
            when: 'Current facility locations',
            source: 'Google Places',
            confidence: 'HIGH',
            interpretation: value > 1 ? 'EXCELLENT' : value > 0 ? 'GOOD' : 'FAIR'
        },
        'hospitals_nearby': {
            what: 'Number of hospitals within 5 miles',
            how: 'Google Places search for hospitals and medical centers',
            why: 'Medical emergency access. Critical for childcare licensing. 2+ hospitals = excellent medical infrastructure.',
            where: '5-mile radius',
            when: 'Current facilities',
            source: 'Google Places',
            confidence: 'HIGH',
            interpretation: value > 2 ? 'EXCELLENT' : value > 1 ? 'GOOD' : value > 0 ? 'FAIR' : 'POOR'
        },
        'emergency_response_time_minutes': {
            what: 'Estimated emergency service response time in minutes',
            how: 'Based on nearest station distance: <1mi = 3min, 1-2mi = 5min, 2-3mi = 8min, >3mi = 12min',
            why: 'Critical for child safety. <5 minutes is ideal. >10 minutes is concerning.',
            where: 'Travel time from nearest station',
            when: 'Estimated from distances',
            source: 'Calculated from station proximity',
            confidence: 'MEDIUM',
            interpretation: value < 5 ? 'EXCELLENT' : value < 8 ? 'GOOD' : value < 12 ? 'FAIR' : 'POOR'
        },
        'environmental_hazards_score': {
            what: 'Environmental risk score (0-100, lower is better)',
            how: 'Proximity penalty: gas stations, factories, waste sites, highways with pollution',
            why: 'Children are sensitive to pollution. Score <30 = clean environment. >60 = concern.',
            where: 'Surrounding area hazards',
            when: 'Current environmental factors',
            source: 'Google Places hazard identification',
            confidence: 'LOW',
            interpretation: value < 30 ? 'EXCELLENT' : value < 50 ? 'GOOD' : value < 70 ? 'FAIR' : 'POOR'
        },
        'flood_risk_indicator': {
            what: 'Flood zone risk level (0=minimal, 1=moderate, 2=high)',
            how: 'Proxy based on proximity to water bodies and elevation estimates',
            why: 'Flood risk affects insurance, licensing, and safety. Level 0 (minimal) is preferred.',
            where: 'FEMA flood zone estimates',
            when: 'Current flood mapping',
            source: 'Estimated from geography',
            confidence: 'LOW',
            interpretation: value === 0 ? 'EXCELLENT' : value === 1 ? 'FAIR' : 'POOR'
        },
        'safety_facilities_score': {
            what: 'Public safety infrastructure score (0-100)',
            how: 'Weighted: police (30%), fire (30%), hospitals (40%) - based on quantity and proximity',
            why: 'Comprehensive safety measure. Score >70 = excellent safety infrastructure.',
            where: 'Combined safety facilities',
            when: 'Current analysis',
            source: 'Calculated from facility data',
            confidence: 'HIGH',
            interpretation: value > 70 ? 'EXCELLENT' : value > 55 ? 'GOOD' : value > 40 ? 'FAIR' : 'POOR'
        },
        'neighborhood_safety_score': {
            what: 'Overall neighborhood safety rating (0-100)',
            how: 'Composite: (100 - crime_index) × 0.4 + safety_facilities × 0.3 + (100 - env_hazards) × 0.3',
            why: 'Holistic safety measure. Score >75 = very safe. <50 = safety concerns.',
            where: 'Neighborhood analysis',
            when: 'Current composite',
            source: 'Calculated from multiple factors',
            confidence: 'MEDIUM',
            interpretation: value > 75 ? 'EXCELLENT' : value > 60 ? 'GOOD' : value > 45 ? 'FAIR' : 'POOR'
        },

        // Additional Economic Metrics
        'startup_cost_estimate': {
            what: 'Estimated initial investment to open childcare center',
            how: 'Real estate + renovations + equipment + licenses: (sqft × cost/sqft × 5000) + $50k',
            why: 'Capital requirement. Typical range $100k-300k. Lower costs improve ROI and break-even timeline.',
            where: 'Local market conditions',
            when: 'Current cost estimates',
            source: 'Calculated from real estate data',
            confidence: 'MEDIUM',
            interpretation: value < 150000 ? 'EXCELLENT' : value < 200000 ? 'GOOD' : value < 300000 ? 'FAIR' : 'POOR'
        },
        'operating_cost_estimate': {
            what: 'Estimated monthly operating expenses',
            how: 'Rent + staff + utilities + insurance: (sqft × $15/month) + staff_costs',
            why: 'Fixed costs to cover monthly. Typical $30k-60k/month. Lower costs improve profit margins.',
            where: 'Local operating environment',
            when: 'Current market rates',
            source: 'Calculated from local costs',
            confidence: 'MEDIUM',
            interpretation: value < 40000 ? 'EXCELLENT' : value < 50000 ? 'GOOD' : value < 65000 ? 'FAIR' : 'POOR'
        },
        'revenue_potential': {
            what: 'Estimated annual revenue at full capacity',
            how: 'Capacity (60 children) × average_fee ($1200/month) × 12 months × occupancy (85%)',
            why: 'Income potential. Typical range $500k-1.5M annually. Higher revenue supports better programs.',
            where: 'Market pricing capacity',
            when: 'Current market rates',
            source: 'Calculated from demographics',
            confidence: 'MEDIUM',
            interpretation: value > 900000 ? 'EXCELLENT' : value > 700000 ? 'GOOD' : value > 500000 ? 'FAIR' : 'POOR'
        },
        'breakeven_timeline_months': {
            what: 'Months until center becomes profitable',
            how: 'startup_cost / (monthly_revenue - monthly_expenses), assuming gradual ramp to 85% capacity',
            why: 'Time to profitability. <24 months is good. >36 months is challenging. Affects financing.',
            where: 'Financial projection',
            when: 'Estimated timeline',
            source: 'Calculated financial model',
            confidence: 'MEDIUM',
            interpretation: value < 24 ? 'EXCELLENT' : value < 30 ? 'GOOD' : value < 42 ? 'FAIR' : 'POOR'
        },
        'labor_cost_estimate': {
            what: 'Estimated annual staff payroll costs',
            how: 'Required staff × average salary. Ratios 1:4 (infants), 1:8 (toddlers). ~$35k avg per staff.',
            why: 'Largest expense (60-70% of operating costs). Lower wages improve margins but affect quality.',
            where: 'Local labor market wages',
            when: 'Current market rates',
            source: 'Labor market data',
            confidence: 'MEDIUM',
            interpretation: value < 300000 ? 'EXCELLENT' : value < 400000 ? 'GOOD' : value < 550000 ? 'FAIR' : 'POOR'
        },
        'market_growth_potential': {
            what: 'Market expansion opportunity score (0-100)',
            how: 'Birth rate trend + population growth + income growth + competition gap',
            why: 'Future demand indicator. Score >60 = growing market. <40 = stagnant or declining.',
            where: 'Market dynamics analysis',
            when: 'Current trends',
            source: 'Demographic projections',
            confidence: 'LOW',
            interpretation: value > 60 ? 'EXCELLENT' : value > 45 ? 'GOOD' : value > 30 ? 'FAIR' : 'POOR'
        },
        'economic_viability_score': {
            what: 'Overall financial feasibility rating (0-100)',
            how: 'Weighted: revenue potential (30%), costs (25%), break-even (25%), growth (20%)',
            why: 'Comprehensive economic assessment. Score >70 = strong business case. <50 = financially challenging.',
            where: 'Complete financial analysis',
            when: 'Current calculations',
            source: 'Calculated composite',
            confidence: 'MEDIUM',
            interpretation: value > 70 ? 'EXCELLENT' : value > 55 ? 'GOOD' : value > 40 ? 'FAIR' : 'POOR'
        },
        'profit_margin_estimate': {
            what: 'Estimated net profit margin percentage',
            how: '((revenue - expenses) / revenue) × 100. Industry average 10-20%.',
            why: 'Profitability measure. >15% = healthy margins. <8% = thin margins, high risk.',
            where: 'Financial model',
            when: 'Projected margins',
            source: 'Calculated from revenue/costs',
            confidence: 'MEDIUM',
            interpretation: value > 15 ? 'EXCELLENT' : value > 10 ? 'GOOD' : value > 5 ? 'FAIR' : 'POOR'
        },

        // Additional Regulatory Metrics
        'state_requirements': {
            what: 'Specific state licensing requirements summary',
            how: 'Lookup based on state: background checks, education, facilities, health standards',
            why: 'Varies by state. Understanding requirements prevents compliance issues and delays.',
            where: 'State regulatory agency',
            when: 'Current regulations',
            source: 'State licensing database',
            confidence: 'HIGH',
            interpretation: 'NEUTRAL'
        },
        'staff_ratio_requirements': {
            what: 'Required staff-to-child ratios by age group',
            how: 'State mandated ratios: 1:4 (infants), 1:6 (toddlers), 1:10 (preschool) - varies by state',
            why: 'Determines staffing costs. Stricter ratios = more staff = higher costs but better quality.',
            where: 'State childcare regulations',
            when: 'Current requirements',
            source: 'State licensing standards',
            confidence: 'HIGH',
            interpretation: 'NEUTRAL'
        },
        'background_check_requirements': {
            what: 'Required background screening for staff',
            how: 'Criminal history, child abuse registry, fingerprinting - specific checks vary by state',
            why: 'Ensures child safety. More thorough checks = longer hiring process but critical for licensing.',
            where: 'State and federal requirements',
            when: 'Current mandates',
            source: 'State regulations',
            confidence: 'HIGH',
            interpretation: 'NEUTRAL'
        },
        'health_safety_standards': {
            what: 'Health and safety compliance requirements',
            how: 'First aid, CPR, health policies, medication, emergency plans, sanitation',
            why: 'Core operational requirements. Non-compliance risks license suspension or revocation.',
            where: 'State health department rules',
            when: 'Current standards',
            source: 'State regulations',
            confidence: 'HIGH',
            interpretation: 'NEUTRAL'
        },
        'facility_requirements': {
            what: 'Building and space requirements',
            how: 'Square footage per child, outdoor space, bathrooms, kitchen, exits, lighting, safety features',
            why: 'Physical space standards. Retrofit costs can be significant. New construction is easier.',
            where: 'State facility codes',
            when: 'Current building codes',
            source: 'State licensing',
            confidence: 'HIGH',
            interpretation: 'NEUTRAL'
        },
        'zoning_compliance': {
            what: 'Local zoning regulations for childcare facilities',
            how: 'Permitted use zones, conditional permits, parking requirements, setbacks',
            why: 'Location restrictions. Some zones prohibit childcare. Verify before leasing/buying property.',
            where: 'Local municipal code',
            when: 'Current zoning laws',
            source: 'City/county zoning office',
            confidence: 'MEDIUM',
            interpretation: 'NEUTRAL'
        },
        'operating_hours_restrictions': {
            what: 'Limitations on hours of operation',
            how: 'Some localities restrict hours (e.g., no 24-hour care, quiet hours)',
            why: 'Affects service offerings. Extended hours can be competitive advantage if allowed.',
            where: 'Local ordinances',
            when: 'Current restrictions',
            source: 'Municipal regulations',
            confidence: 'MEDIUM',
            interpretation: 'NEUTRAL'
        }
    };

    // Return XAI or default
    return xaiDatabase[dataKey] || {
        what: `Measurement of ${dataKey.replace(/_/g, ' ')}`,
        how: 'Data collected from various sources',
        why: 'This metric contributes to overall location analysis',
        where: 'Geographic area of interest',
        when: 'Real-time or recent data',
        source: 'Multiple data sources',
        confidence: 'MEDIUM',
        interpretation: 'NEUTRAL'
    };
}

// Update timing chart
function updateTimingChart(performanceReport) {
    if (!performanceReport) return;

    const ctx = document.getElementById('timingChart').getContext('2d');

    // Destroy existing chart
    if (timingChart) {
        timingChart.destroy();
    }

    if (!performanceReport) {
        if (timingChart) {
            timingChart.destroy();
            timingChart = null;
        }
        const canvas = document.getElementById('timingChart');
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.font = '14px Arial';
            ctx.fillStyle = '#6c757d';
            ctx.textAlign = 'center';
            ctx.fillText('No performance data available', canvas.width / 2, canvas.height / 2);
        }
        return;
    }

    const categories = performanceReport.categories || {};
    const steps = performanceReport.steps || [];
    const labels = Object.keys(categories).map(k => k.charAt(0).toUpperCase() + k.slice(1));
    const data = Object.values(categories).map(c => c.total_ms);

    timingChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Time (ms)',
                data: data,
                backgroundColor: [
                    'rgba(13, 110, 253, 0.7)',
                    'rgba(25, 135, 84, 0.7)',
                    'rgba(13, 202, 240, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(220, 53, 69, 0.7)',
                    'rgba(108, 117, 125, 0.7)'
                ],
                borderColor: [
                    'rgba(13, 110, 253, 1)',
                    'rgba(25, 135, 84, 1)',
                    'rgba(13, 202, 240, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(220, 53, 69, 1)',
                    'rgba(108, 117, 125, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.parsed.y.toFixed(2)} ms`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Time (milliseconds)'
                    }
                }
            }
        }
    });
}

// Format value for display
function formatValue(value) {
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return value.toLocaleString();
        } else {
            return value.toFixed(2);
        }
    } else if (typeof value === 'boolean') {
        return value ? 'Yes' : 'No';
    } else if (typeof value === 'object') {
        return JSON.stringify(value);
    }
    return value;
}

// Show/hide loading state
function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const button = document.getElementById('analyzeBtn');

    if (show) {
        spinner.classList.remove('d-none');
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Analyzing...';
    } else {
        spinner.classList.add('d-none');
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-lightning-charge-fill"></i> Analyze Location';
    }
}

// Show error message
function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.textContent = message;
    errorAlert.classList.remove('d-none');

    // Scroll to error
    errorAlert.scrollIntoView({ behavior: 'smooth' });
}

// Hide error message
function hideError() {
    document.getElementById('errorAlert').classList.add('d-none');
}

// Export results as JSON
function exportJSON() {
    if (!currentResults) return;

    const dataStr = JSON.stringify(currentResults, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

    const exportFileDefaultName = `location-analysis-${Date.now()}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}

// Export results as CSV
function exportCSV() {
    if (!currentResults) return;

    let csv = 'Category,Data Point,Value\n';

    for (const [category, data] of Object.entries(currentResults.categories)) {
        const categoryData = data.data || {};
        for (const [key, value] of Object.entries(categoryData)) {
            if (typeof value !== 'object') {
                csv += `"${category}","${key}","${value}"\n`;
            }
        }
    }

    const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    const exportFileDefaultName = `location-analysis-${Date.now()}.csv`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
}
