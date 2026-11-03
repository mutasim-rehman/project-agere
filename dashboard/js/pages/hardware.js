/**
 * Hardware & Memory Telemetry Page - Academic Light Theme
 */

window.App.registerPage('hardware', {
    async render(container, app) {
        const timelines = await app.fetchJson('data/memory_timelines.json') || {};
        const benchmarks = await app.fetchJson('data/hardware_benchmarks.json') || [];

        container.innerHTML = `
            <!-- Top Hardware Header (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div class="space-y-1 max-w-4xl">
                        <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                            RUPP Protocol Telemetry • Linux cgroup Audits
                        </div>
                        <h2 class="text-base font-bold text-[#172033]">
                            Process-Tree RSS Constraints & Swap Breach Audit
                        </h2>
                        <p class="text-xs text-[#64748B] leading-relaxed">
                            Continuous sub-second cgroup monitoring ensures model inference remains strictly within physical RAM allocations (12.8 GB on 16 GB workstations; 6.4 GB on 8 GB workstations after reserving 20% for host OS and background processes). Any nonzero swap usage automatically invalidates the deployment.
                        </p>
                    </div>
                    <div class="shrink-0 text-right font-mono">
                        <div class="text-[11px] text-[#64748B]">Process Cap (16 GB)</div>
                        <div class="text-base font-bold text-[#172033]">12.8 GB Nominal Limit</div>
                    </div>
                </div>
            </div>

            <!-- Invalidation Incident Card (Clean Academic Notice) -->
            <div class="card p-4 border border-[#FDE68A] bg-[#FFFBEB] flex items-start gap-3">
                <div class="p-1 rounded bg-[#FEF3C7] text-[#D97706] mt-0.5 shrink-0">
                    <i data-lucide="alert-triangle" class="w-4 h-4"></i>
                </div>
                <div class="text-xs text-[#92400E] leading-relaxed">
                    <strong class="text-[#78350F]">Audited Invalidation Incident:</strong> During <span class="font-mono text-[#172033]">tier16-sas-primary</span> (attempt-0001), transient host memory pressure induced a <span class="font-mono text-[#DC2626] font-bold">41.97 MB</span> swap breach. In accordance with Section §6.2 of the specification, the run was marked <span class="badge badge-wrong font-mono">RESOURCE-INVALID</span>. A second attempt (attempt-0002) was executed with zero swap, establishing strict compliance.
                </div>
            </div>

            <!-- Continuous Memory Timeline Chart -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Continuous Process-Tree Memory Timeline</h3>
                        <p class="text-xs text-[#64748B]">Process RSS in GB over elapsed inference seconds (downsampled from 500,000 telemetry samples)</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-[#64748B]">Job Filter:</span>
                        <select id="memory-job-select" class="select-filter text-xs">
                            <option value="all" selected>Key 16 GB Runs Overlay</option>
                            <option value="tier16-mas-primary/attempt-0001">MAS Primary (10.18 GB Peak, 0 MB Swap)</option>
                            <option value="tier16-sas-primary/attempt-0001">SAS Attempt 1 (41.97 MB Swap Breach)</option>
                            <option value="tier16-sas-primary/attempt-0002">SAS Attempt 2 (9.37 GB Peak, 0 MB Swap)</option>
                        </select>
                    </div>
                </div>

                <div class="pt-3">
                    <div id="memory-timeline-chart" class="w-full h-80"></div>
                </div>
            </div>

            <!-- Phase 2 Conversion Benchmarks -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Model Conversion & Quantization Peak RSS (Phase 2 Benchmarks)</h3>
                        <p class="text-xs text-[#64748B]">Peak resident set size measured during conversion and GGUF quantization (0.5B to 32B)</p>
                    </div>
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
                                        <td class="font-mono text-xs font-bold text-[#172033]">${b.model_size.toUpperCase()}</td>
                                        <td><span class="badge ${b.operation === 'quantize' ? 'badge-mas' : 'badge-sas'}">${b.operation}</span></td>
                                        <td class="font-mono text-xs text-[#172033] font-semibold">${b.peak_rss_gb} GB</td>
                                        <td class="font-mono text-xs text-[#64748B]">${b.cap_gb} GB</td>
                                        <td class="font-mono text-xs text-[#15803D] font-medium">+${headroom} GB</td>
                                        <td class="font-mono text-xs text-[#64748B]">0</td>
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
            'tier16-mas-primary/attempt-0001': '#2563EB',
            'tier16-sas-primary/attempt-0001': '#DC2626',
            'tier16-sas-primary/attempt-0002': '#64748B',
            'tier16-sas-direct_control/attempt-0002': '#94A3B8'
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
                    color: colorMap[k] || '#64748B',
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
            name: '12.8 GB RUPP Process Cap',
            line: { color: '#DC2626', width: 1.5, dash: 'dot' }
        });

        const layout = {
            margin: { l: 50, r: 20, t: 10, b: 40 },
            paper_bgcolor: '#FFFFFF',
            plot_bgcolor: '#FFFFFF',
            xaxis: {
                title: 'Elapsed Inference Time (Seconds)',
                titlefont: { color: '#64748B', size: 11, family: 'Inter' },
                tickfont: { color: '#64748B', size: 10, family: 'JetBrains Mono' },
                gridcolor: '#E9EEF5'
            },
            yaxis: {
                title: 'Process RSS (GB)',
                titlefont: { color: '#64748B', size: 11, family: 'Inter' },
                tickfont: { color: '#64748B', size: 10, family: 'JetBrains Mono' },
                gridcolor: '#E9EEF5',
                range: [0, 14]
            },
            legend: {
                font: { color: '#172033', size: 10, family: 'Inter' },
                orientation: 'h',
                y: -0.2
            }
        };

        Plotly.newPlot(container, traces, layout, { responsive: true, displayModeBar: false });
    }
});
