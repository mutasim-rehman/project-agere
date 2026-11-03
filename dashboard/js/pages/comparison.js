/**
 * MAS vs SAS Comparison Page - Academic Light Theme
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
            <!-- Research Contrast Header -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div class="space-y-1 max-w-4xl">
                        <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                            Comparative Evaluation • 16 GB Pretrained FinQA
                        </div>
                        <h2 class="text-base font-bold text-[#172033]">
                            SAS-Quant Outperforms MAS-FP16 by +45.6% on Constrained Analyst Workstations
                        </h2>
                        <p class="text-xs text-[#64748B] leading-relaxed">
                            Under the strict RUPP RAM parity protocol (12.8 GB cap) and equalized thinking tokens, single quantized 14B model achieved 50.6% numerical accuracy versus 5.0% for the 3-agent team. MAS suffered from severe policy withholding (73.8%), failing verifier threshold criteria.
                        </p>
                    </div>
                    <div class="shrink-0 text-right font-mono">
                        <div class="text-[11px] text-[#64748B]">Signflip Test p-value</div>
                        <div class="text-base font-bold text-[#15803D]">p = 1.53e-5 (Sig)</div>
                    </div>
                </div>
            </div>

            <!-- Side-by-side Scientific Scorecard Grid -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Reported Accuracy</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">
                        <span class="text-[#2563EB]">5.0%</span> vs <span class="text-[#172033]">50.6%</span>
                    </div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">MAS (8/160) vs SAS (81/160)</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Delivery Rate</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">
                        <span class="text-[#D97706]">26.3%</span> vs <span class="text-[#172033]">86.9%</span>
                    </div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">MAS withholds 73.8%</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Raw Execution Match</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">
                        <span class="text-[#2563EB]">30.0%</span> vs <span class="text-[#172033]">50.6%</span>
                    </div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">Dual-metric base execution</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Inference Latency / Correct</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">
                        <span class="text-[#64748B]">367.6s</span> vs <span class="text-[#172033]">54.1s</span>
                    </div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">SAS is 6.8x more efficient</div>
                </div>
            </div>

            <!-- Scientific Forest Plot -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Forest Plot: Paired Contrasts & Confidence Intervals</h3>
                        <p class="text-xs text-[#64748B]">Effect size (Δ = MAS - SAS) with 95% Wald and Clustered CIs across key comparison endpoints</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-[#64748B]">Comparison:</span>
                        <select id="forest-filter" class="select-filter text-xs">
                            <option value="primary" selected>Primary Comparison Only</option>
                            <option value="all">All Comparisons (42)</option>
                            <option value="direct_control">Direct Control Ablation</option>
                            <option value="repair_ablation">Repair Ablation</option>
                        </select>
                    </div>
                </div>
                <div class="pt-3">
                    <div id="forest-plot-container" class="w-full h-80"></div>
                </div>
            </div>

            <!-- Profile Ablation Matrix -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="card p-4">
                    <div class="flex items-center justify-between pb-2 border-b border-[#E2E8F0]">
                        <span class="text-xs font-bold text-[#172033] uppercase font-mono">Primary Profile</span>
                        <span class="badge badge-mas">Standard</span>
                    </div>
                    <div class="mt-3 space-y-2 text-xs">
                        <div class="flex justify-between text-[#64748B]">
                            <span>MAS Accuracy:</span>
                            <span class="font-bold font-mono text-[#172033]">5.0% (8/160)</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>SAS Accuracy:</span>
                            <span class="font-bold font-mono text-[#172033]">50.6% (81/160)</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>Delta (MAS - SAS):</span>
                            <span class="font-bold font-mono text-[#DC2626]">-45.6%</span>
                        </div>
                        <p class="text-[11px] text-[#94A3B8] pt-2 border-t border-[#F1F5F9]">
                            Full Drafter + Verifier + conditional repair loop.
                        </p>
                    </div>
                </div>

                <div class="card p-4">
                    <div class="flex items-center justify-between pb-2 border-b border-[#E2E8F0]">
                        <span class="text-xs font-bold text-[#172033] uppercase font-mono">Direct Control</span>
                        <span class="badge badge-sas">No Verifier</span>
                    </div>
                    <div class="mt-3 space-y-2 text-xs">
                        <div class="flex justify-between text-[#64748B]">
                            <span>MAS Accuracy:</span>
                            <span class="font-bold font-mono text-[#172033]">0.0% (0/160)</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>SAS Accuracy:</span>
                            <span class="font-bold font-mono text-[#172033]">31.9% (51/160)</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>Delta (MAS - SAS):</span>
                            <span class="font-bold font-mono text-[#DC2626]">-31.9%</span>
                        </div>
                        <p class="text-[11px] text-[#94A3B8] pt-2 border-t border-[#F1F5F9]">
                            Negative control: without verification, MAS produces 0 delivered correct answers.
                        </p>
                    </div>
                </div>

                <div class="card p-4">
                    <div class="flex items-center justify-between pb-2 border-b border-[#E2E8F0]">
                        <span class="text-xs font-bold text-[#172033] uppercase font-mono">Repair Ablation</span>
                        <span class="badge badge-sas">No Repair</span>
                    </div>
                    <div class="mt-3 space-y-2 text-xs">
                        <div class="flex justify-between text-[#64748B]">
                            <span>MAS Accuracy:</span>
                            <span class="font-bold font-mono text-[#172033]">5.0% (8/160)</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>SAS Accuracy:</span>
                            <span class="font-bold font-mono text-[#172033]">50.6% (81/160)</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>Delta (MAS - SAS):</span>
                            <span class="font-bold font-mono text-[#DC2626]">-45.6%</span>
                        </div>
                        <p class="text-[11px] text-[#94A3B8] pt-2 border-t border-[#F1F5F9]">
                            Verifier flags discrepancies, but the subsequent drafter repair step is bypassed.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Table of Metric Disagreements (48 Cases) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Metric Disagreements (48 Instances)</h3>
                        <p class="text-xs text-[#64748B]">Cases where reported-answer format and direct mathematical execution disagreed</p>
                    </div>
                    <span class="badge badge-sas">48 Cases</span>
                </div>
                <div class="table-container mt-4 max-h-72 overflow-y-auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Case ID</th>
                                <th>Reported Correct</th>
                                <th>Raw Exec Correct</th>
                                <th>Model Output</th>
                                <th>Declared Unit</th>
                                <th>Gold Answer</th>
                                <th>Gold Exec Answer</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${metricDisagreements.slice(0, 15).map(m => `
                                <tr>
                                    <td class="font-mono text-xs text-[#172033] font-medium">${m.case_id}</td>
                                    <td>${m.reported_correct ? '<span class="badge badge-correct">True</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                    <td>${m.raw_correct ? '<span class="badge badge-correct">True</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                    <td class="font-mono text-xs text-[#172033]">${m.predicted ?? 'null'}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.declared_unit ?? '—'}</td>
                                    <td class="font-mono text-xs text-[#172033] font-semibold">${m.gold_answer ?? 'null'}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.gold_exe_ans ?? 'null'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="text-[11px] text-[#94A3B8] mt-2 text-right">
                    Showing first 15 of 48 records. Inspect complete cohort in the Case Explorer.
                </div>
            </div>
        `;

        this.renderForestPlot(pairedEffects.filter(p => p.comparison === 'primary'));

        document.getElementById('forest-filter')?.addEventListener('change', (e) => {
            const val = e.target.value;
            const filtered = val === 'all' ? pairedEffects : pairedEffects.filter(p => p.comparison === val);
            this.renderForestPlot(filtered);
        });
    },

    renderForestPlot(pairedEffects) {
        const container = document.getElementById('forest-plot-container');
        if (!container || !window.Plotly) return;

        const dataRows = pairedEffects.slice(0, 8);
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
                color: '#64748B',
                thickness: 1.5,
                width: 5
            },
            marker: {
                color: deltas.map(d => d < 0 ? '#DC2626' : '#15803D'),
                size: 8
            },
            hoverinfo: 'text',
            text: dataRows.map(d => `Contrast: ${d.comparison}<br>Endpoint: ${d.endpoint}<br>Δ: ${(d.delta*100).toFixed(2)}%<br>95% CI: [${(d.ci_low*100).toFixed(2)}%, ${(d.ci_high*100).toFixed(2)}%]<br>p-value: ${d.cluster_signflip_p ? d.cluster_signflip_p.toExponential(2) : 'N/A'}`)
        };

        const layout = {
            margin: { l: 240, r: 30, t: 10, b: 40 },
            paper_bgcolor: '#FFFFFF',
            plot_bgcolor: '#FFFFFF',
            xaxis: {
                title: 'Effect Size (Δ = MAS - SAS in %)',
                titlefont: { color: '#64748B', size: 11, family: 'Inter' },
                tickfont: { color: '#64748B', size: 10, family: 'JetBrains Mono' },
                gridcolor: '#E9EEF5',
                zerolinecolor: '#94A3B8',
                zerolinewidth: 1.5
            },
            yaxis: {
                tickfont: { color: '#172033', size: 10, family: 'Inter' },
                autorange: 'reversed'
            }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
    }
});
