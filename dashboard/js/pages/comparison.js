/**
 * MAS vs SAS Head-to-Head Comparison Page
 */

window.App.registerPage('comparison', {
    async render(container, app) {
        const pairedEffects = await app.fetchJson('data/tier16_v2/paired_effects.json') || [];
        const metricDisagreements = await app.fetchJson('data/tier16_v2/metric_disagreements.json') || [];
        const aggr = app.state.data.aggregates || await app.fetchJson('data/derived_aggregates.json');
        const jobs = aggr ? aggr.jobs_16gb : {};

        const mas = jobs['tier16-mas-primary'] || {};
        const sas = jobs['tier16-sas-primary'] || {};

        container.innerHTML = `
            <!-- Top Summary Card -->
            <div class="card bg-gradient-to-r from-slate-900 to-indigo-950/30 border-indigo-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-sas">Headline Result</span>
                            <span class="text-xs text-slate-400 font-mono">16 GB Pretrained FinQA • n = 160</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            SAS-Quant Outperforms MAS-FP16 by +45.6% Accuracy on 16 GB Analyst RAM
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            Under the strict RUPP RAM parity protocol (12.8 GB cap) and equalized thinking tokens, single quantized 14B model achieved 50.6% numerical accuracy versus 5.0% for the 3-agent team. MAS suffered from extreme policy withholding (73.8%), failing to pass verifier threshold.
                        </p>
                    </div>
                    <div class="flex items-center gap-3">
                        <div class="text-right">
                            <div class="text-[10px] text-slate-400 font-mono">Clustered Signflip p-value</div>
                            <div class="text-base font-bold font-mono text-emerald-400">p = 1.53e-5</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Side-by-side Scorecard Grid -->
            <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Reported Acc (MAS)</div>
                    <div class="text-xl font-bold font-mono text-emerald-400 mt-1">${mas.reported_acc ?? '5.0'}%</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">8 / 160 correct</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Reported Acc (SAS)</div>
                    <div class="text-xl font-bold font-mono text-purple-400 mt-1">${sas.reported_acc ?? '50.6'}%</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">81 / 160 correct</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Delivery Rate</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        <span class="text-emerald-400 font-mono">${mas.delivery_rate ?? '26.3'}%</span> vs 
                        <span class="text-purple-400 font-mono">${sas.delivery_rate ?? '86.9'}%</span>
                    </div>
                    <div class="text-[10px] text-slate-500 mt-0.5">MAS withholds 73.8%</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Raw Execution Match</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        <span class="text-emerald-400 font-mono">${mas.raw_acc ?? '30.0'}%</span> vs 
                        <span class="text-purple-400 font-mono">${sas.raw_acc ?? '50.6'}%</span>
                    </div>
                    <div class="text-[10px] text-slate-500 mt-0.5">Dual-metric baseline</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Avg Inference Sec</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        ${mas.avg_seconds_per_case ?? '18.4'}s vs ${sas.avg_seconds_per_case ?? '27.4'}s
                    </div>
                    <div class="text-[10px] text-slate-500 mt-0.5">MAS 33% faster</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Sec per Correct Ans</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        ${mas.seconds_per_correct ?? '367.6'}s vs ${sas.seconds_per_correct ?? '54.1'}s
                    </div>
                    <div class="text-[10px] text-slate-500 mt-0.5">SAS 6.8x more efficient</div>
                </div>
            </div>

            <!-- Visualization: Forest Plot of Paired Contrasts -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-2">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="git-commit" class="w-4 h-4 text-emerald-400"></i>
                            Interactive Forest Plot — Paired Contrasts & Confidence Intervals
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Effect sizes (Δ = MAS - SAS) with 95% Wald and Clustered CIs across 42 endpoints</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Filter endpoint:</span>
                        <select id="forest-filter" class="select-filter text-xs">
                            <option value="all">All Comparisons (42)</option>
                            <option value="primary" selected>Primary Comparison Only</option>
                            <option value="direct_control">Direct Control Ablation</option>
                            <option value="repair_ablation">Repair Ablation</option>
                        </select>
                    </div>
                </div>
                <div class="p-2">
                    <div id="forest-plot-container" class="w-full h-80"></div>
                </div>
            </div>

            <!-- Profile Ablation Matrix -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                <div class="card">
                    <div class="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                        <span class="text-xs font-bold text-white uppercase font-mono">Primary Profile</span>
                        <span class="badge badge-mas">Standard</span>
                    </div>
                    <div class="mt-3 space-y-2 text-xs">
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Reported Acc:</span>
                            <span class="font-bold font-mono text-emerald-400">5.0% (8/160)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Reported Acc:</span>
                            <span class="font-bold font-mono text-purple-400">50.6% (81/160)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>Delta (MAS - SAS):</span>
                            <span class="font-bold font-mono text-rose-400">-45.6%</span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                            Full Drafter + Verifier + conditional repair loop.
                        </p>
                    </div>
                </div>

                <div class="card">
                    <div class="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                        <span class="text-xs font-bold text-white uppercase font-mono">Direct Control</span>
                        <span class="badge badge-sas">No Verifier</span>
                    </div>
                    <div class="mt-3 space-y-2 text-xs">
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Reported Acc:</span>
                            <span class="font-bold font-mono text-emerald-400">0.0% (0/160)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Reported Acc:</span>
                            <span class="font-bold font-mono text-purple-400">31.9% (51/160)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>Delta (MAS - SAS):</span>
                            <span class="font-bold font-mono text-rose-400">-31.9%</span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                            Negative control: without verification, MAS produces 0 delivered correct answers.
                        </p>
                    </div>
                </div>

                <div class="card">
                    <div class="flex items-center justify-between pb-2 border-b border-[var(--border-color)]">
                        <span class="text-xs font-bold text-white uppercase font-mono">Repair Ablation</span>
                        <span class="badge">No Repair</span>
                    </div>
                    <div class="mt-3 space-y-2 text-xs">
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Reported Acc:</span>
                            <span class="font-bold font-mono text-emerald-400">5.0% (8/160)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Reported Acc:</span>
                            <span class="font-bold font-mono text-purple-400">50.6% (81/160)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>Delta (MAS - SAS):</span>
                            <span class="font-bold font-mono text-rose-400">-45.6%</span>
                        </div>
                        <p class="text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                            Verifier flags discrepancies, but the subsequent drafter repair step is bypassed.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Table of 48 Metric Disagreements -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="alert-triangle" class="w-4 h-4 text-amber-400"></i>
                            Metric Disagreements Explorer (48 Cases)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Cases where reported-answer correctness and raw-execution correctness disagreed</p>
                    </div>
                    <span class="badge badge-withheld">48 Instances</span>
                </div>
                <div class="table-container mt-4 max-h-80 overflow-y-auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Case ID</th>
                                <th>Reported Correct</th>
                                <th>Raw Correct</th>
                                <th>Model Predicted</th>
                                <th>Declared Unit</th>
                                <th>Gold Answer</th>
                                <th>Gold Execution Ans</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${metricDisagreements.slice(0, 15).map(m => `
                                <tr>
                                    <td class="font-mono text-xs text-white">${m.case_id}</td>
                                    <td>${m.reported_correct ? '<span class="badge badge-correct">True</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                    <td>${m.raw_correct ? '<span class="badge badge-correct">True</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                    <td class="font-mono text-xs text-amber-300">${m.predicted ?? 'null'}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.declared_unit ?? 'null'}</td>
                                    <td class="font-mono text-xs text-emerald-400">${m.gold_answer ?? 'null'}</td>
                                    <td class="font-mono text-xs text-cyan-400">${m.gold_exe_ans ?? 'null'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="text-[11px] text-slate-500 mt-2 text-right">
                    Showing first 15 of 48 metric disagreements. Inspect full table in Case Explorer.
                </div>
            </div>
        `;

        // Render the Plotly Forest Plot
        this.renderForestPlot(pairedEffects);

        // Bind filter change
        const filterSelect = document.getElementById('forest-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                const val = e.target.value;
                const filtered = val === 'all' ? pairedEffects : pairedEffects.filter(p => p.comparison === val);
                this.renderForestPlot(filtered);
            });
        }
    },

    renderForestPlot(pairedEffects) {
        const container = document.getElementById('forest-plot-container');
        if (!container || !window.Plotly) return;

        const dataRows = pairedEffects.slice(0, 12); // top 12 contrasts
        const labels = dataRows.map(d => `${d.comparison} • ${d.endpoint.replace('case_success/', '').replace('raw_execution_match/', 'raw_')}`);
        const deltas = dataRows.map(d => d.delta * 100);
        const ciLows = dataRows.map(d => d.ci_low * 100);
        const ciHighs = dataRows.map(d => d.ci_high * 100);

        const errorMinus = deltas.map((d, i) => d - ciLows[i]);
        const errorPlus = deltas.map((d, i) => ciHighs[i] - d);

        const trace = {
            type: 'scatter',
            mode: 'markers',
            x: deltas,
            y: labels,
            error_x: {
                type: 'data',
                symmetric: false,
                array: errorPlus,
                arrayminus: errorMinus,
                color: '#38bdf8',
                thickness: 2,
                width: 6
            },
            marker: {
                color: deltas.map(d => d < 0 ? '#f43f5e' : '#10b981'),
                size: 9
            },
            hoverinfo: 'text',
            text: dataRows.map(d => `Contrast: ${d.comparison}<br>Endpoint: ${d.endpoint}<br>Δ: ${(d.delta*100).toFixed(2)}%<br>95% CI: [${(d.ci_low*100).toFixed(2)}%, ${(d.ci_high*100).toFixed(2)}%]<br>p-value: ${d.cluster_signflip_p ? d.cluster_signflip_p.toExponential(2) : 'N/A'}`)
        };

        const layout = {
            margin: { l: 200, r: 40, t: 20, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
                title: 'Effect Size (Δ = MAS - SAS in %)',
                titlefont: { color: '#94a3b8', size: 11 },
                tickfont: { color: '#cbd5e1', size: 10 },
                gridcolor: '#1e293b',
                zerolinecolor: '#475569',
                zerolinewidth: 2
            },
            yaxis: {
                tickfont: { color: '#cbd5e1', size: 10 },
                autorange: 'reversed'
            }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
    }
});

