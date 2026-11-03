/**
 * Pipeline Stages & Token Cost Analysis Page - Visual Research Dashboard
 */

window.App.registerPage('pipeline', {
    async render(container, app) {
        const stageMetrics = await app.fetchJson('data/tier16_v2/stage_metrics.json') || [];

        container.innerHTML = `
            <!-- Visual Connected Pipeline Flow (4 Connected Stages) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Multi-Agent Sequential Execution Workflow (MAS-FP16)</h3>
                        <p class="text-xs text-[#64748B]">Sequential CPU execution under the 12.8 GB host-adjusted process cap</p>
                    </div>
                    <span class="badge badge-mas">3 Specialized Agents</span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
                    <!-- Stage 1 -->
                    <div class="card bg-[#F8FAFC] p-4 border border-[#E2E8F0] border-t-4 border-t-[#2563EB] flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-[#2563EB] uppercase font-mono">Stage 1</span>
                                <span class="badge badge-mas">1.5B FP16</span>
                            </div>
                            <div class="font-bold text-sm text-[#172033] mt-2">Evidence Extractor</div>
                            <p class="text-xs text-[#64748B] mt-1">Identifies relevant tables and text spans from 10-K report.</p>
                        </div>
                        <div class="mt-4 pt-2.5 border-t border-[#E2E8F0] flex justify-between items-center text-xs font-mono">
                            <span class="text-[#64748B]">Latency: <strong class="text-[#172033]">5.34s</strong></span>
                            <span class="text-[#2563EB] font-bold">4,121 Tok</span>
                        </div>
                    </div>

                    <!-- Stage 2 -->
                    <div class="card bg-[#F8FAFC] p-4 border border-[#E2E8F0] border-t-4 border-t-[#3B82F6] flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-[#3B82F6] uppercase font-mono">Stage 2</span>
                                <span class="badge badge-mas">7B FP16</span>
                            </div>
                            <div class="font-bold text-sm text-[#172033] mt-2">Program Drafter</div>
                            <p class="text-xs text-[#64748B] mt-1">Generates executable Python program for numerical calculation.</p>
                        </div>
                        <div class="mt-4 pt-2.5 border-t border-[#E2E8F0] flex justify-between items-center text-xs font-mono">
                            <span class="text-[#64748B]">Latency: <strong class="text-[#172033]">11.96s</strong></span>
                            <span class="text-[#3B82F6] font-bold">2,831 Tok</span>
                        </div>
                    </div>

                    <!-- Stage 3 -->
                    <div class="card bg-[#F8FAFC] p-4 border border-[#E2E8F0] border-t-4 border-t-[#7C3AED] flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-[#7C3AED] uppercase font-mono">Stage 3</span>
                                <span class="badge" style="background:#F5F3FF; color:#7C3AED; border:1px solid #DDD6FE;">3B FP16</span>
                            </div>
                            <div class="font-bold text-sm text-[#172033] mt-2">Audit Verifier</div>
                            <p class="text-xs text-[#64748B] mt-1">Audits unit alignment, scale sanity, and evidence grounding.</p>
                        </div>
                        <div class="mt-4 pt-2.5 border-t border-[#E2E8F0] flex justify-between items-center text-xs font-mono">
                            <span class="text-[#64748B]">Latency: <strong class="text-[#172033]">1.12s</strong></span>
                            <span class="text-[#7C3AED] font-bold">1,440 Tok</span>
                        </div>
                    </div>

                    <!-- Stage 4: Decision Gate -->
                    <div class="card bg-[#FFFBEB] p-4 border border-[#FDE68A] border-t-4 border-t-[#D97706] flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold text-[#D97706] uppercase font-mono">Stage 4</span>
                                <span class="badge badge-withheld">Policy Gate</span>
                            </div>
                            <div class="font-bold text-sm text-[#B45309] mt-2">Decision Gate</div>
                            <p class="text-xs text-[#92400E] mt-1">Enforces policy: delivery if verified, withhold if audit fails.</p>
                        </div>
                        <div class="mt-4 pt-2.5 border-t border-[#FDE68A] flex justify-between items-center text-xs font-mono">
                            <span class="text-[#92400E]">Withheld Rate:</span>
                            <span class="text-[#D97706] font-bold">73.8% (118/160)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Charts: Stage Tokens & Latency -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Stage Generated Tokens</h3>
                            <p class="text-xs text-[#64748B]">Total output tokens generated across roles</p>
                        </div>
                        <span class="badge badge-mas">Token Generation</span>
                    </div>
                    <div class="h-64 mt-4">
                        <canvas id="pipeline-token-chart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Cumulative Inference Latency (Seconds)</h3>
                            <p class="text-xs text-[#64748B]">Total CPU runtime across 160 instances</p>
                        </div>
                        <span class="badge badge-sas">CPU Execution</span>
                    </div>
                    <div class="h-64 mt-4">
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
                <div class="table-container max-h-[380px] overflow-y-auto mt-4">
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
                        backgroundColor: ['#2563EB', '#3B82F6', '#7C3AED'],
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        tooltip: { backgroundColor: '#172033', titleColor: '#FFFFFF', bodyColor: '#F8FAFC', padding: 10 }
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
                    labels: ['Extractor (1.5B)', 'Drafter (7B)', 'Verifier (3B)'],
                    datasets: [{
                        label: 'Inference Seconds',
                        data: [854.7, 1914.7, 179.6],
                        backgroundColor: ['#64748B', '#2563EB', '#7C3AED'],
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        tooltip: { backgroundColor: '#172033', titleColor: '#FFFFFF', bodyColor: '#F8FAFC', padding: 10 }
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