/**
 * MAS vs SAS Comparison Page - Minimal, Plain, Publication-Grade
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
            <!-- Research Summary Banner (Plain, Structured) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Primary Headline Contrast</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            SAS-Quant Outperforms MAS-FP16 by +45.6% on 16 GB Analyst RAM
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            Under equalized RAM (12.8 GB cap) and equalized thinking tokens, the single quantized 14B model achieved 50.6% accuracy versus 5.0% for the 3-agent team. MAS suffered from severe policy withholding (73.8%), failing verifier thresholds.
                        </p>
                    </div>
                    <div class="shrink-0 text-right">
                        <div class="text-[11px] text-slate-400 font-mono">Clustered Signflip Test</div>
                        <div class="text-base font-bold font-mono text-white">p = 1.53e-5</div>
                    </div>
                </div>
            </div>

            <!-- Plain Scorecard Grid (4 Core Indicators) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Reported Accuracy</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        <span class="text-slate-300">5.0%</span> vs <span class="text-white">50.6%</span>
                    </div>
                    <div class="text-xs text-slate-400 font-mono mt-1">MAS (8/160) vs SAS (81/160)</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Delivery Rate</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        <span class="text-slate-300">26.3%</span> vs <span class="text-white">86.9%</span>
                    </div>
                    <div class="text-xs text-slate-400 font-mono mt-1">MAS withholds 73.8%</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Raw Execution Match</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        <span class="text-slate-300">30.0%</span> vs <span class="text-white">50.6%</span>
                    </div>
                    <div class="text-xs text-slate-400 font-mono mt-1">Dual-metric base accuracy</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-medium">Inference Seconds / Correct</div>
                    <div class="text-xl font-bold font-mono text-white mt-1">
                        <span class="text-slate-300">367.6s</span> vs <span class="text-white">54.1s</span>
                    </div>
                    <div class="text-xs text-slate-400 font-mono mt-1">SAS is 6.8x more efficient</div>
                </div>
            </div>

            <!-- Forest Plot (Academic Journal Style) -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-2">
                    <div>
                        <h3 class="text-sm font-semibold text-white">Forest Plot: Paired Contrasts & Confidence Intervals</h3>
                        <p class="text-xs text-slate-400">Effect size (Δ = MAS - SAS) with 95% Wald and Clustered CIs across key comparison endpoints</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Filter:</span>
                        <select id="forest-filter" class="select-filter text-xs">
                            <option value="primary" selected>Primary Comparison Only</option>
                            <option value="all">All Comparisons (42)</option>
                            <option value="direct_control">Direct Control Ablation</option>
                            <option value="repair_ablation">Repair Ablation</option>
                        </select>
                    </div>
                </div>
                <div class="p-2">
                    <div id="forest-plot-container" class="w-full h-72"></div>
                </div>
            </div>

            <!-- Table of Metric Disagreements (48 Cases) -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-semibold text-white">Metric Disagreements (48 Instances)</h3>
                        <p class="text-xs text-slate-400">Cases where reported-answer format and direct mathematical execution disagreed</p>
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
                                    <td class="font-mono text-xs text-white">${m.case_id}</td>
                                    <td>${m.reported_correct ? '<span class="badge badge-correct">True</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                    <td>${m.raw_correct ? '<span class="badge badge-correct">True</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                    <td class="font-mono text-xs text-slate-300">${m.predicted ?? 'null'}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.declared_unit ?? '—'}</td>
                                    <td class="font-mono text-xs text-white font-medium">${m.gold_answer ?? 'null'}</td>
                                    <td class="font-mono text-xs text-slate-300">${m.gold_exe_ans ?? 'null'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <div class="text-[11px] text-slate-400 mt-2 text-right">
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
                color: '#6e7681',
                thickness: 1.5,
                width: 4
            },
            marker: {
                color: deltas.map(d => d < 0 ? '#f85149' : '#3fb950'),
                size: 8
            },
            hoverinfo: 'text',
            text: dataRows.map(d => `Contrast: ${d.comparison}<br>Endpoint: ${d.endpoint}<br>Δ: ${(d.delta*100).toFixed(2)}%<br>95% CI: [${(d.ci_low*100).toFixed(2)}%, ${(d.ci_high*100).toFixed(2)}%]<br>p-value: ${d.cluster_signflip_p ? d.cluster_signflip_p.toExponential(2) : 'N/A'}`)
        };

        const layout = {
            margin: { l: 220, r: 30, t: 10, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
                title: 'Effect Size (Δ = MAS - SAS in %)',
                titlefont: { color: '#8b949e', size: 11, family: 'Inter' },
                tickfont: { color: '#8b949e', size: 10, family: 'JetBrains Mono' },
                gridcolor: '#242c38',
                zerolinecolor: '#484f58',
                zerolinewidth: 1.5
            },
            yaxis: {
                tickfont: { color: '#8b949e', size: 10, family: 'Inter' },
                autorange: 'reversed'
            }
        };

        Plotly.newPlot(container, [trace], layout, { responsive: true, displayModeBar: false });
    }
});
