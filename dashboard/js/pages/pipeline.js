/**
 * Pipeline Stages & Token Cost Analysis Page - Minimal, Plain, Publication-Grade
 */

window.App.registerPage('pipeline', {
    async render(container, app) {
        const stageMetrics = await app.fetchJson('data/tier16_v2/stage_metrics.json') || [];

        container.innerHTML = `
            <!-- Top Summary (Plain, Structured) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Architecture & Latency</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Multi-Agent Stage Decomposition & Token Consumption
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            The MAS pipeline splits execution into three specialized roles: Extractor (evidence span selection), Drafter (arithmetic program generation), and Verifier (grounding and sanity check). Latency and token consumption are measured directly via CPU inference timers.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Pipeline Architecture Flow Diagram (Plain, Crisp) -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Execution Pipeline Flow (MAS-FP16)</h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border border-[var(--border-color)]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-white uppercase font-mono">Stage 1: Evidence</span>
                            <span class="badge badge-sas">1.5B F16</span>
                        </div>
                        <div class="font-semibold text-sm text-white mt-2">Extractor Role</div>
                        <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                            Extracts candidate numerical spans and table rows from 10-K filings.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-white">5.34s</span>
                        </div>
                    </div>

                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border border-[var(--border-color)]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-white uppercase font-mono">Stage 2: Program</span>
                            <span class="badge badge-sas">7B F16</span>
                        </div>
                        <div class="font-semibold text-sm text-white mt-2">Drafter Role</div>
                        <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                            Translates extracted spans into executable arithmetic programs.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-white">11.96s</span>
                        </div>
                    </div>

                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border border-[var(--border-color)]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-white uppercase font-mono">Stage 3: Audit</span>
                            <span class="badge badge-sas">3B F16</span>
                        </div>
                        <div class="font-semibold text-sm text-white mt-2">Verifier Role</div>
                        <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                            Audits units, span alignment, and logic sanity. Triggers repair or withhold.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-white">1.12s</span>
                        </div>
                    </div>

                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border border-[var(--border-color)]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-white uppercase font-mono">Decision Gate</span>
                            <span class="badge badge-withheld">Policy</span>
                        </div>
                        <div class="font-semibold text-sm text-white mt-2">Delivery / Withhold</div>
                        <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                            Enforces compliance threshold. If confidence fails, answer is withheld.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[var(--border-color)] text-xs text-slate-400 font-mono flex justify-between">
                            <span>Withheld Rate:</span>
                            <span class="text-amber-400 font-semibold">73.8%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts: Stage Tokens & Inference Time -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-semibold text-white">Stage Token Generation (MAS Primary)</h3>
                        <p class="text-xs text-slate-400">Tokens generated per role</p>
                    </div>
                    <div class="h-60 mt-4">
                        <canvas id="pipeline-token-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-semibold text-white">Cumulative Inference Latency (Seconds)</h3>
                        <p class="text-xs text-slate-400">Total CPU seconds by pipeline stage</p>
                    </div>
                    <div class="h-60 mt-4">
                        <canvas id="pipeline-time-chart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Full Stage Metrics Table -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Stage-by-Stage Cost Telemetry (23 Recorded Stages)</h3>
                    <p class="text-xs text-slate-400">Calls, prompt tokens, generated tokens, and context budget skips</p>
                </div>
                <div class="table-container max-h-[420px] overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Job Name</th>
                                <th>Role</th>
                                <th>Stage</th>
                                <th>Calls</th>
                                <th>Prompt Tokens</th>
                                <th>Generated Tokens</th>
                                <th>Inference Seconds</th>
                                <th>Tokens / Call</th>
                                <th>Skips</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stageMetrics.map(s => `
                                <tr>
                                    <td class="font-mono text-xs text-white">${s.job}</td>
                                    <td><span class="badge badge-sas">${s.role}</span></td>
                                    <td class="text-xs text-slate-400 font-mono">${s.stage}</td>
                                    <td class="font-mono text-xs">${s.calls}</td>
                                    <td class="font-mono text-xs text-slate-400">${s.prompt_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-white font-medium">${s.generated_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-slate-300">${s.inference_seconds.toFixed(1)}s</td>
                                    <td class="font-mono text-xs text-slate-400">${(s.generated_tokens / Math.max(s.calls, 1)).toFixed(1)}</td>
                                    <td class="font-mono text-xs ${s.context_or_budget_skips > 0 ? 'text-rose-400 font-semibold' : 'text-slate-500'}">${s.context_or_budget_skips}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.renderCharts();
    },

    renderCharts() {
        const ctx1 = document.getElementById('pipeline-token-chart');
        if (ctx1) {
            new Chart(ctx1, {
                type: 'bar',
                data: {
                    labels: ['Extractor', 'Drafter', 'Verifier'],
                    datasets: [{
                        label: 'Generated Tokens',
                        data: [4121, 2831, 1440],
                        backgroundColor: '#388bfd',
                        borderRadius: 4
                    }]
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

        const ctx2 = document.getElementById('pipeline-time-chart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['Extractor', 'Drafter', 'Verifier'],
                    datasets: [{
                        label: 'Inference Seconds',
                        data: [854.7, 1914.7, 179.6],
                        backgroundColor: '#6e7681',
                        borderRadius: 4
                    }]
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
    }
});
