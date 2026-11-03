/**
 * Statistical Battery & Hypothesis Testing Page
 */

window.App.registerPage('statistics', {
    state: {
        tests: [],
        filtered: [],
        tierFilter: 'all',
        metricFilter: 'all',
        search: ''
    },

    async render(container, app) {
        if (this.state.tests.length === 0) {
            const raw = await app.fetchJson('data/paper/paper_statistical_tests.rows.json') || [];
            this.state.tests = raw;
            this.state.filtered = raw;
        }

        container.innerHTML = `
            <!-- Top Rigour Banner -->
            <div class="card bg-gradient-to-r from-slate-900 to-emerald-950/20 border-emerald-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-mas">Statistical Battery</span>
                            <span class="text-xs text-slate-400 font-mono">126 Hypotheses Evaluated</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Cluster-Robust & Nonparametric Hypothesis Battery
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            Following regulated finance reporting standards, we report exact McNemar tests, Durkalski cluster-adjusted tests (accounting for 50 report / company clusters), CR1 standard errors, and Stuart–Maxwell tests of marginal homogeneity across 21 paired contrasts.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Stats Overview Cards -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Total Statistical Tests</div>
                    <div class="text-2xl font-bold font-mono text-white mt-1">126</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">21 paired comparisons × 6 endpoints</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Clustered Significance</div>
                    <div class="text-2xl font-bold font-mono text-emerald-400 mt-1">p < 0.001</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">Both McNemar & Durkalski report tests</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Design Effect (DEFF)</div>
                    <div class="text-2xl font-bold font-mono text-amber-400 mt-1">1.24 - 1.86</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">Report-level intra-cluster correlation</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Publication Figures</div>
                    <div class="text-2xl font-bold font-mono text-cyan-400 mt-1">9 Figures</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">P01 through P09 verified</div>
                </div>
            </div>

            <!-- Publication Figures Gallery -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="image" class="w-4 h-4 text-cyan-400"></i>
                            Publication Paper Figures Gallery (P01 – P09)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Click any figure to inspect vector resolution and formal manuscript captions</p>
                    </div>
                    <span class="badge badge-sas">Vector Visualizations</span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div class="card p-3 hover:border-cyan-500/50 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P01_paired_transitions.png', 'Figure P01: Paired Transitions', 'Case-level state transitions between MAS and SAS across Correct, Wrong, and Withheld.')">
                        <img src="figures/paper/P01_paired_transitions.png" alt="P01" class="rounded h-36 w-full object-cover">
                        <div class="font-bold text-xs text-white mt-2">P01: Paired Transitions</div>
                        <div class="text-[10px] text-slate-400">State transition matrix between arms</div>
                    </div>

                    <div class="card p-3 hover:border-cyan-500/50 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P02_bootstrap_distributions.png', 'Figure P02: Bootstrap Distributions', 'Non-parametric bootstrap distributions for paired differences.')">
                        <img src="figures/paper/P02_bootstrap_distributions.png" alt="P02" class="rounded h-36 w-full object-cover">
                        <div class="font-bold text-xs text-white mt-2">P02: Bootstrap Distributions</div>
                        <div class="text-[10px] text-slate-400">Empirical 95% confidence intervals</div>
                    </div>

                    <div class="card p-3 hover:border-cyan-500/50 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P03_report_scatter.png', 'Figure P03: Report-Level Scatter', 'Accuracy correlation and dispersion grouped by financial 10-K report.')">
                        <img src="figures/paper/P03_report_scatter.png" alt="P03" class="rounded h-36 w-full object-cover">
                        <div class="font-bold text-xs text-white mt-2">P03: Report-Level Scatter</div>
                        <div class="text-[10px] text-slate-400">Report clustering dispersion</div>
                    </div>

                    <div class="card p-3 hover:border-cyan-500/50 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P05_latency_distributions.png', 'Figure P05: Latency Distributions', 'Per-case inference latency distributions across deployment arms.')">
                        <img src="figures/paper/P05_latency_distributions.png" alt="P05" class="rounded h-36 w-full object-cover">
                        <div class="font-bold text-xs text-white mt-2">P05: Latency Distributions</div>
                        <div class="text-[10px] text-slate-400">Inference seconds boxplots</div>
                    </div>

                    <div class="card p-3 hover:border-cyan-500/50 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P06_memory_timelines.png', 'Figure P06: Process Memory Timelines', 'Continuous process-tree RSS timelines showing RUPP cap adherence.')">
                        <img src="figures/paper/P06_memory_timelines.png" alt="P06" class="rounded h-36 w-full object-cover">
                        <div class="font-bold text-xs text-white mt-2">P06: Memory Timelines</div>
                        <div class="text-[10px] text-slate-400">Process RSS telemetry & caps</div>
                    </div>

                    <div class="card p-3 hover:border-cyan-500/50 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P07_stage_costs.png', 'Figure P07: Stage Breakdown Costs', 'Token consumption and latency across extractor, drafter, and verifier.')">
                        <img src="figures/paper/P07_stage_costs.png" alt="P07" class="rounded h-36 w-full object-cover">
                        <div class="font-bold text-xs text-white mt-2">P07: Stage Costs</div>
                        <div class="text-[10px] text-slate-400">Stage token & second allocation</div>
                    </div>
                </div>
            </div>

            <!-- Table of 126 Hypothesis Tests -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-3">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="calculator" class="w-4 h-4 text-emerald-400"></i>
                            Hypothesis Test Battery (126 Tests)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Filter by comparison, metric, or search by test label</p>
                    </div>

                    <div class="flex items-center gap-2 w-full md:w-auto">
                        <select id="stat-tier-filter" class="select-filter text-xs">
                            <option value="all">All Tiers (16 & 8 GB)</option>
                            <option value="16">16 GB Tier</option>
                            <option value="8">8 GB Tier</option>
                        </select>
                        <select id="stat-metric-filter" class="select-filter text-xs">
                            <option value="all">All Metrics</option>
                            <option value="case_success">Case Success</option>
                            <option value="raw_execution">Raw Execution</option>
                        </select>
                        <input id="stat-search-input" type="text" placeholder="Search comparison..." class="input-search text-xs">
                    </div>
                </div>

                <div class="table-container max-h-[500px] overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Comparison Label</th>
                                <th>Tier</th>
                                <th>Metric</th>
                                <th>n</th>
                                <th>Delta (Δ)</th>
                                <th>Wald 95% CI</th>
                                <th>Bootstrap 95% CI</th>
                                <th>Exact McNemar p</th>
                                <th>Durkalski Clustered p</th>
                                <th>Bowker Homogeneity</th>
                            </tr>
                        </thead>
                        <tbody id="stat-table-body">
                            <!-- Injected dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.bindEvents();
        this.renderTable();
    },

    bindEvents() {
        const update = () => {
            let list = this.state.tests;
            if (this.state.tierFilter !== 'all') {
                list = list.filter(t => String(t.tier) === this.state.tierFilter);
            }
            if (this.state.metricFilter !== 'all') {
                list = list.filter(t => t.metric && t.metric.includes(this.state.metricFilter));
            }
            if (this.state.search) {
                list = list.filter(t => (t.label && t.label.toLowerCase().includes(this.state.search)) || (t.comparison && t.comparison.toLowerCase().includes(this.state.search)));
            }
            this.state.filtered = list;
            this.renderTable();
        };

        document.getElementById('stat-tier-filter')?.addEventListener('change', (e) => {
            this.state.tierFilter = e.target.value;
            update();
        });

        document.getElementById('stat-metric-filter')?.addEventListener('change', (e) => {
            this.state.metricFilter = e.target.value;
            update();
        });

        document.getElementById('stat-search-input')?.addEventListener('input', (e) => {
            this.state.search = e.target.value.toLowerCase().trim();
            update();
        });
    },

    renderTable() {
        const tbody = document.getElementById('stat-table-body');
        if (!tbody) return;

        const items = this.state.filtered.slice(0, 30); // show top 30
        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" class="text-center py-6 text-slate-500 text-xs">No statistical tests match filters.</td></tr>`;
            return;
        }

        tbody.innerHTML = items.map(t => {
            const pVal = t.exact_mcnemar_p != null ? (t.exact_mcnemar_p < 0.0001 ? t.exact_mcnemar_p.toExponential(2) : t.exact_mcnemar_p.toFixed(4)) : 'N/A';
            const durkP = t.durkalski_report_p != null ? (t.durkalski_report_p < 0.0001 ? t.durkalski_report_p.toExponential(2) : t.durkalski_report_p.toFixed(4)) : 'N/A';
            const deltaPct = (t.delta * 100).toFixed(1) + '%';
            const isSig = (t.exact_mcnemar_p != null && t.exact_mcnemar_p < 0.05);

            return `
                <tr>
                    <td class="font-medium text-white text-xs">${t.label || t.comparison}</td>
                    <td class="font-mono text-xs">${t.tier} GB</td>
                    <td class="text-xs text-slate-300 font-mono">${t.metric || '—'}</td>
                    <td class="font-mono text-xs">${t.n}</td>
                    <td class="font-mono text-xs font-bold ${t.delta < 0 ? 'text-rose-400' : 'text-emerald-400'}">${deltaPct}</td>
                    <td class="font-mono text-[11px] text-slate-400">[${(t.wald95_low*100).toFixed(1)}%, ${(t.wald95_high*100).toFixed(1)}%]</td>
                    <td class="font-mono text-[11px] text-slate-400">[${(t.boot95_low*100).toFixed(1)}%, ${(t.boot95_high*100).toFixed(1)}%]</td>
                    <td class="font-mono text-xs ${isSig ? 'text-emerald-400 font-bold' : 'text-slate-400'}">${pVal}</td>
                    <td class="font-mono text-xs ${durkP !== 'N/A' && parseFloat(durkP) < 0.05 ? 'text-emerald-400' : 'text-slate-400'}">${durkP}</td>
                    <td class="font-mono text-xs text-slate-400">${t.bowker_p != null ? (t.bowker_p < 0.001 ? '<0.001' : t.bowker_p.toFixed(3)) : '—'}</td>
                </tr>
            `;
        }).join('');
    }
});

