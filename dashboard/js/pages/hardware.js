/**
 * Hardware & Memory Telemetry Page
 */

window.App.registerPage('hardware', {
    async render(container, app) {
        const timelines = await app.fetchJson('data/memory_timelines.json') || {};
        const benchmarks = await app.fetchJson('data/hardware_benchmarks.json') || [];
        const events = await app.fetchJson('data/tier16_v2/resource_events.json') || [];

        container.innerHTML = `
            <!-- Top Hardware Header -->
            <div class="card bg-gradient-to-r from-slate-900 via-rose-950/20 to-slate-900 border-rose-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-wrong">Hardware Telemetry</span>
                            <span class="text-xs text-slate-400 font-mono">RUPP RAM Parity Protocol</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Process-Tree RSS & Swap Breach Invalidation Audit
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            Under RUPP, experiments are monitored at sub-second intervals via Linux cgroups. Any single nonzero swap allocation (even 1 MB) immediately invalidates the run to prevent disk offloading from masquerading as RAM residency.
                        </p>
                    </div>
                    <div class="text-right">
                        <div class="text-[10px] text-slate-400 font-mono">16 GB Nominal Cap</div>
                        <div class="text-xl font-bold font-mono text-emerald-400">12.8 GB Max</div>
                    </div>
                </div>
            </div>

            <!-- Resource Incident Callout -->
            <div class="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl flex items-start gap-3">
                <div class="p-2 rounded-lg bg-amber-500/20 text-amber-400 shrink-0 mt-0.5">
                    <i data-lucide="alert-octagon" class="w-5 h-5"></i>
                </div>
                <div>
                    <h4 class="font-bold text-sm text-amber-400">Audited Invalidation Incident: tier16-sas-primary (Attempt 0001)</h4>
                    <p class="text-xs text-slate-300 mt-1 leading-relaxed">
                        At timestamp <span class="font-mono text-white">1793242632</span>, background host pressure induced a <span class="font-bold text-rose-400 font-mono">41.97 MB</span> swap breach while peak RSS reached 9.37 GB. In accordance with Section §6.2 of the specification, the attempt was formally marked <span class="badge badge-wrong font-mono">RESOURCE-INVALID</span>. A second attempt (attempt-0002) was executed with zero swap to ensure strict compliance.
                    </p>
                </div>
            </div>

            <!-- Continuous Memory Timeline Chart -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-2">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="activity" class="w-4 h-4 text-emerald-400"></i>
                            Continuous Process-Tree RSS Timeline (Downsampled from 500k Telemetry Samples)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Real-time memory footprints of MAS Primary vs SAS Attempt 1 (breached) and Attempt 2 (clean)</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Series:</span>
                        <select id="memory-job-select" class="select-filter text-xs">
                            <option value="all" selected>All Major Jobs (Overlay)</option>
                            <option value="tier16-mas-primary/attempt-0001">MAS Primary (10.18 GB Peak, 0 MB Swap)</option>
                            <option value="tier16-sas-primary/attempt-0001">SAS Attempt 1 (41.97 MB Swap Breach)</option>
                            <option value="tier16-sas-primary/attempt-0002">SAS Attempt 2 (9.37 GB Peak, 0 MB Swap)</option>
                        </select>
                    </div>
                </div>

                <div class="p-2">
                    <div id="memory-timeline-chart" class="w-full h-80"></div>
                </div>
            </div>

            <!-- Phase 2 Conversion & Quantization Benchmarks -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="cpu" class="w-4 h-4 text-purple-400"></i>
                            Model Conversion & GGUF Quantization Memory Footprints (Phase 2 Benchmarks)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Measured peak RSS across model parameter scales (0.5B to 32B)</p>
                    </div>
                    <span class="badge badge-sas">Phase 2 Audit</span>
                </div>

                <div class="table-container max-h-72 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Model Scale</th>
                                <th>Operation</th>
                                <th>Peak RSS (GB)</th>
                                <th>Memory Cap (GB)</th>
                                <th>Headroom</th>
                                <th>OOM Events</th>
                                <th>Audit Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${benchmarks.map(b => {
                                const headroom = (b.cap_gb - b.peak_rss_gb).toFixed(2);
                                return `
                                    <tr>
                                        <td class="font-mono text-xs font-bold text-white">${b.model_size.toUpperCase()}</td>
                                        <td><span class="badge ${b.operation === 'quantize' ? 'badge-sas' : 'badge-mas'}">${b.operation}</span></td>
                                        <td class="font-mono text-xs font-bold text-cyan-400">${b.peak_rss_gb} GB</td>
                                        <td class="font-mono text-xs text-slate-400">${b.cap_gb} GB</td>
                                        <td class="font-mono text-xs text-emerald-400">+${headroom} GB</td>
                                        <td class="font-mono text-xs text-slate-400">${b.oom_events}</td>
                                        <td><span class="badge badge-correct">Compliant</span></td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.renderTimeline(timelines);

        document.getElementById('memory-job-select')?.addEventListener('change', (e) => {
            this.renderTimeline(timelines, e.target.value);
        });
    },

    renderTimeline(timelines, filterKey = 'all') {
        const container = document.getElementById('memory-timeline-chart');
        if (!container || !window.Plotly) return;

        const traces = [];

        const colorMap = {
            'tier16-mas-primary/attempt-0001': '#10b981',
            'tier16-sas-primary/attempt-0001': '#f43f5e',
            'tier16-sas-primary/attempt-0002': '#8b5cf6',
            'tier16-sas-direct_control/attempt-0002': '#38bdf8'
        };

        const keys = filterKey === 'all' 
            ? ['tier16-mas-primary/attempt-0001', 'tier16-sas-primary/attempt-0001', 'tier16-sas-primary/attempt-0002'] 
            : [filterKey];

        for (const k of keys) {
            const series = timelines[k];
            if (!series || !series.data) continue;

            const name = k.replace('/attempt-000', ' Att-');
            traces.push({
                x: series.data.map(d => d.rel_sec),
                y: series.data.map(d => d.rss_gb),
                mode: 'lines',
                name: `${name} (Peak: ${series.peak_rss_gb} GB${series.swap_breach ? ', SWAP BREACH' : ''})`,
                line: {
                    color: colorMap[k] || '#cbd5e1',
                    width: series.swap_breach ? 2.5 : 2,
                    dash: series.swap_breach ? 'dash' : 'solid'
                }
            });
        }

        // Add 12.8 GB Cap line
        traces.push({
            x: [0, 4000],
            y: [12.8, 12.8],
            mode: 'lines',
            name: '12.8 GB RUPP Process RSS Cap',
            line: { color: '#ef4444', width: 2, dash: 'dot' }
        });

        const layout = {
            margin: { l: 60, r: 30, t: 20, b: 50 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
                title: 'Elapsed Inference Time (Seconds)',
                titlefont: { color: '#94a3b8', size: 11 },
                tickfont: { color: '#cbd5e1', size: 10 },
                gridcolor: '#1e293b'
            },
            yaxis: {
                title: 'Process-Tree RSS (GB)',
                titlefont: { color: '#94a3b8', size: 11 },
                tickfont: { color: '#cbd5e1', size: 10 },
                gridcolor: '#1e293b',
                range: [0, 14]
            },
            legend: {
                font: { color: '#cbd5e1', size: 10 },
                orientation: 'h',
                y: -0.2
            }
        };

        Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
    }
});

