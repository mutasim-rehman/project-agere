/**
 * Pipeline Stages & Token Cost Analysis Page
 */

window.App.registerPage('pipeline', {
    async render(container, app) {
        const stageMetrics = await app.fetchJson('data/tier16_v2/stage_metrics.json') || [];

        container.innerHTML = `
            <!-- Top Summary -->
            <div class="card bg-gradient-to-r from-slate-900 to-cyan-950/20 border-cyan-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-mas">Pipeline Diagnostics</span>
                            <span class="text-xs text-slate-400 font-mono">16 GB Evaluation Stages</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Multi-Agent Stage Decomposition & Token Consumption
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            The MAS pipeline splits execution into three specialized roles: Extractor (evidence span selection), Drafter (arithmetic program generation), and Verifier (grounding and sanity check). Latency and token consumption are measured directly via CPU inference timers.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Pipeline Architecture Flow Diagram -->
            <div class="card p-6">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                        <i data-lucide="git-merge" class="w-4 h-4 text-cyan-400"></i>
                        Multi-Agent Execution Pipeline Flow (MAS-FP16)
                    </h3>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border-l-4 border-emerald-500">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-white uppercase font-mono">Stage 1: Evidence</span>
                            <span class="badge badge-mas">1.5B F16</span>
                        </div>
                        <div class="font-bold text-sm text-emerald-400 mt-2">Extractor Role</div>
                        <p class="text-[11px] text-slate-400 mt-1 leading-relaxed">
                            Filters financial tables and narrative paragraphs. Identifies relevant numerical spans and assigns unique span IDs.
                        </p>
                        <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400 font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-white">5.34s</span>
                        </div>
                    </div>

                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border-l-4 border-cyan-500">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-white uppercase font-mono">Stage 2: Program</span>
                            <span class="badge">7B F16</span>
                        </div>
                        <div class="font-bold text-sm text-cyan-400 mt-2">Drafter Role</div>
                        <p class="text-[11px] text-slate-400 mt-1 leading-relaxed">
                            Takes extracted evidence spans and constructs an executable calculation program (e.g. `add(290, 27.5)`).
                        </p>
                        <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400 font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-white">11.96s</span>
                        </div>
                    </div>

                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border-l-4 border-purple-500">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-white uppercase font-mono">Stage 3: Audit</span>
                            <span class="badge badge-sas">3B F16</span>
                        </div>
                        <div class="font-bold text-sm text-purple-400 mt-2">Verifier Role</div>
                        <p class="text-[11px] text-slate-400 mt-1 leading-relaxed">
                            Validates units, span alignment, and sanity. If a contradiction is detected, triggers a single repair loop or withholds.
                        </p>
                        <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400 font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-white">1.12s</span>
                        </div>
                    </div>

                    <div class="card bg-[var(--bg-surface-elevated)] p-4 border-l-4 border-amber-500">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-white uppercase font-mono">Decision Gate</span>
                            <span class="badge badge-withheld">Policy</span>
                        </div>
                        <div class="font-bold text-sm text-amber-400 mt-2">Delivery / Withhold</div>
                        <p class="text-[11px] text-slate-400 mt-1 leading-relaxed">
                            Regulated delivery condition. If confidence or validation fails, answers are explicitly withheld rather than hallucinated.
                        </p>
                        <div class="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-400 font-mono flex justify-between">
                            <span>Withheld Rate:</span>
                            <span class="text-amber-400 font-bold">73.8%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts: Stage Tokens & Inference Time -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="pie-chart" class="w-4 h-4 text-emerald-400"></i>
                            Stage Token Generation Breakdown (MAS Primary)
                        </h3>
                    </div>
                    <div class="h-64 mt-4">
                        <canvas id="pipeline-token-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="pb-3 border-b border-[var(--border-color)]">
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="clock" class="w-4 h-4 text-purple-400"></i>
                            Cumulative Stage Inference Latency (Seconds)
                        </h3>
                    </div>
                    <div class="h-64 mt-4">
                        <canvas id="pipeline-time-chart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Full Stage Metrics Table -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="table" class="w-4 h-4 text-cyan-400"></i>
                            Stage-by-Stage Cost Telemetry (23 Recorded Stages)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Calls, prompt tokens, generated tokens, and context budget skips</p>
                    </div>
                </div>
                <div class="table-container max-h-[450px] overflow-y-auto mt-4">
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
                                    <td><span class="badge ${s.role === 'drafter' ? 'badge-sas' : (s.role === 'extractor' ? 'badge-mas' : 'badge-withheld')}">${s.role}</span></td>
                                    <td class="text-xs text-slate-300 font-mono">${s.stage}</td>
                                    <td class="font-mono text-xs">${s.calls}</td>
                                    <td class="font-mono text-xs text-slate-300">${s.prompt_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs font-bold text-emerald-400">${s.generated_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-slate-300">${s.inference_seconds.toFixed(1)}s</td>
                                    <td class="font-mono text-xs">${(s.generated_tokens / Math.max(s.calls, 1)).toFixed(1)}</td>
                                    <td class="font-mono text-xs ${s.context_or_budget_skips > 0 ? 'text-rose-400 font-bold' : 'text-slate-500'}">${s.context_or_budget_skips}</td>
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
                type: 'doughnut',
                data: {
                    labels: ['Extractor (select_evidence)', 'Drafter (program)', 'Verifier (verify_program)'],
                    datasets: [{
                        data: [4121, 2831, 1440],
                        backgroundColor: ['#10b981', '#38bdf8', '#8b5cf6'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 11 } } }
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
                        backgroundColor: ['#10b981', '#38bdf8', '#8b5cf6']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: { grid: { color: '#1e293b' }, ticks: { color: '#cbd5e1' } },
                        y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }
    }
});

