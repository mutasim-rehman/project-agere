/**
 * Datasets Page - Academic Light Theme
 */

window.App.registerPage('datasets', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const companies = aggr ? aggr.company_breakdown : [];

        container.innerHTML = `
            <!-- Top Summary Card (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="space-y-1 max-w-4xl">
                    <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                        Benchmark Suite & Financial Corpora
                    </div>
                    <h2 class="text-base font-bold text-[#172033]">
                        Regulated Financial Workflows & Document Splits
                    </h2>
                    <p class="text-xs text-[#64748B] leading-relaxed">
                        Evaluations test complex numerical reasoning and grounding over real corporate financial filings (SEC 10-K), synthetic KYC compliance packs, credit memo spreading, and negative control multi-hop tasks.
                    </p>
                </div>
            </div>

            <!-- Dataset Profiles Cards (Plain, Clean Borders) -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="card p-4 border-t-4 border-t-[#2563EB]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#64748B] font-mono">SEC 10-K Filings</span>
                        <span class="badge badge-mas">Benchmark 1</span>
                    </div>
                    <div class="font-bold text-sm text-[#2563EB] mt-2">FinQA Benchmark</div>
                    <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                        Numerical reasoning over earnings reports requiring multi-step arithmetic over tables and narrative text.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono">
                        160 Unique Questions • 50 10-Ks
                    </div>
                </div>

                <div class="card p-4 border-t-4 border-t-[#3B82F6]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#64748B] font-mono">Synthetic PII</span>
                        <span class="badge badge-sas">Benchmark 2</span>
                    </div>
                    <div class="font-bold text-sm text-[#3B82F6] mt-2">Agere-KYC-Synth</div>
                    <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                        Customer Due Diligence (CDD/EDD) case-file assembly, sanctions screening summaries, and discrepancy registers.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono">
                        100 Synthetic Cases • JSONL
                    </div>
                </div>

                <div class="card p-4 border-t-4 border-t-[#7C3AED]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#64748B] font-mono">Underwriting Spreads</span>
                        <span class="badge" style="background:#F5F3FF; color:#7C3AED; border:1px solid #DDD6FE;">Benchmark 3</span>
                    </div>
                    <div class="font-bold text-sm text-[#7C3AED] mt-2">Agere-Credit-Synth</div>
                    <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                        Borrower financials spreading, debt-service coverage (DSCR) calculations, and loan covenant checks.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono">
                        75 Synthetic Files • Spreads
                    </div>
                </div>

                <div class="card p-4 border-t-4 border-t-[#D97706]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#64748B] font-mono">Multi-Hop Control</span>
                        <span class="badge badge-withheld">Control</span>
                    </div>
                    <div class="font-bold text-sm text-[#D97706] mt-2">FRAMES & MortarBench</div>
                    <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                        Multi-hop document retrieval and origination validation where large monolithic models are expected to excel.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono">
                        100 Question Slice • Public
                    </div>
                </div>
            </div>

            <!-- Company Representation Chart & Table -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Company Evaluation Coverage (Top 8)</h3>
                            <p class="text-xs text-[#64748B]">Total cases tested across corporate reports</p>
                        </div>
                    </div>
                    <div class="h-64 mt-4">
                        <canvas id="company-coverage-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Per-Company Accuracy Breakdown</h3>
                            <p class="text-xs text-[#64748B]">MAS accuracy vs SAS accuracy by corporation</p>
                        </div>
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
                                        <td class="font-mono text-xs text-[#172033] font-semibold">${c.sas_correct_pct}%</td>
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
                    tooltip: { backgroundColor: '#172033', titleColor: '#FFFFFF', bodyColor: '#F8FAFC' }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#64748B', font: { size: 11, family: 'Inter' } } },
                    y: { grid: { color: '#E9EEF5' }, ticks: { color: '#64748B', font: { size: 11, family: 'JetBrains Mono' } } }
                }
            }
        });
    }
});
