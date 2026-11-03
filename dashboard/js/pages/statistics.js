/**
 * Statistical Battery & Hypothesis Testing Page - Minimal, Plain, Publication-Grade
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
            <!-- Top Summary Card (Plain, Crisp) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Inferential Statistics</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Cluster-Robust & Nonparametric Hypothesis Battery
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            To account for company and 10-K report clustering (50 clusters), we report exact McNemar tests, Durkalski cluster-adjusted tests, CR1 standard errors, and Stuart–Maxwell homogeneity tests across all 21 paired experimental comparisons.
                        </p>
                    </div>
                    <div class="shrink-0 text-right">
                        <div class="text-[11px] text-slate-400 font-mono">Statistical Battery</div>
                        <div class="text-base font-bold font-mono text-white">126 Hypotheses</div>
                    </div>
                </div>
            </div>

            <!-- Stats Overview Row -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Evaluated Hypotheses</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">126 Tests</div>
                    <div class="text-xs text-slate-400 font-mono mt-0.5">21 paired contrasts × 6 endpoints</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Clustered Significance</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">p < 0.001</div>
                    <div class="text-xs text-slate-400 font-mono mt-0.5">Report-level intra-cluster adjusted</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Design Effect (DEFF)</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">1.24 – 1.86</div>
                    <div class="text-xs text-slate-400 font-mono mt-0.5">Report correlation penalty</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Publication Figures</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">9 Figures</div>
                    <div class="text-xs text-slate-400 font-mono mt-0.5">P01 through P09 verified</div>
                </div>
            </div>

            <!-- Publication Figures Gallery -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-semibold text-white">Publication Figures Gallery (P01 – P09)</h3>
                        <p class="text-xs text-slate-400">Click any figure thumbnail to view full-resolution vector graphics and research captions</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
                    <div class="card p-2 hover:border-slate-500 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P01_paired_transitions.png', 'Figure P01: Paired Transitions', 'State transitions between MAS and SAS across Correct, Wrong, and Withheld.')">
                        <img src="figures/paper/P01_paired_transitions.png" alt="P01" class="rounded h-24 w-full object-cover">
                        <div class="font-medium text-xs text-white mt-1.5 truncate">P01: Transitions</div>
                    </div>

                    <div class="card p-2 hover:border-slate-500 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P02_bootstrap_distributions.png', 'Figure P02: Bootstrap Distributions', 'Non-parametric bootstrap distributions for paired differences.')">
                        <img src="figures/paper/P02_bootstrap_distributions.png" alt="P02" class="rounded h-24 w-full object-cover">
                        <div class="font-medium text-xs text-white mt-1.5 truncate">P02: Bootstrap CIs</div>
                    </div>

                    <div class="card p-2 hover:border-slate-500 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P03_report_scatter.png', 'Figure P03: Report-Level Scatter', 'Accuracy dispersion grouped by corporate 10-K report.')">
                        <img src="figures/paper/P03_report_scatter.png" alt="P03" class="rounded h-24 w-full object-cover">
                        <div class="font-medium text-xs text-white mt-1.5 truncate">P03: Report Scatter</div>
                    </div>

                    <div class="card p-2 hover:border-slate-500 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P05_latency_distributions.png', 'Figure P05: Latency Distributions', 'Per-case inference latency distributions across deployment arms.')">
                        <img src="figures/paper/P05_latency_distributions.png" alt="P05" class="rounded h-24 w-full object-cover">
                        <div class="font-medium text-xs text-white mt-1.5 truncate">P05: Latency Boxplots</div>
                    </div>

                    <div class="card p-2 hover:border-slate-500 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P06_memory_timelines.png', 'Figure P06: Process Memory Timelines', 'Continuous process-tree RSS timelines showing RUPP cap adherence.')">
                        <img src="figures/paper/P06_memory_timelines.png" alt="P06" class="rounded h-24 w-full object-cover">
                        <div class="font-medium text-xs text-white mt-1.5 truncate">P06: Memory Timelines</div>
                    </div>

                    <div class="card p-2 hover:border-slate-500 cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P07_stage_costs.png', 'Figure P07: Stage Breakdown Costs', 'Token consumption and latency across extractor, drafter, and verifier.')">
                        <img src="figures/paper/P07_stage_costs.png" alt="P07" class="rounded h-24 w-full object-cover">
                        <div class="font-medium text-xs text-white mt-1.5 truncate">P07: Stage Costs</div>
                    </div>
                </div>
            </div>

            <!-- Table of 126 Hypothesis Tests -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-3">
                    <div>
                        <h3 class="text-sm font-semibold text-white">Hypothesis Test Battery (126 Tests)</h3>
                        <p class="text-xs text-slate-400">Statistical endpoints with Wald CIs, bootstrap CIs, and clustered p-values</p>
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
                        <input id="stat-search-input" type="text" placeholder="Filter comparison..." class="input-search text-xs">
                    </div>
                </div>

                <div class="table-container max-h-[480px] overflow-y-auto mt-4">
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

        const items = this.state.filtered.slice(0, 30);
        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" class="text-center py-6 text-slate-500 text-xs">No matching tests.</td></tr>`;
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
                    <td class="font-mono text-xs text-slate-300">${t.tier} GB</td>
                    <td class="text-xs text-slate-400 font-mono">${t.metric || '—'}</td>
                    <td class="font-mono text-xs text-slate-400">${t.n}</td>
                    <td class="font-mono text-xs font-semibold ${t.delta < 0 ? 'text-rose-400' : 'text-emerald-400'}">${deltaPct}</td>
                    <td class="font-mono text-[11px] text-slate-400">[${(t.wald95_low*100).toFixed(1)}%, ${(t.wald95_high*100).toFixed(1)}%]</td>
                    <td class="font-mono text-[11px] text-slate-400">[${(t.boot95_low*100).toFixed(1)}%, ${(t.boot95_high*100).toFixed(1)}%]</td>
                    <td class="font-mono text-xs ${isSig ? 'text-white font-semibold' : 'text-slate-400'}">${pVal}</td>
                    <td class="font-mono text-xs ${durkP !== 'N/A' && parseFloat(durkP) < 0.05 ? 'text-white' : 'text-slate-400'}">${durkP}</td>
                    <td class="font-mono text-xs text-slate-400">${t.bowker_p != null ? (t.bowker_p < 0.001 ? '<0.001' : t.bowker_p.toFixed(3)) : '—'}</td>
                </tr>
            `;
        }).join('');
    }
});
