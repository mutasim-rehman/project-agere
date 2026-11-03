/**
 * Executive Overview Page - Visual Research Dashboard
 */

window.App.registerPage('overview', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const jobs = aggr ? aggr.jobs_16gb : {};

        const mas = jobs['tier16-mas-primary'] || {};
        const sas = jobs['tier16-sas-primary'] || {};

        container.innerHTML = `
            <!-- 4 Primary Research KPI Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <!-- KPI 1: Accuracy Delta -->
                <div class="stat-card border-l-4 border-l-[#DC2626]">
                    <div class="stat-card-label">
                        <span>Accuracy Delta (MAS - SAS)</span>
                        <span class="badge badge-wrong">p = 6.10e-5</span>
                    </div>
                    <div class="stat-card-value text-[#DC2626]">-45.6%</div>
                    <div class="stat-card-meta">
                        Holm-adjusted significance • n = 160
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#DC2626]" style="width: 45.6%;"></div>
                    </div>
                </div>

                <!-- KPI 2: SAS Accuracy -->
                <div class="stat-card border-l-4 border-l-[#15803D]">
                    <div class="stat-card-label">
                        <span>SAS 14B Monolith</span>
                        <span class="badge badge-correct">Q4_K_M</span>
                    </div>
                    <div class="stat-card-value text-[#15803D]">50.6%</div>
                    <div class="stat-card-meta">
                        81 / 160 correct answers
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#15803D]" style="width: 50.6%;"></div>
                    </div>
                </div>

                <!-- KPI 3: MAS Accuracy -->
                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">
                        <span>MAS 3-Agent Team</span>
                        <span class="badge badge-mas">FP16</span>
                    </div>
                    <div class="stat-card-value text-[#2563EB]">5.0%</div>
                    <div class="stat-card-meta">
                        8 / 160 correct answers
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 5.0%;"></div>
                    </div>
                </div>

                <!-- KPI 4: MAS Withholding -->
                <div class="stat-card border-l-4 border-l-[#D97706]">
                    <div class="stat-card-label">
                        <span>MAS Policy Withholding</span>
                        <span class="badge badge-withheld">Verifier Gate</span>
                    </div>
                    <div class="stat-card-value text-[#D97706]">73.8%</div>
                    <div class="stat-card-meta">
                        118 / 160 withheld by verifier
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#D97706]" style="width: 73.8%;"></div>
                    </div>
                </div>
            </div>

            <!-- Primary Visual Row: Outcome Breakdown & Donut Distribution -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Visual 1: 16 GB Evaluation Outcome Breakdown -->
                <div class="card lg:col-span-7">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">16 GB Evaluation Outcome Breakdown</h3>
                            <p class="text-xs text-[#64748B]">Correct vs Incorrect vs Withheld (n = 160 cases per arm)</p>
                        </div>
                        <span class="badge badge-sas">Dual-Metric</span>
                    </div>
                    <div class="pt-4">
                        <div class="w-full h-72">
                            <canvas id="overview-outcome-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Visual 2: MAS vs SAS Decision Distribution Donut -->
                <div class="card lg:col-span-5 flex flex-col justify-between">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Decision Outcome Proportions</h3>
                            <p class="text-xs text-[#64748B]">MAS Team verifier withholding vs SAS baseline</p>
                        </div>
                        <span class="badge badge-mas">Distribution</span>
                    </div>
                    <div class="pt-3 flex-1 flex items-center justify-center">
                        <div class="w-full h-64">
                            <canvas id="overview-donut-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Secondary Visual Row: Cross-Tier Comparison & Comparative Specifications -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Visual 3: Hardware RAM Tier Comparison Chart -->
                <div class="card lg:col-span-6">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Accuracy by Hardware RAM Tier</h3>
                            <p class="text-xs text-[#64748B]">8 GB Adapted Natural FinQA vs 16 GB Pretrained FinQA</p>
                        </div>
                        <span class="badge badge-mas">Hardware Scaling</span>
                    </div>
                    <div class="pt-4">
                        <div class="w-full h-64">
                            <canvas id="overview-tier-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Visual 4: Comparative Architecture Cards -->
                <div class="card lg:col-span-6 flex flex-col justify-between">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Deployment Arm Comparison (16 GB Analyst Tier)</h3>
                            <p class="text-xs text-[#64748B]">Constrained to 12.8 GB process-tree RSS cap</p>
                        </div>
                        <span class="badge badge-sas">12.8 GB RSS</span>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-4">
                        <!-- MAS Spec Card -->
                        <div class="p-4 rounded-lg bg-[#EFF6FF] border border-[#BFDBFE] space-y-2.5">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-xs text-[#2563EB] uppercase font-mono">MAS-FP16 Team</span>
                                <span class="badge badge-mas">3 Models</span>
                            </div>
                            <div class="text-xs text-[#172033] font-medium">Qwen2.5 1.5B + 7B + 3B (FP16)</div>
                            <div class="space-y-1.5 pt-2 border-t border-[#DBEAFE] text-xs font-mono">
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Accuracy:</span>
                                    <strong class="text-[#2563EB]">5.0% (8/160)</strong>
                                </div>
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Withheld:</span>
                                    <strong class="text-[#D97706]">73.8% (118/160)</strong>
                                </div>
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Peak RSS:</span>
                                    <strong class="text-[#172033]">10.18 GB</strong>
                                </div>
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Avg Latency:</span>
                                    <strong class="text-[#172033]">367.6s / correct</strong>
                                </div>
                            </div>
                        </div>

                        <!-- SAS Spec Card -->
                        <div class="p-4 rounded-lg bg-[#F8FAFC] border border-[#E2E8F0] space-y-2.5">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-xs text-[#64748B] uppercase font-mono">SAS-Quant Monolith</span>
                                <span class="badge badge-sas">Single 14B</span>
                            </div>
                            <div class="text-xs text-[#172033] font-medium">Qwen2.5-14B (GGUF Q4_K_M)</div>
                            <div class="space-y-1.5 pt-2 border-t border-[#E2E8F0] text-xs font-mono">
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Accuracy:</span>
                                    <strong class="text-[#15803D]">50.6% (81/160)</strong>
                                </div>
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Withheld:</span>
                                    <strong class="text-[#172033]">13.1% (21/160)</strong>
                                </div>
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Peak RSS:</span>
                                    <strong class="text-[#172033]">9.37 GB</strong>
                                </div>
                                <div class="flex justify-between text-[#64748B]">
                                    <span>Avg Latency:</span>
                                    <strong class="text-[#15803D]">54.1s / correct (6.8x)</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        this.renderCharts(mas, sas);
    },

    renderCharts(mas, sas) {
        // Chart 1: Outcome Breakdown (Bar Chart)
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

        // Chart 2: Outcome Proportions Donut Chart
        const ctxDonut = document.getElementById('overview-donut-chart');
        if (ctxDonut) {
            new Chart(ctxDonut, {
                type: 'doughnut',
                data: {
                    labels: ['MAS Withheld (73.8%)', 'MAS Incorrect (21.3%)', 'MAS Correct (5.0%)', 'SAS Correct (50.6%)', 'SAS Incorrect (36.3%)', 'SAS Withheld (13.1%)'],
                    datasets: [{
                        data: [118, 34, 8, 81, 58, 21],
                        backgroundColor: [
                            '#D97706', // MAS Withheld
                            '#EF4444', // MAS Incorrect
                            '#2563EB', // MAS Correct
                            '#15803D', // SAS Correct
                            '#F87171', // SAS Incorrect
                            '#FBBF24'  // SAS Withheld
                        ],
                        borderWidth: 2,
                        borderColor: '#FFFFFF'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#64748B',
                                font: { size: 10, family: 'Inter' },
                                boxWidth: 10,
                                padding: 8
                            }
                        },
                        tooltip: {
                            backgroundColor: '#172033',
                            titleColor: '#FFFFFF',
                            bodyColor: '#F8FAFC',
                            borderColor: '#E2E8F0',
                            borderWidth: 1,
                            padding: 10,
                            callbacks: {
                                label: (c) => ` ${c.label}: ${c.raw} cases (${((c.raw/160)*100).toFixed(1)}%)`
                            }
                        }
                    },
                    cutout: '62%'
                }
            });
        }

        // Chart 3: Accuracy by Hardware Tier
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