/**
 * Hardware & Memory Telemetry Page - Minimal, Plain, Publication-Grade
 */

window.App.registerPage('hardware', {
    async render(container, app) {
        const timelines = await app.fetchJson('data/memory_timelines.json') || {};
        const benchmarks = await app.fetchJson('data/hardware_benchmarks.json') || [];

        container.innerHTML = `
            <!-- Technical Overview Box (Plain, Structured) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">RUPP Protocol Telemetry</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Process-Tree RSS & Swap Breach Audit
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            Continuous sub-second cgroup monitoring ensures that model inference remains strictly within host physical RAM caps (12.8 GB on 16 GB machines). Any swap allocation automatically invalidates the run to prevent disk paging from masking memory overflow.
                        </p>
                    </div>
                    <div class="shrink-0 text-right">
                        <div class="text-[11px] text-slate-400 font-mono">Process RSS Cap</div>
                        <div class="text-base font-bold font-mono text-white">12.8 GB Nominal</div>
                    </div>
                </div>
            </div>

            <!-- Invalidation Incident Note (Clean, Muted) -->
            <div class="card p-4 border border-amber-900/40 bg-amber-950/10 flex items-start gap-3">
                <div class="p-1 rounded bg-amber-900/30 text-amber-400 mt-0.5">
                    <i data-lucide="info" class="w-4 h-4"></i>
                </div>
                <div class="text-xs text-slate-300 leading-relaxed">
                    <span class="font-semibold text-white">Audited Swap Failure & Invalidation:</span> 
                    During <span class="font-mono text-slate-200">tier16-sas-primary</span> (attempt-0001), transient host memory pressure induced a <span class="font-mono text-rose-400 font-bold">41.97 MB</span> swap breach. Under Section §6.2 of the protocol, this attempt was marked <span class="badge badge-wrong font-mono">INVALID</span>. A clean second run (attempt-0002) completed under strict 0 MB swap isolation.
                </div>
            </div>

            <!-- Memory Timeline Chart -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-2">
                    <div>
                        <h3 class="text-sm font-semibold text-white">Continuous Process-Tree Memory Timeline</h3>
                        <p class="text-xs text-slate-400">Process RSS in GB over elapsed inference time (recorded at sub-second polling)</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-slate-400">Job:</span>
                        <select id="memory-job-select" class="select-filter text-xs">
                            <option value="all" selected>Key 16 GB Runs Overlay</option>
                            <option value="tier16-mas-primary/attempt-0001">MAS Primary (10.18 GB Peak, 0 MB Swap)</option>
                            <option value="tier16-sas-primary/attempt-0001">SAS Attempt 1 (41.97 MB Swap Breach)</option>
                            <option value="tier16-sas-primary/attempt-0002">SAS Attempt 2 (9.37 GB Peak, 0 MB Swap)</option>
                        </select>
                    </div>
                </div>

                <div class="p-2">
                    <div id="memory-timeline-chart" class="w-full h-72"></div>
                </div>
            </div>

            <!-- Phase 2 Conversion Benchmarks -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Model Conversion & Quantization Peak RSS (Phase 2 Audits)</h3>
                    <p class="text-xs text-slate-400">Peak resident set size measured during conversion and GGUF quantization (0.5B to 32B)</p>
                </div>

                <div class="table-container max-h-64 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Model Scale</th>
                                <th>Operation</th>
                                <th>Peak RSS (GB)</th>
                                <th>Assigned Cap (GB)</th>
                                <th>Safety Headroom</th>
                                <th>cgroup OOM</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${benchmarks.map(b => {
                                const headroom = (b.cap_gb - b.peak_rss_gb).toFixed(2);
                                return `
                                    <tr>
                                        <td class="font-mono text-xs font-semibold text-white">${b.model_size.toUpperCase()}</td>
                                        <td><span class="badge ${b.operation === 'quantize' ? 'badge-sas' : 'badge-mas'}">${b.operation}</span></td>
                                        <td class="font-mono text-xs text-slate-200">${b.peak_rss_gb} GB</td>
                                        <td class="font-mono text-xs text-slate-400">${b.cap_gb} GB</td>
                                        <td class="font-mono text-xs text-emerald-400">+${headroom} GB</td>
                                        <td class="font-mono text-xs text-slate-400">0</td>
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
            'tier16-mas-primary/attempt-0001': '#388bfd',
            'tier16-sas-primary/attempt-0001': '#f85149',
            'tier16-sas-primary/attempt-0002': '#8b949e',
            'tier16-sas-direct_control/attempt-0002': '#6e7681'
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
                name: `${name} (Peak: ${series.peak_rss_gb} GB${series.swap_breach ? ', Swap Breach' : ''})`,
                line: {
                    color: colorMap[k] || '#8b949e',
                    width: series.swap_breach ? 2 : 1.5,
                    dash: series.swap_breach ? 'dash' : 'solid'
                }
            });
        }

        // 12.8 GB Cap Line
        traces.push({
            x: [0, 4000],
            y: [12.8, 12.8],
            mode: 'lines',
            name: '12.8 GB RUPP Cap',
            line: { color: '#f85149', width: 1.5, dash: 'dot' }
        });

        const layout = {
            margin: { l: 50, r: 20, t: 10, b: 40 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            xaxis: {
                title: 'Elapsed Inference Time (Seconds)',
                titlefont: { color: '#8b949e', size: 11, family: 'Inter' },
                tickfont: { color: '#8b949e', size: 10, family: 'JetBrains Mono' },
                gridcolor: '#242c38'
            },
            yaxis: {
                title: 'Process RSS (GB)',
                titlefont: { color: '#8b949e', size: 11, family: 'Inter' },
                tickfont: { color: '#8b949e', size: 10, family: 'JetBrains Mono' },
                gridcolor: '#242c38',
                range: [0, 14]
            },
            legend: {
                font: { color: '#8b949e', size: 10, family: 'Inter' },
                orientation: 'h',
                y: -0.2
            }
        };

        Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
    }
});
