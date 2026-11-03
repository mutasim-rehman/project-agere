/**
 * Datasets, Financial Reports & Splits Page
 */

window.App.registerPage('datasets', {
    async render(container, app) {
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const companies = aggr ? aggr.company_breakdown : [];
        const manifests = await app.fetchJson('data/manifests_summary.json') || {};

        container.innerHTML = `
            <!-- Top Summary Card -->
            <div class="card bg-gradient-to-r from-slate-900 to-emerald-950/20 border-emerald-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-mas">Benchmark Suite</span>
                            <span class="text-xs text-slate-400 font-mono">Regulated Finance Tasks</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Domain Workflows: FinQA, Agere-Synth & Negative Controls
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            Evaluations test complex numerical reasoning and grounding over real corporate financial filings (SEC 10-K), synthetic KYC compliance packs, credit memo spreading, and negative control multi-hop tasks.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Dataset Profiles Cards Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="card p-4 border-l-4 border-emerald-500">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-white uppercase font-mono">Benchmark 1</span>
                        <span class="badge badge-mas">SEC 10-K</span>
                    </div>
                    <div class="font-bold text-base text-emerald-400 mt-2">FinQA Benchmark</div>
                    <p class="text-xs text-slate-300 mt-1 leading-relaxed">
                        Numerical reasoning over earnings reports. Questions require multi-step arithmetic over tables and narrative text.
                    </p>
                    <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400 font-mono space-y-1">
                        <div>Cohort: <span class="text-white">160 Unique Questions</span></div>
                        <div>Reports: <span class="text-white">50 Corporate 10-Ks</span></div>
                    </div>
                </div>

                <div class="card p-4 border-l-4 border-cyan-500">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-white uppercase font-mono">Benchmark 2</span>
                        <span class="badge">Synthetic PII</span>
                    </div>
                    <div class="font-bold text-base text-cyan-400 mt-2">Agere-KYC-Synth</div>
                    <p class="text-xs text-slate-300 mt-1 leading-relaxed">
                        Customer Due Diligence (CDD/EDD) case-file assembly, sanctions screening summaries, and discrepancy registers.
                    </p>
                    <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400 font-mono space-y-1">
                        <div>Cohort: <span class="text-white">100 Synthetic Cases</span></div>
                        <div>Format: <span class="text-white">JSONL Structured</span></div>
                    </div>
                </div>

                <div class="card p-4 border-l-4 border-purple-500">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-white uppercase font-mono">Benchmark 3</span>
                        <span class="badge badge-sas">Underwriting</span>
                    </div>
                    <div class="font-bold text-base text-purple-400 mt-2">Agere-Credit-Synth</div>
                    <p class="text-xs text-slate-300 mt-1 leading-relaxed">
                        Commercial credit memo drafting: borrower financials spreading, debt-service coverage (DSCR) calculations, and covenant checks.
                    </p>
                    <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400 font-mono space-y-1">
                        <div>Cohort: <span class="text-white">75 Synthetic Files</span></div>
                        <div>Format: <span class="text-white">Multi-table Spreads</span></div>
                    </div>
                </div>

                <div class="card p-4 border-l-4 border-amber-500">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-white uppercase font-mono">Benchmark 4</span>
                        <span class="badge badge-withheld">Negative Control</span>
                    </div>
                    <div class="font-bold text-base text-amber-400 mt-2">FRAMES & MortarBench</div>
                    <p class="text-xs text-slate-300 mt-1 leading-relaxed">
                        Multi-hop document retrieval and origination validation. Used as negative control where large monolithic models are expected to excel.
                    </p>
                    <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400 font-mono space-y-1">
                        <div>Cohort: <span class="text-white">100 Question Slice</span></div>
                        <div>Source: <span class="text-white">External Public Test</span></div>
                    </div>
                </div>
            </div>

            <!-- Company Representation Chart & Table -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="building" class="w-4 h-4 text-emerald-400"></i>
                            Company Evaluation Coverage (Top 10)
                        </h3>
                    </div>
                    <div class="h-72 mt-4">
                        <canvas id="company-coverage-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="table" class="w-4 h-4 text-cyan-400"></i>
                            Per-Company Accuracy Breakdown
                        </h3>
                    </div>
                    <div class="table-container max-h-72 overflow-y-auto mt-4">
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
                                        <td class="font-mono text-xs font-bold text-white">${c.company}</td>
                                        <td class="font-mono text-xs">${c.sas_total}</td>
                                        <td class="font-mono text-xs text-emerald-400 font-bold">${c.mas_correct_pct}%</td>
                                        <td class="font-mono text-xs text-purple-400 font-bold">${c.sas_correct_pct}%</td>
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

        const top10 = companies.slice(0, 8);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: top10.map(c => c.company),
                datasets: [
                    {
                        label: 'Evaluated Cases',
                        data: top10.map(c => c.sas_total),
                        backgroundColor: '#38bdf8'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: '#1e293b' }, ticks: { color: '#cbd5e1' } },
                    y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                }
            }
        });
    }
});

