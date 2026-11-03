/**
 * Statistical Tests Page - Academic Light Theme
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
            <!-- Top Summary Card (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div class="space-y-1 max-w-4xl">
                        <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                            Statistical Inference & Hypothesis Battery
                        </div>
                        <h2 class="text-base font-bold text-[#172033]">
                            Cluster-Robust & Nonparametric Hypothesis Battery
                        </h2>
                        <p class="text-xs text-[#64748B] leading-relaxed">
                            Following regulated finance reporting standards, we report exact McNemar tests, Durkalski cluster-adjusted tests (accounting for 50 report / company clusters), CR1 standard errors, and Stuart–Maxwell tests of marginal homogeneity across 21 paired experimental comparisons.
                        </p>
                    </div>
                    <div class="shrink-0 text-right font-mono">
                        <div class="text-[11px] text-[#64748B]">Hypothesis Battery</div>
                        <div class="text-base font-bold text-[#2563EB]">126 Tests Evaluated</div>
                    </div>
                </div>
            </div>

            <!-- Stats Overview Row -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Total Statistical Tests</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">126 Tests</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">21 paired contrasts × 6 endpoints</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Clustered Significance</div>
                    <div class="text-xl font-bold font-mono text-[#15803D] mt-1">p < 0.001</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">Report-level intra-cluster adjusted</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Design Effect (DEFF)</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">1.24 – 1.86</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">Corporate report correlation penalty</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Publication Figures</div>
                    <div class="text-xl font-bold font-mono text-[#2563EB] mt-1">9 Figures</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">P01 through P09 verified</div>
                </div>
            </div>

            <!-- Publication Figures Gallery -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Publication Figures Gallery (P01 – P09)</h3>
                        <p class="text-xs text-[#64748B]">Click any figure thumbnail to view full-resolution vector graphics and formal manuscript captions</p>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-4">
                    <div class="card p-2 hover:border-[#2563EB] cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P01_paired_transitions.png', 'Figure P01: Paired Transitions', 'State transitions between MAS and SAS across Correct, Wrong, and Withheld.')">
                        <img src="figures/paper/P01_paired_transitions.png" alt="P01" class="rounded h-24 w-full object-cover border border-[#E2E8F0]">
                        <div class="font-bold text-xs text-[#172033] mt-1.5 truncate">P01: Transitions</div>
                    </div>

                    <div class="card p-2 hover:border-[#2563EB] cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P02_bootstrap_distributions.png', 'Figure P02: Bootstrap Distributions', 'Non-parametric bootstrap distributions for paired differences.')">
                        <img src="figures/paper/P02_bootstrap_distributions.png" alt="P02" class="rounded h-24 w-full object-cover border border-[#E2E8F0]">
                        <div class="font-bold text-xs text-[#172033] mt-1.5 truncate">P02: Bootstrap CIs</div>
                    </div>

                    <div class="card p-2 hover:border-[#2563EB] cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P03_report_scatter.png', 'Figure P03: Report-Level Scatter', 'Accuracy dispersion grouped by corporate 10-K report.')">
                        <img src="figures/paper/P03_report_scatter.png" alt="P03" class="rounded h-24 w-full object-cover border border-[#E2E8F0]">
                        <div class="font-bold text-xs text-[#172033] mt-1.5 truncate">P03: Report Scatter</div>
                    </div>

                    <div class="card p-2 hover:border-[#2563EB] cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P05_latency_distributions.png', 'Figure P05: Latency Distributions', 'Per-case inference latency distributions across deployment arms.')">
                        <img src="figures/paper/P05_latency_distributions.png" alt="P05" class="rounded h-24 w-full object-cover border border-[#E2E8F0]">
                        <div class="font-bold text-xs text-[#172033] mt-1.5 truncate">P05: Latency Boxplots</div>
                    </div>

                    <div class="card p-2 hover:border-[#2563EB] cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P06_memory_timelines.png', 'Figure P06: Process Memory Timelines', 'Continuous process-tree RSS timelines showing RUPP cap adherence.')">
                        <img src="figures/paper/P06_memory_timelines.png" alt="P06" class="rounded h-24 w-full object-cover border border-[#E2E8F0]">
                        <div class="font-bold text-xs text-[#172033] mt-1.5 truncate">P06: Memory Timelines</div>
                    </div>

                    <div class="card p-2 hover:border-[#2563EB] cursor-pointer transition" onclick="window.App.showFigure('figures/paper/P07_stage_costs.png', 'Figure P07: Stage Breakdown Costs', 'Token consumption and latency across extractor, drafter, and verifier.')">
                        <img src="figures/paper/P07_stage_costs.png" alt="P07" class="rounded h-24 w-full object-cover border border-[#E2E8F0]">
                        <div class="font-bold text-xs text-[#172033] mt-1.5 truncate">P07: Stage Costs</div>
                    </div>
                </div>
            </div>

            <!-- Table of 126 Hypothesis Tests -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[#E2E8F0] gap-3">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Hypothesis Test Battery (126 Tests)</h3>
                        <p class="text-xs text-[#64748B]">Statistical endpoints with Wald CIs, bootstrap CIs, and clustered p-values</p>
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
            tbody.innerHTML = `<tr><td colspan="10" class="text-center py-6 text-[#64748B] text-xs">No matching tests.</td></tr>`;
            return;
        }

        tbody.innerHTML = items.map(t => {
            const pVal = t.exact_mcnemar_p != null ? (t.exact_mcnemar_p < 0.0001 ? t.exact_mcnemar_p.toExponential(2) : t.exact_mcnemar_p.toFixed(4)) : 'N/A';
            const durkP = t.durkalski_report_p != null ? (t.durkalski_report_p < 0.0001 ? t.durkalski_report_p.toExponential(2) : t.durkalski_report_p.toFixed(4)) : 'N/A';
            const deltaPct = (t.delta * 100).toFixed(1) + '%';
            const isSig = (t.exact_mcnemar_p != null && t.exact_mcnemar_p < 0.05);

            return `
                <tr>
                    <td class="font-medium text-[#172033] text-xs">${t.label || t.comparison}</td>
                    <td class="font-mono text-xs text-[#64748B]">${t.tier} GB</td>
                    <td class="text-xs text-[#64748B] font-mono">${t.metric || '—'}</td>
                    <td class="font-mono text-xs text-[#64748B]">${t.n}</td>
                    <td class="font-mono text-xs font-bold ${t.delta < 0 ? 'text-[#DC2626]' : 'text-[#15803D]'}">${deltaPct}</td>
                    <td class="font-mono text-[11px] text-[#64748B]">[${(t.wald95_low*100).toFixed(1)}%, ${(t.wald95_high*100).toFixed(1)}%]</td>
                    <td class="font-mono text-[11px] text-[#64748B]">[${(t.boot95_low*100).toFixed(1)}%, ${(t.boot95_high*100).toFixed(1)}%]</td>
                    <td class="font-mono text-xs ${isSig ? 'text-[#15803D] font-bold' : 'text-[#64748B]'}">${pVal}</td>
                    <td class="font-mono text-xs ${durkP !== 'N/A' && parseFloat(durkP) < 0.05 ? 'text-[#15803D] font-bold' : 'text-[#64748B]'}">${durkP}</td>
                    <td class="font-mono text-xs text-[#64748B]">${t.bowker_p != null ? (t.bowker_p < 0.001 ? '<0.001' : t.bowker_p.toFixed(3)) : '—'}</td>
                </tr>
            `;
        }).join('');
    }
});
