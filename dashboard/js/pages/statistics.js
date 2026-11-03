/**
 * Statistical Tests Page - Visual Research Dashboard
 */

window.App.registerPage('statistics', {
    state: {
        tests: [],
        filtered: [],
        tierFilter: 'all',
        metricFilter: 'all',
        search: '',
        activeFigureIndex: 0
    },

    figures: [
        {
            src: 'figures/paper/P01_paired_transitions.png',
            title: 'Figure P01: Paired Outcome State Transitions',
            desc: 'State transitions between MAS and SAS across Correct, Wrong, and Policy Withheld.'
        },
        {
            src: 'figures/paper/P02_bootstrap_distributions.png',
            title: 'Figure P02: Bootstrap Difference Distributions',
            desc: 'Non-parametric bootstrap distributions for paired performance contrasts across 16 GB cases.'
        },
        {
            src: 'figures/paper/P03_report_scatter.png',
            title: 'Figure P03: Report-Level Accuracy Dispersion',
            desc: 'Corporate 10-K report-level performance clusters illustrating intra-cluster correlation.'
        },
        {
            src: 'figures/paper/P05_latency_distributions.png',
            title: 'Figure P05: Inference Latency Distributions',
            desc: 'Boxplots of per-case wall-clock inference latency across MAS and SAS architectures.'
        },
        {
            src: 'figures/paper/P06_memory_timelines.png',
            title: 'Figure P06: Process Memory Timelines',
            desc: 'Sub-second cgroup RSS telemetry over elapsed execution time proving RUPP adherence.'
        },
        {
            src: 'figures/paper/P07_stage_costs.png',
            title: 'Figure P07: Stage Breakdown & Token Costs',
            desc: 'Token consumption and latency across Extractor, Drafter, and Verifier components.'
        }
    ],

    async render(container, app) {
        if (this.state.tests.length === 0) {
            const raw = await app.fetchJson('data/paper/paper_statistical_tests.rows.json') || [];
            this.state.tests = raw;
            this.state.filtered = raw;
        }

        const activeFig = this.figures[this.state.activeFigureIndex];

        container.innerHTML = `
            <!-- Top Metric Strip -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">
                        <span>Hypothesis Battery</span>
                        <span class="badge badge-mas">Inference</span>
                    </div>
                    <div class="stat-card-value text-[#2563EB]">126 Tests</div>
                    <div class="stat-card-meta">21 paired contrasts × 6 endpoints</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 100%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#15803D]">
                    <div class="stat-card-label">
                        <span>Clustered Significance</span>
                        <span class="badge badge-correct">Report-Adjusted</span>
                    </div>
                    <div class="stat-card-value text-[#15803D]">p &lt; 0.001</div>
                    <div class="stat-card-meta">Durkalski cluster-adjusted p = 1.53e-5</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#15803D]" style="width: 95%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#7C3AED]">
                    <div class="stat-card-label">
                        <span>Intra-Cluster Design Effect</span>
                        <span class="badge badge-sas">DEFF</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">1.24 – 1.86</div>
                    <div class="stat-card-meta">Corporate 10-K clustering penalty accounted</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#7C3AED]" style="width: 65%;"></div>
                    </div>
                </div>
            </div>

            <!-- Publication Figures Visual Showcase (Eye Magnet) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Publication Graphics Showcase</h3>
                        <p class="text-xs text-[#64748B]">Click thumbnails below to preview full-resolution vector figures from the manuscript</p>
                    </div>
                    <button id="active-fig-enlarge" class="btn btn-primary text-xs">
                        <i data-lucide="maximize-2" class="w-3.5 h-3.5"></i> Enlarge Fullscreen
                    </button>
                </div>

                <!-- Active Main Figure Preview -->
                <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4 items-center">
                    <div class="lg:col-span-8 bg-[#F8FAFC] border border-[#E2E8F0] rounded-lg p-3 text-center flex items-center justify-center">
                        <img id="active-fig-img" src="${activeFig.src}" alt="${activeFig.title}" class="max-h-72 mx-auto rounded object-contain cursor-pointer transition hover:scale-[1.01]">
                    </div>

                    <div class="lg:col-span-4 space-y-4">
                        <div>
                            <span class="badge badge-mas mb-2">Figure Preview</span>
                            <h4 id="active-fig-title" class="font-bold text-base text-[#172033] mt-1">${activeFig.title}</h4>
                            <p id="active-fig-desc" class="text-xs text-[#64748B] mt-2 leading-relaxed">${activeFig.desc}</p>
                        </div>

                        <!-- Thumbnail Strip -->
                        <div class="pt-2 border-t border-[#E2E8F0]">
                            <div class="text-[11px] font-bold text-[#64748B] uppercase font-mono mb-2">Select Figure (P01 – P07)</div>
                            <div class="grid grid-cols-6 gap-2">
                                ${this.figures.map((fig, idx) => `
                                    <div class="fig-thumb cursor-pointer border-2 rounded p-0.5 transition ${idx === this.state.activeFigureIndex ? 'border-[#2563EB] bg-[#EFF6FF]' : 'border-[#E2E8F0] hover:border-[#94A3B8]'}" data-index="${idx}">
                                        <img src="${fig.src}" alt="Thumb" class="h-10 w-full object-cover rounded">
                                    </div>
                                `).join('')}
                            </div>
                        </div>
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

                <div class="table-container max-h-[420px] overflow-y-auto mt-4">
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

        // Figure thumbnails
        document.querySelectorAll('.fig-thumb').forEach(el => {
            el.addEventListener('click', () => {
                const idx = parseInt(el.getAttribute('data-index'), 10);
                this.state.activeFigureIndex = idx;
                const fig = this.figures[idx];
                document.getElementById('active-fig-img').src = fig.src;
                document.getElementById('active-fig-title').innerText = fig.title;
                document.getElementById('active-fig-desc').innerText = fig.desc;

                document.querySelectorAll('.fig-thumb').forEach((t, i) => {
                    if (i === idx) {
                        t.classList.add('border-[#2563EB]', 'bg-[#EFF6FF]');
                        t.classList.remove('border-[#E2E8F0]');
                    } else {
                        t.classList.remove('border-[#2563EB]', 'bg-[#EFF6FF]');
                        t.classList.add('border-[#E2E8F0]');
                    }
                });
            });
        });

        // Enlarge fullscreen
        const enlargeBtn = document.getElementById('active-fig-enlarge');
        const activeImg = document.getElementById('active-fig-img');
        const openLightbox = () => {
            const fig = this.figures[this.state.activeFigureIndex];
            window.App.showFigure(fig.src, fig.title, fig.desc);
        };
        enlargeBtn?.addEventListener('click', openLightbox);
        activeImg?.addEventListener('click', openLightbox);
    },

    renderTable() {
        const tbody = document.getElementById('stat-table-body');
        if (!tbody) return;

        const items = this.state.filtered.slice(0, 30);
        if (items.length === 0) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center py-6 text-[#64748B] text-xs">No matching tests.</td></tr>`;
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
                </tr>
            `;
        }).join('');
    }
});