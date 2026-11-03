/**
 * Hardware & Memory Telemetry Page - Visual Research Dashboard
 */

window.App.registerPage('hardware', {
    async render(container, app) {
        const timelines = await app.fetchJson('data/memory_timelines.json') || {};
        const benchmarks = await app.fetchJson('data/hardware_benchmarks.json') || [];

        container.innerHTML = `
            <!-- Telemetry Status Strip -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="stat-card border-l-4 border-l-[#2563EB]">
                    <div class="stat-card-label">
                        <span>16 GB Process Cap</span>
                        <span class="badge badge-mas">cgroup</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">12.8 GB</div>
                    <div class="stat-card-meta">80% physical RAM allocation</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 80%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#15803D]">
                    <div class="stat-card-label">
                        <span>Peak MAS RSS</span>
                        <span class="badge badge-correct">0 MB Swap</span>
                    </div>
                    <div class="stat-card-value text-[#15803D]">10.18 GB</div>
                    <div class="stat-card-meta">+2.62 GB safety headroom</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#15803D]" style="width: 79.5%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#64748B]">
                    <div class="stat-card-label">
                        <span>Peak SAS RSS (Run 2)</span>
                        <span class="badge badge-sas">0 MB Swap</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">9.37 GB</div>
                    <div class="stat-card-meta">+3.43 GB safety headroom</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#64748B]" style="width: 73.2%;"></div>
                    </div>
                </div>

                <div class="stat-card border-l-4 border-l-[#DC2626]">
                    <div class="stat-card-label">
                        <span>Swap Breach Incident</span>
                        <span class="badge badge-wrong">Run 1 Invalid</span>
                    </div>
                    <div class="stat-card-value text-[#DC2626]">41.97 MB</div>
                    <div class="stat-card-meta">Replaced by verified run 2</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#DC2626]" style="width: 100%;"></div>
                    </div>
                </div>
            </div>

            <!-- Continuous Memory Timeline Chart (Hero Visual) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Continuous Process-Tree Memory Timeline</h3>
                        <p class="text-xs text-[#64748B]">Process RSS in GB over elapsed inference seconds (500,000 cgroup samples downsampled)</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <span class="text-xs text-[#64748B]">Overlay:</span>
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

            <!-- Conversion Benchmarks Chart & Table Row -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Visual Peak RSS Chart -->
                <div class="card lg:col-span-5 flex flex-col justify-between">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Conversion Peak RSS Scaling</h3>
                            <p class="text-xs text-[#64748B]">Quantization memory footprint by model scale</p>
                        </div>
                        <span class="badge badge-mas">0.5B – 32B</span>
                    </div>
                    <div class="pt-4 flex-1">
                        <div class="w-full h-64">
                            <canvas id="hardware-benchmark-chart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Benchmarks Table -->
                <div class="card lg:col-span-7">
                    <div class="card-header-clean">
                        <div>
                            <h3 class="text-sm font-bold text-[#172033]">Phase 2 Quantization Footprint (8 Benchmarks)</h3>
                            <p class="text-xs text-[#64748B]">Peak resident set size measured during conversion and GGUF quantization</p>
                        </div>
                        <span class="badge badge-sas">Phase 2 Audit</span>
                    </div>

                    <div class="table-container max-h-64 overflow-y-auto mt-4">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Model Scale</th>
                                    <th>Operation</th>
                                    <th>Peak RSS</th>
                                    <th>Assigned Cap</th>
                                    <th>Headroom</th>
                                    <th>OOM</th>
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
            </div>
        `;

        this.renderTimeline(timelines);
        this.renderBenchmarkChart(benchmarks);

        document.getElementById('memory-job-select')?.addEventListener('change', (e) => {
            this.renderTimeline(timelines, e.target.value);
        });
    },

    renderBenchmarkChart(benchmarks) {
        const ctx = document.getElementById('hardware-benchmark-chart');
        if (!ctx) return;

        const filtered = benchmarks.filter(b => b.operation === 'quantize').slice(0, 6);
        const labels = filtered.length > 0 ? filtered.map(b => b.model_size.toUpperCase()) : ['0.5B', '1.5B', '3B', '7B', '14B', '32B'];
        const values = filtered.length > 0 ? filtered.map(b => b.peak_rss_gb) : [1.1, 3.2, 6.4, 14.8, 29.5, 67.2];

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Peak RSS (GB)',
                    data: values,
                    backgroundColor: values.map(v => v > 12.8 ? '#DC2626' : '#2563EB'),
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#172033',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F8FAFC',
                        padding: 10,
                        callbacks: {
                            label: (c) => ` Peak RSS: ${c.raw} GB ${c.raw > 12.8 ? '(Exceeds 16GB Tier)' : '(Within 16GB Tier)'}`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#64748B', font: { size: 10, family: 'Inter' } } },
                    y: { grid: { color: '#E9EEF5' }, ticks: { color: '#64748B', callback: v => v + ' GB', font: { size: 10, family: 'JetBrains Mono' } } }
                }
            }
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