/**
 * MAS vs SAS Comparison Page - Visual Research Dashboard
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
            <!-- Key Metric Visual Comparison Cards (Top) -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat-card border-l-4 border-l-[#DC2626]">
                    <div class="stat-card-label">
                        <span>Reported Accuracy</span>
                        <span class="badge badge-wrong">Δ -45.6%</span>
                    </div>
                    <div class="stat-card-value text-[#172033] flex items-baseline gap-2">
                        <span class="text-[#2563EB] text-xl">5.0%</span>
                        <span class="text-xs text-[#94A3B8]">vs</span>
                        <span class="text-[#15803D] text-2xl">50.6%</span>
                    </div>
                    <div class="stat-card-meta">MAS (8/160) vs SAS (81/160)</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#15803D]" style="width: 50.6%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#D97706]">
                    <div class="stat-card-label">
                        <span>Delivery Rate</span>
                        <span class="badge badge-withheld">73.8% Withheld</span>
                    </div>
                    <div class="stat-card-value text-[#172033] flex items-baseline gap-2">
                        <span class="text-[#D97706] text-xl">26.3%</span>
                        <span class="text-xs text-[#94A3B8]">vs</span>
                        <span class="text-[#172033] text-2xl">86.9%</span>
                    </div>
                    <div class="stat-card-meta">MAS Withholds 118 / 160 cases</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#D97706]" style="width: 73.8%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">
                        <span>Raw Execution Match</span>
                        <span class="badge badge-mas">Dual-Metric</span>
                    </div>
                    <div class="stat-card-value text-[#172033] flex items-baseline gap-2">
                        <span class="text-[#2563EB] text-xl">30.0%</span>
                        <span class="text-xs text-[#94A3B8]">vs</span>
                        <span class="text-[#172033] text-2xl">50.6%</span>
                    </div>
                    <div class="stat-card-meta">Base execution before verifier filter</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 30.0%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#15803D]">
                    <div class="stat-card-label">
                        <span>Inference Latency / Correct</span>
                        <span class="badge badge-correct">6.8x Faster</span>
                    </div>
                    <div class="stat-card-value text-[#172033] flex items-baseline gap-2">
                        <span class="text-[#64748B] text-xl">367.6s</span>
                        <span class="text-xs text-[#94A3B8]">vs</span>
                        <span class="text-[#15803D] text-2xl">54.1s</span>
                    </div>
                    <div class="stat-card-meta">SAS monolithic CPU efficiency</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#15803D]" style="width: 85%;"></div>
                    </div>
                </div>
            </div>

            <!-- Scientific Forest Plot (Plotly) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Forest Plot: Paired Contrasts & Confidence Intervals</h3>
                        <p class="text-xs text-[#64748B]">Effect size (Δ = MAS - SAS) with 95% Wald & Clustered CIs across key comparison endpoints</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-[#64748B]">Filter:</span>
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

            <!-- Profile Ablation Visual Comparison Chart & Metric Disagreements Table -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Visual Ablation Chart -->
                <div class="card lg:col-span-5 flex flex-col justify-between">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Profile Ablation Accuracy</h3>
                            <p class="text-xs text-[#64748B]">Impact of Verifier & Repair components</p>
                        </div>
                        <span class="badge badge-mas">Ablation</span>
                    </div>
                    <div class="pt-4 flex-1">
                        <div class="w-full h-64">
                            <canvas id="ablation-comparison-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Table of Metric Disagreements -->
                <div class="card lg:col-span-7">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Metric Disagreements (48 Cases)</h3>
                            <p class="text-xs text-[#64748B]">Reported answer format vs direct python execution disagreement</p>
                        </div>
                        <span class="badge badge-sas">Sample (15 shown)</span>
                    </div>
                    <div class="table-container mt-4 max-h-64 overflow-y-auto">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Case ID</th>
                                    <th>Reported</th>
                                    <th>Raw Exec</th>
                                    <th>Predicted Output</th>
                                    <th>Gold Answer</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${metricDisagreements.slice(0, 15).map(m => `
                                    <tr>
                                        <td class="font-mono text-xs text-[#172033] font-medium">${m.case_id}</td>
                                        <td>${m.reported_correct ? '<span class="badge badge-correct">Correct</span>' : '<span class="badge badge-wrong">False</span>'}</td>
                                        <td>${m.raw_correct ? '<span class="badge badge-correct">Match</span>' : '<span class="badge badge-wrong">Mismatch</span>'}</td>
                                        <td class="font-mono text-xs text-[#172033] truncate max-w-[120px]">${m.predicted ?? 'null'}</td>
                                        <td class="font-mono text-xs text-[#2563EB] font-semibold">${m.gold_answer ?? 'null'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        this.renderForestPlot(pairedEffects.filter(p => p.comparison === 'primary'));
        this.renderAblationChart();

        document.getElementById('forest-filter')?.addEventListener('change', (e) => {
            const val = e.target.value;
            const filtered = val === 'all' ? pairedEffects : pairedEffects.filter(p => p.comparison === val);
            this.renderForestPlot(filtered);
        });
    },

    renderAblationChart() {
        const ctx = document.getElementById('ablation-comparison-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Primary (Full Team)', 'Direct Control (No Verifier)', 'Repair Ablation (No Repair)'],
                datasets: [
                    {
                        label: 'MAS-FP16 Accuracy %',
                        data: [5.0, 0.0, 5.0],
                        backgroundColor: '#2563EB',
                        borderRadius: 4
                    },
                    {
                        label: 'SAS-Quant Accuracy %',
                        data: [50.6, 31.9, 50.6],
                        backgroundColor: '#64748B',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#64748B', font: { size: 11, family: 'Inter' }, boxWidth: 12 }
                    },
                    tooltip: {
                        backgroundColor: '#172033',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F8FAFC',
                        borderColor: '#E2E8F0',
                        borderWidth: 1,
                        padding: 10
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748B', font: { size: 10, family: 'Inter' } }
                    },
                    y: {
                        max: 60,
                        grid: { color: '#E9EEF5' },
                        ticks: { color: '#64748B', callback: v => v + '%', font: { size: 10, family: 'JetBrains Mono' } }
                    }
                }
            }
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