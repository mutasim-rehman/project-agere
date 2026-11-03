/**
 * Pipeline Stages & Token Cost Analysis Page - Academic Light Theme
 */

window.App.registerPage('pipeline', {
    async render(container, app) {
        const stageMetrics = await app.fetchJson('data/tier16_v2/stage_metrics.json') || [];

        container.innerHTML = `
            <!-- Top Summary Card (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="space-y-1 max-w-4xl">
                    <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                        MAS Pipeline Architecture & Cost Decomposition
                    </div>
                    <h2 class="text-base font-bold text-[#172033]">
                        Multi-Agent Stage Decomposition & Token Consumption
                    </h2>
                    <p class="text-xs text-[#64748B] leading-relaxed">
                        The MAS pipeline splits execution into three specialized roles: Extractor (evidence span selection), Drafter (arithmetic program generation), and Verifier (grounding and sanity check). Latency and token consumption are measured directly via CPU inference timers.
                    </p>
                </div>
            </div>

            <!-- Pipeline Execution Workflow Diagram (4 Connected Stages) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Multi-Agent Execution Pipeline Flow (MAS-FP16)</h3>
                        <p class="text-xs text-[#64748B]">Sequential CPU execution pipeline operating under the 12.8 GB RUPP process limit</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                    <!-- Stage 1 -->
                    <div class="card bg-[#F8FAFC] p-4 border border-[#E2E8F0] border-t-4 border-t-[#2563EB]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-[#172033] uppercase font-mono">Stage 1: Evidence</span>
                            <span class="badge badge-mas">1.5B FP16</span>
                        </div>
                        <div class="font-bold text-sm text-[#2563EB] mt-2">Extractor Role</div>
                        <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                            Extracts candidate numerical spans and table rows from raw 10-K filings.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-[#172033] font-bold">5.34s</span>
                        </div>
                    </div>

                    <!-- Stage 2 -->
                    <div class="card bg-[#F8FAFC] p-4 border border-[#E2E8F0] border-t-4 border-t-[#3B82F6]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-[#172033] uppercase font-mono">Stage 2: Program</span>
                            <span class="badge badge-mas">7B FP16</span>
                        </div>
                        <div class="font-bold text-sm text-[#3B82F6] mt-2">Drafter Role</div>
                        <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                            Translates extracted evidence spans into executable arithmetic programs.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-[#172033] font-bold">11.96s</span>
                        </div>
                    </div>

                    <!-- Stage 3 -->
                    <div class="card bg-[#F8FAFC] p-4 border border-[#E2E8F0] border-t-4 border-t-[#7C3AED]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-[#172033] uppercase font-mono">Stage 3: Audit</span>
                            <span class="badge" style="background:#F5F3FF; color:#7C3AED; border:1px solid #DDD6FE;">3B FP16</span>
                        </div>
                        <div class="font-bold text-sm text-[#7C3AED] mt-2">Verifier Role</div>
                        <p class="text-xs text-[#64748B] mt-1 leading-relaxed">
                            Audits units, span alignment, and logic sanity. Triggers repair or withhold.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[#E2E8F0] text-xs text-[#64748B] font-mono flex justify-between">
                            <span>Avg Latency:</span>
                            <span class="text-[#172033] font-bold">1.12s</span>
                        </div>
                    </div>

                    <!-- Stage 4: Decision Gate (Distinct Amber Treatment) -->
                    <div class="card bg-[#FFFBEB] p-4 border border-[#FDE68A] border-t-4 border-t-[#D97706]">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-bold text-[#D97706] uppercase font-mono">Stage 4: Gate</span>
                            <span class="badge badge-withheld">Policy Audit</span>
                        </div>
                        <div class="font-bold text-sm text-[#D97706] mt-2">Delivery / Withhold</div>
                        <p class="text-xs text-[#92400E] mt-1 leading-relaxed">
                            Enforces compliance threshold. If confidence fails, answer is withheld.
                        </p>
                        <div class="mt-3 pt-2 border-t border-[#FDE68A] text-xs text-[#92400E] font-mono flex justify-between">
                            <span>Withheld Rate:</span>
                            <span class="text-[#D97706] font-bold">73.8%</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts: Stage Tokens & Latency -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Stage Token Generation (MAS Primary)</h3>
                            <p class="text-xs text-[#64748B]">Total output tokens by role</p>
                        </div>
                    </div>
                    <div class="h-60 mt-4">
                        <canvas id="pipeline-token-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Cumulative Inference Latency (Seconds)</h3>
                            <p class="text-xs text-[#64748B]">Total CPU seconds across 160 instances</p>
                        </div>
                    </div>
                    <div class="h-60 mt-4">
                        <canvas id="pipeline-time-chart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Full Stage Metrics Table -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Stage-by-Stage Cost Telemetry (23 Recorded Stages)</h3>
                        <p class="text-xs text-[#64748B]">Calls, prompt tokens, generated tokens, and context budget skips</p>
                    </div>
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
                                    <td class="font-mono text-xs text-[#172033] font-medium">${s.job}</td>
                                    <td><span class="badge ${s.role === 'drafter' ? 'badge-mas' : (s.role === 'verifier' ? 'badge-withheld' : 'badge-sas')}">${s.role}</span></td>
                                    <td class="text-xs text-[#64748B] font-mono">${s.stage}</td>
                                    <td class="font-mono text-xs text-[#172033]">${s.calls}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${s.prompt_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-[#172033] font-bold">${s.generated_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${s.inference_seconds.toFixed(1)}s</td>
                                    <td class="font-mono text-xs text-[#64748B]">${(s.generated_tokens / Math.max(s.calls, 1)).toFixed(1)}</td>
                                    <td class="font-mono text-xs ${s.context_or_budget_skips > 0 ? 'text-[#DC2626] font-bold' : 'text-[#94A3B8]'}">${s.context_or_budget_skips}</td>
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
                    labels: ['Extractor (1.5B)', 'Drafter (7B)', 'Verifier (3B)'],
                    datasets: [{
                        label: 'Generated Tokens',
                        data: [4121, 2831, 1440],
                        backgroundColor: '#2563EB',
                        borderRadius: 4
                    }]
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

        const ctx2 = document.getElementById('pipeline-time-chart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: ['Extractor', 'Drafter', 'Verifier'],
                    datasets: [{
                        label: 'Inference Seconds',
                        data: [854.7, 1914.7, 179.6],
                        backgroundColor: '#64748B',
                        borderRadius: 4
                    }]
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
    }
});
