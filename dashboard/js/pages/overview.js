/**
 * Executive Overview Page - Academic Light Theme
 */

window.App.registerPage('overview', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const jobs = aggr ? aggr.jobs_16gb : {};

        const mas = jobs['tier16-mas-primary'] || {};
        const sas = jobs['tier16-sas-primary'] || {};

        container.innerHTML = `
            <!-- Research Question Panel (Clean Scientific Summary) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                    <div class="space-y-1.5 max-w-4xl">
                        <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                            Primary Empirical Research Question
                        </div>
                        <h2 class="text-lg font-bold text-[#172033] tracking-tight">
                            Multi-Agent Full-Precision Teams vs. Quantized Monoliths on Analyst RAM
                        </h2>
                        <p class="text-xs text-[#64748B] leading-relaxed">
                            Banks and regulated funds that cannot use cloud APIs on KYC and credit files default to a single large quantized model on local analyst workstations. We experimentally evaluate whether an orchestrated team of smaller full-precision specialist agents (Extractor, Drafter, Verifier) outperforms the monolithic default under the identical host-adjusted process-tree RSS cap (12.8 GB on 16 GB machines; 6.4 GB on 8 GB machines) and matched thinking-token budgets.
                        </p>
                    </div>
                    <div class="shrink-0 flex flex-col sm:flex-row lg:flex-col gap-2 font-mono text-xs">
                        <div class="px-3 py-1.5 rounded bg-[#F8FAFC] border border-[#E2E8F0] text-[#172033]">
                            <span class="text-[#64748B]">Protocol:</span> <strong class="text-[#2563EB]">RUPP Parity</strong>
                        </div>
                        <div class="px-3 py-1.5 rounded bg-[#F8FAFC] border border-[#E2E8F0] text-[#172033]">
                            <span class="text-[#64748B]">RAM Cap:</span> <strong class="text-[#172033]">12.8 GB (80% RSS)</strong>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 4 Primary Research KPI Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- KPI 1: Accuracy Delta -->
                <div class="stat-card border-l-4 border-l-[#DC2626]">
                    <div class="stat-card-label">16 GB Accuracy Delta (MAS - SAS)</div>
                    <div class="stat-card-value text-[#DC2626]">-45.6%</div>
                    <div class="stat-card-meta">
                        Holm-adjusted <span class="text-[#172033] font-semibold">p = 6.10e-5</span> • n = 160
                    </div>
                    <p class="text-[11px] text-[#64748B] mt-2 pt-2 border-t border-[#F1F5F9] leading-tight">
                        Statistically significant performance disadvantage for MAS under matched RAM.
                    </p>
                </div>

                <!-- KPI 2: SAS Accuracy -->
                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">SAS 14B Monolith Accuracy</div>
                    <div class="stat-card-value text-[#172033]">50.6%</div>
                    <div class="stat-card-meta">
                        <span class="text-[#2563EB] font-semibold">81 / 160</span> correct • Denominator n = 160
                    </div>
                    <p class="text-[11px] text-[#64748B] mt-2 pt-2 border-t border-[#F1F5F9] leading-tight">
                        Qwen2.5-14B-Instruct (GGUF Q4_K_M) delivering answers on 86.9% of cases.
                    </p>
                </div>

                <!-- KPI 3: MAS Accuracy -->
                <div class="stat-card border-l-4 border-l-[#64748B]">
                    <div class="stat-card-label">MAS 3-Agent Team Accuracy</div>
                    <div class="stat-card-value text-[#172033]">5.0%</div>
                    <div class="stat-card-meta">
                        <span class="text-[#172033] font-semibold">8 / 160</span> correct • Denominator n = 160
                    </div>
                    <p class="text-[11px] text-[#64748B] mt-2 pt-2 border-t border-[#F1F5F9] leading-tight">
                        Full-precision team: 1.5B Extractor + 7B Drafter + 3B Verifier (FP16).
                    </p>
                </div>

                <!-- KPI 4: MAS Withholding -->
                <div class="stat-card border-l-4 border-l-[#D97706]">
                    <div class="stat-card-label">MAS Policy Withholding Rate</div>
                    <div class="stat-card-value text-[#D97706]">73.8%</div>
                    <div class="stat-card-meta">
                        <span class="text-[#D97706] font-semibold">118 / 160</span> withheld by verifier
                    </div>
                    <p class="text-[11px] text-[#64748B] mt-2 pt-2 border-t border-[#F1F5F9] leading-tight">
                        Conservative verifier rejection, not incorrect arithmetic, drives low accuracy.
                    </p>
                </div>
            </div>

            <!-- Publication Charts Row -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Chart 1: 16 GB Evaluation Outcome Breakdown -->
                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">16 GB Evaluation Outcome Breakdown</h3>
                            <p class="text-xs text-[#64748B]">Correct vs Incorrect vs Withheld (n = 160 per deployment arm)</p>
                        </div>
                        <span class="badge badge-sas">Dual-Metric</span>
                    </div>
                    <div class="pt-4">
                        <div class="w-full h-64">
                            <canvas id="overview-outcome-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Chart 2: Accuracy by Hardware RAM Tier -->
                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Accuracy by Hardware RAM Tier</h3>
                            <p class="text-xs text-[#64748B]">8 GB Adapted Natural FinQA vs 16 GB Pretrained FinQA</p>
                        </div>
                        <span class="badge badge-mas">Cross-Tier</span>
                    </div>
                    <div class="pt-4">
                        <div class="w-full h-64">
                            <canvas id="overview-tier-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Deployment Specifications Table -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Comparative Deployment Specifications (16 GB Analyst Tier)</h3>
                        <p class="text-xs text-[#64748B]">Process-tree RSS constrained to 12.8 GB after 20% host OS reservation</p>
                    </div>
                </div>
                <div class="table-container mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Deployment Arm</th>
                                <th>Architecture Role</th>
                                <th>Model & Precision</th>
                                <th>Process RSS Cap</th>
                                <th>Reported Correct</th>
                                <th>Incorrect Delivery</th>
                                <th>Policy Withheld</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><span class="badge badge-mas">MAS-FP16</span></td>
                                <td class="font-medium text-[#172033]">Specialized Team (Extractor + Drafter + Verifier)</td>
                                <td class="font-mono text-xs">Qwen2.5 1.5B + 7B + 3B (FP16)</td>
                                <td class="font-mono text-xs">12.8 GB</td>
                                <td class="font-mono text-xs font-semibold text-[#15803D]">5.0% (8/160)</td>
                                <td class="font-mono text-xs font-semibold text-[#DC2626]">21.3% (34/160)</td>
                                <td class="font-mono text-xs font-semibold text-[#D97706]">73.8% (118/160)</td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-sas">SAS-Quant</span></td>
                                <td class="font-medium text-[#172033]">Single Monolith (Standard Baseline)</td>
                                <td class="font-mono text-xs">Qwen2.5-14B (GGUF Q4_K_M)</td>
                                <td class="font-mono text-xs">12.8 GB</td>
                                <td class="font-mono text-xs font-semibold text-[#15803D]">50.6% (81/160)</td>
                                <td class="font-mono text-xs font-semibold text-[#DC2626]">36.3% (58/160)</td>
                                <td class="font-mono text-xs text-[#64748B]">13.1% (21/160)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.renderCharts(mas, sas);
    },

    renderCharts(mas, sas) {
        // Chart 1: Outcome Breakdown (Clean Academic Theme)
        const ctx1 = document.getElementById('overview-outcome-chart');
        if (ctx1) {
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['MAS-FP16 (Specialist Team)', 'SAS-Quant (Monolith Baseline)'],
                    datasets: [
                        {
                            label: 'Correct Answer',
                            data: [mas.reported_correct || 8, sas.reported_correct || 81],
                            backgroundColor: '#15803D',
                            borderRadius: 4
                        },
                        {
                            label: 'Incorrect Answer',
                            data: [mas.wrong || 34, sas.wrong || 58],
                            backgroundColor: '#DC2626',
                            borderRadius: 4
                        },
                        {
                            label: 'Withheld by Policy',
                            data: [mas.withheld || 118, sas.withheld || 21],
                            backgroundColor: '#D97706',
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'top', 
                            labels: { color: '#64748B', font: { size: 11, family: 'Inter' }, boxWidth: 12 } 
                        },
                        tooltip: {
                            backgroundColor: '#172033',
                            titleColor: '#FFFFFF',
                            bodyColor: '#F8FAFC',
                            borderColor: '#E2E8F0',
                            borderWidth: 1,
                            padding: 10,
                            callbacks: {
                                label: (c) => ` ${c.dataset.label}: ${c.raw} cases (${((c.raw/160)*100).toFixed(1)}%)`
                            }
                        }
                    },
                    scales: {
                        x: { 
                            stacked: true, 
                            grid: { display: false }, 
                            ticks: { color: '#64748B', font: { size: 11, family: 'Inter' } } 
                        },
                        y: { 
                            stacked: true, 
                            max: 160, 
                            grid: { color: '#E9EEF5' }, 
                            ticks: { color: '#64748B', font: { size: 11, family: 'JetBrains Mono' } } 
                        }
                    }
                }
            });
        }

        // Chart 2: Accuracy by Hardware Tier
        const ctx2 = document.getElementById('overview-tier-chart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['8 GB Tier (Adapted Cohort)', '16 GB Tier (Pretrained Cohort)'],
                    datasets: [
                        {
                            label: 'MAS-FP16 Accuracy %',
                            data: [15.4, 5.0],
                            backgroundColor: '#2563EB',
                            borderRadius: 4
                        },
                        {
                            label: 'SAS-Quant Accuracy %',
                            data: [19.2, 50.6],
                            backgroundColor: '#64748B',
                            borderRadius: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { 
                            position: 'top', 
                            labels: { color: '#64748B', font: { size: 11, family: 'Inter' }, boxWidth: 12 } 
                        },
                        tooltip: {
                            backgroundColor: '#172033',
                            titleColor: '#FFFFFF',
                            bodyColor: '#F8FAFC',
                            borderColor: '#E2E8F0',
                            borderWidth: 1,
                            padding: 10
                        }
                    },
                    scales: {
                        x: { 
                            grid: { display: false }, 
                            ticks: { color: '#64748B', font: { size: 11, family: 'Inter' } } 
                        },
                        y: { 
                            max: 60, 
                            grid: { color: '#E9EEF5' }, 
                            ticks: { color: '#64748B', callback: v => v + '%', font: { size: 11, family: 'JetBrains Mono' } } 
                        }
                    }
                }
            });
        }
    }
});
