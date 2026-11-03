/**
 * Runs & Evidence Page - Visual Research Dashboard
 */

window.App.registerPage('runs', {
    state: {
        evidence: [],
        conditions: [],
        archiveStats: {},
        search: ''
    },

    async render(container, app) {
        if (this.state.evidence.length === 0) {
            this.state.evidence = await app.fetchJson('data/le16_v2/tier8_evidence_catalog.json') || [];
            this.state.conditions = await app.fetchJson('data/le16_v2/tier8_condition_inventory.json') || [];
            this.state.archiveStats = await app.fetchJson('data/archive_stats.json') || {};
        }

        const stats = this.state.archiveStats;

        container.innerHTML = `
            <!-- Archive Stat Strip -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">
                        <span>Evidence Volume</span>
                        <span class="badge badge-mas">17 Archives</span>
                    </div>
                    <div class="stat-card-value text-[#2563EB]">${stats.total_mb ? stats.total_mb + ' MB' : '645 MB'}</div>
                    <div class="stat-card-meta">17 verified SSD archives</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 100%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#15803D]">
                    <div class="stat-card-label">
                        <span>Source Files</span>
                        <span class="badge badge-correct">Hashed</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">${stats.total_files ?? '2,598'}</div>
                    <div class="stat-card-meta">1,629 unique content hashes</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#15803D]" style="width: 85%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#7C3AED]">
                    <div class="stat-card-label">
                        <span>Cataloged Artifacts</span>
                        <span class="badge badge-sas">Indexed</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">197 Items</div>
                    <div class="stat-card-meta">Indexed research outputs</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#7C3AED]" style="width: 70%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#D97706]">
                    <div class="stat-card-label">
                        <span>Experimental Conditions</span>
                        <span class="badge badge-withheld">Evaluations</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">15 Conditions</div>
                    <div class="stat-card-meta">30 recorded evaluations</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#D97706]" style="width: 60%;"></div>
                    </div>
                </div>
            </div>

            <!-- Visual Archive Breakdown Chart -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Archive Storage & Artifact Distribution</h3>
                        <p class="text-xs text-[#64748B]">Volume in Megabytes across experimental cohorts</p>
                    </div>
                    <span class="badge badge-mas">Archive Telemetry</span>
                </div>
                <div class="pt-4">
                    <div class="w-full h-56">
                        <canvas id="runs-archive-chart"></canvas>
                    </div>
                </div>
            </div>

            <!-- 8 GB Experimental Condition Inventory -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">8 GB Experimental Condition Inventory (30 Evaluations)</h3>
                        <p class="text-xs text-[#64748B]">Evaluations across control, crossed, baseline, and analysis conditions</p>
                    </div>
                    <span class="badge badge-sas">8 GB Natural Regime</span>
                </div>

                <div class="table-container max-h-64 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Job Name</th>
                                <th>Metric</th>
                                <th>n</th>
                                <th>Reports</th>
                                <th>Correct</th>
                                <th>Wrong</th>
                                <th>Withheld</th>
                                <th>Peak RSS</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.state.conditions.map(c => `
                                <tr>
                                    <td class="font-mono text-xs text-[#172033] font-medium">${c.job}</td>
                                    <td class="text-xs text-[#64748B] font-mono">${c.metric}</td>
                                    <td class="font-mono text-xs text-[#172033]">${c.n}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${c.reports}</td>
                                    <td class="font-mono text-xs font-bold text-[#15803D]">${c.correct}</td>
                                    <td class="font-mono text-xs font-bold text-[#DC2626]">${c.wrong}</td>
                                    <td class="font-mono text-xs font-bold text-[#D97706]">${c.withheld}</td>
                                    <td class="font-mono text-xs text-[#172033] font-semibold">${(c.peak_rss_bytes / (1024**3)).toFixed(2)} GB</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Historical Evidence Catalog Browser -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[#E2E8F0] gap-3">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Historical Evidence Catalog (197 Artifacts)</h3>
                        <p class="text-xs text-[#64748B]">Search cataloged checkpoint logs, diagnostic runs, and traces</p>
                    </div>
                    <input id="evidence-search" type="text" placeholder="Filter artifact path..." class="input-search text-xs w-full md:w-64">
                </div>

                <div class="table-container max-h-64 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Artifact Path / Filename</th>
                                <th>Category</th>
                                <th>Archive Location</th>
                            </tr>
                        </thead>
                        <tbody id="evidence-table-body">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.renderArchiveChart();
        this.renderEvidenceRows();

        document.getElementById('evidence-search')?.addEventListener('input', (e) => {
            this.state.search = e.target.value.toLowerCase().trim();
            this.renderEvidenceRows();
        });
    },

    renderArchiveChart() {
        const ctx = document.getElementById('runs-archive-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['16 GB Primary & Ablation Runs', '8 GB Iterative Curricula', 'Model Checkpoints & Weights', 'Diagnostic Traces & OOM Audits'],
                datasets: [{
                    label: 'Volume (MB)',
                    data: [310, 195, 98, 42],
                    backgroundColor: ['#2563EB', '#3B82F6', '#7C3AED', '#64748B'],
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#172033',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F8FAFC',
                        padding: 10,
                        callbacks: {
                            label: (c) => ` ${c.raw} MB archive storage`
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: '#E9EEF5' },
                        ticks: { color: '#64748B', callback: v => v + ' MB', font: { size: 10, family: 'JetBrains Mono' } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#172033', font: { size: 11, family: 'Inter' } }
                    }
                }
            }
        });
    },

    renderEvidenceRows() {
        const tbody = document.getElementById('evidence-table-body');
        if (!tbody) return;

        let items = this.state.evidence;
        if (this.state.search) {
            items = items.filter(it => {
                const s = JSON.stringify(it).toLowerCase();
                return s.includes(this.state.search);
            });
        }

        const displayItems = items.slice(0, 20);
        if (displayItems.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="text-center py-6 text-[#64748B] text-xs">No matching evidence artifacts.</td></tr>`;
            return;
        }

        tbody.innerHTML = displayItems.map(it => {
            const pathStr = typeof it === 'string' ? it : (it.path || it.source || it.name || JSON.stringify(it));
            const cat = pathStr.includes('runs') ? 'Runs' : (pathStr.includes('datasets') ? 'Datasets' : (pathStr.includes('weights') ? 'Weights' : 'Phase 2'));
            return `
                <tr>
                    <td class="font-mono text-xs text-[#172033] font-medium">${pathStr}</td>
                    <td><span class="badge ${cat === 'Runs' ? 'badge-mas' : 'badge-sas'}">${cat}</span></td>
                    <td class="font-mono text-xs text-[#64748B]">dashboard_handoff/evidence/</td>
                </tr>
            `;
        }).join('');
    }
});