/**
 * Executive Overview Page
 */

window.App.registerPage('overview', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const kpis = aggr ? aggr.kpis : {};
        const jobs = aggr ? aggr.jobs_16gb : {};

        const mas = jobs['tier16-mas-primary'] || {};
        const sas = jobs['tier16-sas-primary'] || {};

        container.innerHTML = `
            <!-- Top Alert / Context Banner -->
            <div class="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-500/30 p-4 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <div class="p-2.5 rounded-lg bg-indigo-500/20 text-indigo-400">
                        <i data-lucide="scale" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <div class="text-sm font-bold text-white tracking-wide">
                            Core Research Question: Spend It Together or Spend It Big?
                        </div>
                        <div class="text-xs text-slate-300 mt-0.5">
                            Can a multi-agent system of smaller full-precision LLMs outperform a single large quantized LLM under identical host-adjusted RAM caps (12.8 GB / 6.4 GB) and thinking-token budgets?
                        </div>
                    </div>
                </div>
                <div class="flex items-center gap-2 font-mono text-xs">
                    <span class="badge badge-mas">RUPP Protocol</span>
                    <span class="badge badge-sas">Phase 3 Final</span>
                </div>
            </div>

            <!-- Key Statistical KPIs -->
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                <div class="card stat-card">
                    <div class="text-xs text-slate-400 font-medium">16 GB Acc Delta (MAS - SAS)</div>
                    <div class="text-2xl font-bold font-mono text-rose-400 mt-2">${kpis.accuracy_delta ?? -45.6}%</div>
                    <div class="text-[10px] text-slate-500 font-mono mt-1">Holm p = 6.10e-5</div>
                </div>
                <div class="card stat-card">
                    <div class="text-xs text-slate-400 font-medium">Total Cases Evaluated</div>
                    <div class="text-2xl font-bold font-mono text-white mt-2">${kpis.total_cases_combined ?? 1728}</div>
                    <div class="text-[10px] text-slate-500 font-mono mt-1">960 (16GB) + 768 (8GB)</div>
                </div>
                <div class="card stat-card">
                    <div class="text-xs text-slate-400 font-medium">SAS 16GB Accuracy</div>
                    <div class="text-2xl font-bold font-mono text-purple-400 mt-2">${kpis.primary_sas_accuracy ?? 50.6}%</div>
                    <div class="text-[10px] text-slate-500 font-mono mt-1">Qwen2.5-14B-Q4</div>
                </div>
                <div class="card stat-card">
                    <div class="text-xs text-slate-400 font-medium">MAS 16GB Accuracy</div>
                    <div class="text-2xl font-bold font-mono text-emerald-400 mt-2">${kpis.primary_mas_accuracy ?? 5.0}%</div>
                    <div class="text-[10px] text-slate-500 font-mono mt-1">73.8% Withheld Rate</div>
                </div>
                <div class="card stat-card alert">
                    <div class="text-xs text-slate-400 font-medium">Swap Breaches Caught</div>
                    <div class="text-2xl font-bold font-mono text-amber-400 mt-2">2</div>
                    <div class="text-[10px] text-slate-500 font-mono mt-1">44 MB breach audited</div>
                </div>
                <div class="card stat-card">
                    <div class="text-xs text-slate-400 font-medium">Evidence Files Archived</div>
                    <div class="text-2xl font-bold font-mono text-cyan-400 mt-2">${kpis.total_evidence_files ?? 2598}</div>
                    <div class="text-[10px] text-slate-500 font-mono mt-1">17 managed ZIPs</div>
                </div>
            </div>

            <!-- Visual Charts Row -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Chart 1: Outcome Breakdown Donut (Correct vs Wrong vs Withheld) -->
                <div class="card">
                    <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                        <div>
                            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                <i data-lucide="pie-chart" class="w-4 h-4 text-emerald-400"></i>
                                16 GB Primary Outcome Distributions
                            </h3>
                            <p class="text-xs text-slate-400 mt-0.5">Dual-metric accounting: Correct vs Wrong vs Withheld</p>
                        </div>
                        <span class="badge badge-mas">n = 160 per arm</span>
                    </div>
                    <div class="pt-4 flex flex-col items-center">
                        <div class="w-full h-64">
                            <canvas id="overview-outcome-chart"></canvas>
                        </div>
                        <div class="text-xs text-slate-400 text-center mt-2 max-w-md">
                            <span class="text-emerald-400 font-semibold">Key Finding:</span> MAS withholds 73.8% of cases due to verifier rejection, while SAS delivers answers on 86.9% of cases with 50.6% numerical accuracy.
                        </div>
                    </div>
                </div>

                <!-- Chart 2: Cross-Tier Comparison (8 GB vs 16 GB) -->
                <div class="card">
                    <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                        <div>
                            <h3 class="text-sm font-bold text-white flex items-center gap-2">
                                <i data-lucide="bar-chart" class="w-4 h-4 text-purple-400"></i>
                                Cross-Tier Regimes (8 GB vs 16 GB)
                            </h3>
                            <p class="text-xs text-slate-400 mt-0.5">Pretrained FinQA (16 GB) vs Adapted / Synthetic (8 GB)</p>
                        </div>
                        <span class="badge badge-sas">2 Regimes</span>
                    </div>
                    <div class="pt-4 flex flex-col items-center">
                        <div class="w-full h-64">
                            <canvas id="overview-tier-chart"></canvas>
                        </div>
                        <div class="text-xs text-slate-400 text-center mt-2 max-w-md">
                            <span class="text-purple-400 font-semibold">Rigour Note:</span> Denominators, task cohorts, and model adaptations differ between tiers. The study establishes independent tier evaluations, not a causal RAM-scaling curve.
                        </div>
                    </div>
                </div>
            </div>

            <!-- Architecture Comparison Grid -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                        <i data-lucide="layers" class="w-4 h-4 text-cyan-400"></i>
                        Competing Deployment Architectures (Nominal 16 GB Tier)
                    </h3>
                    <p class="text-xs text-slate-400 mt-0.5">Both arms operate under the identical 12.8 GB cgroup process-tree cap after 20% OS reservation</p>
                </div>
                <div class="overflow-x-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Deployment Arm</th>
                                <th>Architecture</th>
                                <th>Models & Weights</th>
                                <th>Precision</th>
                                <th>Process RSS Cap</th>
                                <th>Thinking-Token Cap</th>
                                <th>16 GB Reported Acc</th>
                                <th>Withheld Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><span class="badge badge-mas">MAS-FP16</span></td>
                                <td class="font-medium text-white">Multi-Agent Team (Extractor + Drafter + Verifier)</td>
                                <td class="font-mono text-xs">Qwen2.5 1.5B + 7B + 3B</td>
                                <td>Native FP16/BF16</td>
                                <td class="font-mono text-xs">12.8 GB</td>
                                <td class="font-mono text-xs">Equalized (Tran 2026)</td>
                                <td class="font-bold text-emerald-400 font-mono">5.0% (8/160)</td>
                                <td class="font-bold text-amber-400 font-mono">73.8%</td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-sas">SAS-Quant</span></td>
                                <td class="font-medium text-white">Single Generalist Monolith (Industry Default)</td>
                                <td class="font-mono text-xs">Qwen2.5-14B-Instruct</td>
                                <td>GGUF Q4_K_M</td>
                                <td class="font-mono text-xs">12.8 GB</td>
                                <td class="font-mono text-xs">Equalized (Tran 2026)</td>
                                <td class="font-bold text-purple-400 font-mono">50.6% (81/160)</td>
                                <td class="font-bold text-slate-400 font-mono">13.1%</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Quick Navigation Cards Grid -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <a href="#comparison" class="card hover:border-emerald-500/50 cursor-pointer transition p-4 flex items-start gap-3">
                    <div class="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
                        <i data-lucide="swords" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <div class="text-sm font-bold text-white">MAS vs SAS Deep Dive</div>
                        <div class="text-xs text-slate-400 mt-1">Forest plot of all 42 paired contrasts, outcome alluvials, and 48 metric disagreements.</div>
                    </div>
                </a>

                <a href="#cases" class="card hover:border-cyan-500/50 cursor-pointer transition p-4 flex items-start gap-3">
                    <div class="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-400">
                        <i data-lucide="microscope" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <div class="text-sm font-bold text-white">Case Explorer</div>
                        <div class="text-xs text-slate-400 mt-1">Inspect all 1,728 individual test cases with calculation programs, tokens, and repair traces.</div>
                    </div>
                </a>

                <a href="#hardware" class="card hover:border-rose-500/50 cursor-pointer transition p-4 flex items-start gap-3">
                    <div class="p-2.5 rounded-lg bg-rose-500/10 text-rose-400">
                        <i data-lucide="cpu" class="w-5 h-5"></i>
                    </div>
                    <div>
                        <div class="text-sm font-bold text-white">Hardware & Telemetry</div>
                        <div class="text-xs text-slate-400 mt-1">Process RSS timeline, swap failure invalidation audit, and model conversion memory benchmarks.</div>
                    </div>
                </a>
            </div>
        `;

        // Render Charts
        this.renderCharts(mas, sas);
    },

    renderCharts(mas, sas) {
        // Chart 1: Outcome Donut
        const ctx1 = document.getElementById('overview-outcome-chart');
        if (ctx1) {
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['MAS-FP16 (Team)', 'SAS-Quant (Monolith)'],
                    datasets: [
                        {
                            label: 'Reported Correct',
                            data: [mas.reported_correct || 8, sas.reported_correct || 81],
                            backgroundColor: '#10b981'
                        },
                        {
                            label: 'Reported Wrong',
                            data: [mas.wrong || 34, sas.wrong || 58],
                            backgroundColor: '#f43f5e'
                        },
                        {
                            label: 'Withheld by Policy',
                            data: [mas.withheld || 118, sas.withheld || 21],
                            backgroundColor: '#f59e0b'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { color: '#94a3b8', font: { size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (c) => ` ${c.dataset.label}: ${c.raw} cases (${((c.raw/160)*100).toFixed(1)}%)`
                            }
                        }
                    },
                    scales: {
                        x: { stacked: true, grid: { color: '#1e293b' }, ticks: { color: '#cbd5e1' } },
                        y: { stacked: true, max: 160, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        // Chart 2: Cross Tier
        const ctx2 = document.getElementById('overview-tier-chart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['8 GB (Adapted FinQA)', '16 GB (Pretrained FinQA)'],
                    datasets: [
                        {
                            label: 'MAS-FP16 Acc %',
                            data: [15.4, 5.0],
                            backgroundColor: '#10b981'
                        },
                        {
                            label: 'SAS-Quant Acc %',
                            data: [19.2, 50.6],
                            backgroundColor: '#8b5cf6'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { color: '#94a3b8', font: { size: 11 } } }
                    },
                    scales: {
                        x: { grid: { color: '#1e293b' }, ticks: { color: '#cbd5e1' } },
                        y: { max: 60, grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', callback: v => v + '%' } }
                    }
                }
            });
        }
    }
});

