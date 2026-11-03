/**
 * Executive Overview Page - Minimal, Plain, Publication-Grade
 */

window.App.registerPage('overview', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const kpis = aggr ? aggr.kpis : {};
        const jobs = aggr ? aggr.jobs_16gb : {};

        const mas = jobs['tier16-mas-primary'] || {};
        const sas = jobs['tier16-sas-primary'] || {};

        container.innerHTML = `
            <!-- Research Context Box (Plain, Crisp, Professional) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Research Question & Framing</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst RAM
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            We evaluate whether a specialized team of smaller full-precision LLMs outperforms a single larger quantized generalist under identical host-adjusted process RSS limits (12.8 GB / 6.4 GB) and thinking-token budgets on regulated financial document tasks.
                        </p>
                    </div>
                    <div class="shrink-0 flex items-center gap-2">
                        <span class="badge badge-sas">RUPP Protocol</span>
                        <span class="badge badge-mas">16 GB Primary Cohort</span>
                    </div>
                </div>
            </div>

            <!-- Primary 4 Metrics (High Data-to-Ink Ratio) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">16 GB Accuracy Delta (MAS - SAS)</div>
                    <div class="text-2xl font-bold font-mono text-rose-400 mt-2">-45.6%</div>
                    <div class="text-xs text-slate-400 font-mono mt-1">Holm p = 6.10e-5 (Sig)</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">SAS 14B Monolith Accuracy</div>
                    <div class="text-2xl font-bold font-mono text-slate-200 mt-2">50.6%</div>
                    <div class="text-xs text-slate-400 font-mono mt-1">81 of 160 questions correct</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">MAS 3-Agent Team Accuracy</div>
                    <div class="text-2xl font-bold font-mono text-slate-200 mt-2">5.0%</div>
                    <div class="text-xs text-slate-400 font-mono mt-1">8 of 160 questions correct</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">MAS Policy Withholding Rate</div>
                    <div class="text-2xl font-bold font-mono text-amber-400 mt-2">73.8%</div>
                    <div class="text-xs text-slate-400 font-mono mt-1">118 of 160 withheld</div>
                </div>
            </div>

            <!-- Minimalist Charts Row -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Chart 1: Outcome Breakdown -->
                <div class="card">
                    <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                        <div>
                            <h3 class="text-sm font-semibold text-white">16 GB Evaluation Outcome Breakdown</h3>
                            <p class="text-xs text-slate-400">Reported Correct vs Wrong vs Withheld by Policy (n = 160 per arm)</p>
                        </div>
                    </div>
                    <div class="pt-4">
                        <div class="w-full h-64">
                            <canvas id="overview-outcome-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Chart 2: Cross Tier Comparison -->
                <div class="card">
                    <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                        <div>
                            <h3 class="text-sm font-semibold text-white">Accuracy by Hardware RAM Tier</h3>
                            <p class="text-xs text-slate-400">8 GB Adapted FinQA vs 16 GB Pretrained FinQA</p>
                        </div>
                    </div>
                    <div class="pt-4">
                        <div class="w-full h-64">
                            <canvas id="overview-tier-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Plain Comparative Architecture Table -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Deployment Specifications (16 GB Analyst Workstation)</h3>
                    <p class="text-xs text-slate-400">Both arms tested under identical 12.8 GB process-tree RSS limits with 20% host OS reservation</p>
                </div>
                <div class="table-container mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Deployment Arm</th>
                                <th>Architecture Role</th>
                                <th>Models & Quantization</th>
                                <th>Process RSS Cap</th>
                                <th>Reported Correct</th>
                                <th>Wrong Delivery</th>
                                <th>Withheld Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><span class="badge badge-mas">MAS-FP16</span></td>
                                <td class="font-medium text-white">Specialized Team (Extractor + Drafter + Verifier)</td>
                                <td class="font-mono text-xs">Qwen2.5 1.5B + 7B + 3B (F16)</td>
                                <td class="font-mono text-xs">12.8 GB</td>
                                <td class="font-mono text-xs text-white">5.0% (8/160)</td>
                                <td class="font-mono text-xs text-rose-400">21.3% (34/160)</td>
                                <td class="font-mono text-xs text-amber-400 font-semibold">73.8% (118/160)</td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-sas">SAS-Quant</span></td>
                                <td class="font-medium text-white">Single Monolith (Standard Baseline)</td>
                                <td class="font-mono text-xs">Qwen2.5-14B (GGUF Q4_K_M)</td>
                                <td class="font-mono text-xs">12.8 GB</td>
                                <td class="font-mono text-xs text-white font-semibold">50.6% (81/160)</td>
                                <td class="font-mono text-xs text-rose-400">36.3% (58/160)</td>
                                <td class="font-mono text-xs text-slate-400">13.1% (21/160)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.renderCharts(mas, sas);
    },

    renderCharts(mas, sas) {
        // Chart 1: Outcome Breakdown (Clean, Flat, Plain Tones)
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
                            backgroundColor: '#3fb950',
                            borderRadius: 4
                        },
                        {
                            label: 'Reported Wrong',
                            data: [mas.wrong || 34, sas.wrong || 58],
                            backgroundColor: '#f85149',
                            borderRadius: 4
                        },
                        {
                            label: 'Withheld by Policy',
                            data: [mas.withheld || 118, sas.withheld || 21],
                            backgroundColor: '#d29922',
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { color: '#8b949e', font: { size: 11, family: 'Inter' }, boxWidth: 12 } }
                    },
                    scales: {
                        x: { stacked: true, grid: { display: false }, ticks: { color: '#8b949e', font: { size: 11 } } },
                        y: { stacked: true, max: 160, grid: { color: '#242c38' }, ticks: { color: '#8b949e', font: { size: 11 } } }
                    }
                }
            });
        }

        // Chart 2: Cross Tier (Clean Academic Bars)
        const ctx2 = document.getElementById('overview-tier-chart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['8 GB Tier (Adapted)', '16 GB Tier (Pretrained)'],
                    datasets: [
                        {
                            label: 'MAS-FP16 Accuracy %',
                            data: [15.4, 5.0],
                            backgroundColor: '#388bfd',
                            borderRadius: 4
                        },
                        {
                            label: 'SAS-Quant Accuracy %',
                            data: [19.2, 50.6],
                            backgroundColor: '#6e7681',
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { color: '#8b949e', font: { size: 11, family: 'Inter' }, boxWidth: 12 } }
                    },
                    scales: {
                        x: { grid: { display: false }, ticks: { color: '#8b949e', font: { size: 11 } } },
                        y: { max: 60, grid: { color: '#242c38' }, ticks: { color: '#8b949e', callback: v => v + '%', font: { size: 11 } } }
                    }
                }
            });
        }
    }
});
