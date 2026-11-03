/**
 * Datasets Page - Visual Research Dashboard
 */

window.App.registerPage('datasets', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const companies = aggr ? aggr.company_breakdown : [];

        container.innerHTML = `
            <!-- Dataset Profiles Cards Strip -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">
                        <span>FinQA Benchmark</span>
                        <span class="badge badge-mas">SEC 10-K</span>
                    </div>
                    <div class="stat-card-value text-[#2563EB]">160 Cases</div>
                    <div class="stat-card-meta">50 Corporate 10-K Annual Filings</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 100%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#3B82F6]">
                    <div class="stat-card-label">
                        <span>Agere-KYC-Synth</span>
                        <span class="badge badge-sas">Compliance</span>
                    </div>
                    <div class="stat-card-value text-[#3B82F6]">100 Cases</div>
                    <div class="stat-card-meta">CDD/EDD sanctions screening packs</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#3B82F6]" style="width: 62.5%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#7C3AED]">
                    <div class="stat-card-label">
                        <span>Agere-Credit-Synth</span>
                        <span class="badge" style="background:#F5F3FF; color:#7C3AED; border:1px solid #DDD6FE;">Spreads</span>
                    </div>
                    <div class="stat-card-value text-[#7C3AED]">75 Files</div>
                    <div class="stat-card-meta">DSCR spreading & covenant audits</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#7C3AED]" style="width: 46.8%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#D97706]">
                    <div class="stat-card-label">
                        <span>FRAMES / MortarBench</span>
                        <span class="badge badge-withheld">Control</span>
                    </div>
                    <div class="stat-card-value text-[#D97706]">100 Qs</div>
                    <div class="stat-card-meta">Multi-hop retrieval negative control</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#D97706]" style="width: 62.5%;"></div>
                    </div>
                </div>
            </div>

            <!-- Company Representation Chart & Table -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div class="card lg:col-span-6">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Company Evaluation Coverage (Top 8 Corpora)</h3>
                            <p class="text-xs text-[#64748B]">Case frequency per company report</p>
                        </div>
                        <span class="badge badge-mas">Representation</span>
                    </div>
                    <div class="h-64 mt-4">
                        <canvas id="company-coverage-chart"></canvas>
                    </div>
                </div>

                <div class="card lg:col-span-6">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Corporate Accuracy & Withholding</h3>
                            <p class="text-xs text-[#64748B]">Comparative outcome rates by company</p>
                        </div>
                        <span class="badge badge-sas">Per-Company</span>
                    </div>
                    <div class="table-container max-h-64 overflow-y-auto mt-4">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Company</th>
                                    <th>Cases</th>
                                    <th>MAS Acc %</th>
                                    <th>SAS Acc %</th>
                                    <th>MAS Withheld</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${companies.slice(0, 10).map(c => `
                                    <tr>
                                        <td class="font-mono text-xs font-bold text-[#172033]">${c.company}</td>
                                        <td class="font-mono text-xs text-[#64748B]">${c.sas_total}</td>
                                        <td class="font-mono text-xs text-[#2563EB] font-semibold">${c.mas_correct_pct}%</td>
                                        <td class="font-mono text-xs text-[#15803D] font-semibold">${c.sas_correct_pct}%</td>
                                        <td class="font-mono text-xs text-[#D97706] font-semibold">${c.mas_withheld_pct}%</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        this.renderChart(companies);
    },

    renderChart(companies) {
        const ctx = document.getElementById('company-coverage-chart');
        if (!ctx) return;

        const top8 = companies.slice(0, 8);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top8.map(c => c.company),
                datasets: [
                    {
                        label: 'Cases Evaluated',
                        data: top8.map(c => c.sas_total),
                        backgroundColor: '#2563EB',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { display: false },
                    tooltip: { backgroundColor: '#172033', titleColor: '#FFFFFF', bodyColor: '#F8FAFC', padding: 10 }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#64748B', font: { size: 10, family: 'Inter' } } },
                    y: { grid: { color: '#E9EEF5' }, ticks: { color: '#64748B', font: { size: 10, family: 'JetBrains Mono' } } }
                }
            }
        });
    }
});