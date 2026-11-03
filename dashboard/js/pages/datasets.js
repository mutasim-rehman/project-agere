/**
 * Datasets, Financial Reports & Splits Page - Minimal, Plain, Publication-Grade
 */

window.App.registerPage('datasets', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const companies = aggr ? aggr.company_breakdown : [];

        container.innerHTML = `
            <!-- Top Summary Card (Plain, Structured) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Financial Benchmark Suite</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Regulated Finance Tasks & Document Splits
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            Evaluations test complex numerical reasoning and grounding over real corporate financial filings (SEC 10-K), synthetic KYC compliance packs, credit memo spreading, and negative control multi-hop tasks.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Dataset Profiles Cards (Plain, Clean Borders) -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-400 font-mono">SEC 10-K Filings</span>
                        <span class="badge badge-mas">Benchmark 1</span>
                    </div>
                    <div class="font-semibold text-sm text-white mt-2">FinQA Benchmark</div>
                    <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                        Numerical reasoning over earnings reports requiring multi-step arithmetic over tables and narrative text.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono">
                        160 Unique Questions • 50 10-Ks
                    </div>
                </div>

                <div class="card p-4">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-400 font-mono">Synthetic PII</span>
                        <span class="badge badge-sas">Benchmark 2</span>
                    </div>
                    <div class="font-semibold text-sm text-white mt-2">Agere-KYC-Synth</div>
                    <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                        Customer Due Diligence (CDD/EDD) case-file assembly, sanctions screening summaries, and discrepancy registers.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono">
                        100 Synthetic Cases • JSONL
                    </div>
                </div>

                <div class="card p-4">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-400 font-mono">Underwriting Spreads</span>
                        <span class="badge badge-sas">Benchmark 3</span>
                    </div>
                    <div class="font-semibold text-sm text-white mt-2">Agere-Credit-Synth</div>
                    <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                        Borrower financials spreading, debt-service coverage (DSCR) calculations, and loan covenant checks.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono">
                        75 Synthetic Files • Spreads
                    </div>
                </div>

                <div class="card p-4">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-400 font-mono">Multi-Hop Control</span>
                        <span class="badge badge-withheld">Negative Control</span>
                    </div>
                    <div class="font-semibold text-sm text-white mt-2">FRAMES & MortarBench</div>
                    <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                        Multi-hop document retrieval and origination validation where large monolithic models are expected to excel.
                    </p>
                    <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono">
                        100 Question Slice • Public
                    </div>
                </div>
            </div>

            <!-- Company Representation Chart & Table -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-semibold text-white">Company Evaluation Coverage (Top 8)</h3>
                        <p class="text-xs text-slate-400">Total cases tested across corporate reports</p>
                    </div>
                    <div class="h-64 mt-4">
                        <canvas id="company-coverage-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-semibold text-white">Per-Company Accuracy Breakdown</h3>
                        <p class="text-xs text-slate-400">MAS accuracy vs SAS accuracy by corporation</p>
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
                                        <td class="font-mono text-xs font-semibold text-white">${c.company}</td>
                                        <td class="font-mono text-xs text-slate-400">${c.sas_total}</td>
                                        <td class="font-mono text-xs text-white font-medium">${c.mas_correct_pct}%</td>
                                        <td class="font-mono text-xs text-white font-medium">${c.sas_correct_pct}%</td>
                                        <td class="font-mono text-xs text-amber-400">${c.mas_withheld_pct}%</td>
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
                        backgroundColor: '#388bfd',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#8b949e', font: { size: 11 } } },
                    y: { grid: { color: '#242c38' }, ticks: { color: '#8b949e', font: { size: 11 } } }
                }
            }
        });
    }
});
