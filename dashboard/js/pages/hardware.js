/**
 * Memory & Swap: RSS telemetry against the application ceiling and the swap-breach audit.
 */

window.App.registerPage('hardware', {
    state: { selected: null },

    async render(container, app) {
        const timelines = (await app.fetchJson('data/memory_timelines.json')) || {};
        const benchmarks = (await app.fetchJson('data/hardware_benchmarks.json')) || [];
        const jobs = await Data.jobs16();
        this.timelines = timelines;

        const keys = Object.keys(timelines);
        if (!this.state.selected) this.state.selected = new Set(['tier16-mas-primary/attempt-0001', 'tier16-sas-primary/attempt-0001', 'tier16-sas-primary/attempt-0002']);
        const breaches = keys.filter(k => timelines[k].swap_breach);
        const peakJob = Object.values(jobs).reduce((a, b) => (b.peakGb > a.peakGb ? b : a));
        const headroom = Data.APP_CEILING_GB - peakJob.peakGb;

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Resource audit',
                title: `${breaches.length} swap breaches caught, invalidated and re-run`,
                sub: 'Any process-tree swap invalidates a run, because paging to disk would hide a memory overflow. The final continuation ran with kernel memory.swap.max = 0.',
                right: `<div class="flex flex-col gap-2 items-start lg:items-end">${breaches.map(k => `<span class="badge badge-wrong"><i data-lucide="alert-octagon" class="w-3 h-3"></i>${k.replace('tier16-', '')} · ${timelines[k].max_swap_mb.toFixed(1)} MiB</span>`).join('')}</div>`
            })}

            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
                ${UI.kpi({ label: 'Application ceiling', value: Data.APP_CEILING_GB, decimals: 1, suffix: ' GB', foot: `Nominal RUPP cap ${Data.NOMINAL_CAP_GB} GB`, icon: 'gauge', i: 1 })}
                ${UI.kpi({ label: 'Highest peak RSS', value: peakJob.peakGb, decimals: 2, suffix: ' GB', foot: `${peakJob.arm.toUpperCase()} ${Data.PROFILE_LABEL[peakJob.profile].toLowerCase()} · controller + worker`, tone: 'mas', icon: 'memory-stick', i: 2 })}
                ${UI.kpi({ label: 'Tightest headroom', value: headroom * 1000, suffix: ' MB', foot: 'Below the ceiling at peak', tone: headroom < 1 ? 'withheld' : 'correct', icon: 'move-vertical', i: 3 })}
                ${UI.kpi({ label: 'Swap breaches', value: breaches.length, foot: 'Both in SAS attempt-0001 runs', tone: 'wrong', icon: 'hard-drive', i: 4 })}
            </div>

            ${UI.card({
                i: 5,
                title: 'Worker RSS over each run',
                sub: 'Toggle runs to compare. Dashed lines are attempts invalidated by swap.',
                body: `
                    <div id="mem-chips" class="flex flex-wrap gap-2 mb-4">
                        ${keys.map(k => {
                            const t = timelines[k];
                            const on = this.state.selected.has(k);
                            return `<button class="btn text-xs py-1 ${on ? '' : 'opacity-50'}" data-k="${k}">
                                <span class="w-2 h-2 rounded-full" style="background:${this.color(k)}"></span>
                                ${k.replace('tier16-', '').replace('/attempt-000', ' #')}
                                ${t.swap_breach ? '<span class="badge badge-wrong py-0">swap</span>' : ''}
                            </button>`;
                        }).join('')}
                    </div>
                    <div class="h-80"><canvas id="mem-timeline"></canvas></div>`
            })}

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
                ${UI.card({
                    i: 6,
                    title: 'Peak RSS vs the 11.5 GB ceiling',
                    sub: 'Sampled controller-plus-worker peak for each final 16 GB job',
                    body: `
                        <div class="space-y-4">
                            ${Data.PROFILES.flatMap(p => ['sas', 'mas'].map(arm => jobs[`tier16-${arm}-${p}`])).map(j => `
                                <div>
                                    <div class="flex justify-between text-xs mb-1.5">
                                        <span class="flex items-center gap-2">${UI.armBadge(j.arm)}<span class="t-secondary">${Data.PROFILE_LABEL[j.profile]}</span></span>
                                        <span class="font-mono"><span class="t-primary">${j.peakGb.toFixed(2)} GB</span> <span class="t-muted">· ${((Data.APP_CEILING_GB - j.peakGb) * 1000).toFixed(0)} MB spare</span></span>
                                    </div>
                                    ${UI.meter(j.peakGb, Data.APP_CEILING_GB, `linear-gradient(90deg, ${UI.alpha(j.arm, 0.5)}, var(--color-${j.arm}))`)}
                                </div>`).join('')}
                        </div>
                        <div class="mt-5">${UI.insight({ tone: 'mas', icon: 'info', title: 'Fewer parameters, more memory', body: 'MAS keeps three F16 models resident (5B parameters in total) and peaks about 0.87 GB higher than the 14B Q4 monolith.' })}</div>`
                })}
                ${UI.card({
                    i: 7,
                    title: 'Phase 2 conversion and quantization footprints',
                    sub: 'Peak RSS while converting weights and building GGUF Q4_K_M files',
                    body: `<div class="h-72"><canvas id="mem-convert"></canvas></div>
                        <div class="text-xs t-muted mt-3">${benchmarks.length} operations · ${benchmarks.reduce((a, b) => a + (b.oom_events || 0), 0)} OOM events</div>`
                })}
            </div>

            ${UI.card({
                i: 8,
                title: 'Incident log',
                body: `
                    <div class="tl">
                        <div class="tl-item"><div class="tl-dot"></div><div class="text-sm font-semibold">8,192-token context probes hit swap</div><div class="text-xs t-secondary mt-0.5">Common context reduced to 4,096 for both arms and tiers before the accuracy run. Weights and precision unchanged.</div></div>
                        <div class="tl-item alert"><div class="tl-dot"></div><div class="text-sm font-semibold">SAS primary attempt-0001 stopped after 145 cases</div><div class="text-xs t-secondary mt-0.5">44.0 MB process-tree swap at 10.06 GB sampled RSS. Attempt invalidated. Pre-breach checkpoints passed full replay before reuse.</div></div>
                        <div class="tl-item alert"><div class="tl-dot"></div><div class="text-sm font-semibold">SAS direct-control attempt-0001 stopped after 7 cases</div><div class="text-xs t-secondary mt-0.5">34.4 MB swap. Attempt invalidated.</div></div>
                        <div class="tl-item"><div class="tl-dot"></div><div class="text-sm font-semibold">Final continuation under memory.swap.max = 0</div><div class="text-xs t-secondary mt-0.5">User-systemd service. All six jobs completed and the saved-response audit passed. Status remains <span class="font-mono">complete_accuracy_audited_resource_invalid</span>.</div></div>
                    </div>`
            })}
        `;

        document.getElementById('mem-chips').addEventListener('click', e => {
            const b = e.target.closest('button');
            if (!b) return;
            const k = b.dataset.k;
            if (this.state.selected.has(k)) this.state.selected.delete(k); else this.state.selected.add(k);
            b.classList.toggle('opacity-50', !this.state.selected.has(k));
            this.renderTimeline();
        });

        this.renderTimeline();
        this.renderConvert(benchmarks);
    },

    color(k) {
        const palette = {
            'tier16-mas-primary/attempt-0001': UI.css('--color-mas'),
            'tier16-sas-primary/attempt-0001': UI.css('--color-wrong'),
            'tier16-sas-primary/attempt-0002': UI.css('--color-sas'),
            'tier16-sas-direct_control/attempt-0001': '#fb923c',
            'tier16-sas-direct_control/attempt-0002': '#22d3ee',
            'tier16-mas-direct_control/attempt-0001': '#c084fc',
            'tier16-mas-repair_ablation/attempt-0001': '#e879f9',
            'tier16-sas-repair_ablation/attempt-0001': '#2dd4bf'
        };
        return palette[k] || UI.css('--text-muted');
    },

    renderTimeline() {
        this.timelineChart?.destroy();
        const k = UI.colors();
        const keys = [...this.state.selected].filter(x => this.timelines[x]);
        const maxH = Math.max(1, ...keys.map(x => this.timelines[x].duration_sec / 3600));
        const datasets = keys.map(x => {
            const t = this.timelines[x];
            return {
                label: `${x.replace('tier16-', '').replace('/attempt-000', ' #')} · peak ${t.peak_rss_gb} GB`,
                data: t.data.map(d => ({ x: d.rel_sec / 3600, y: d.rss_gb })),
                borderColor: this.color(x), backgroundColor: this.color(x) + '14', fill: 'origin',
                borderWidth: 2, pointRadius: 0, tension: 0.25,
                borderDash: t.swap_breach ? [6, 4] : []
            };
        });
        datasets.push({ label: `Application ceiling ${Data.APP_CEILING_GB} GB`, data: [{ x: 0, y: Data.APP_CEILING_GB }, { x: maxH, y: Data.APP_CEILING_GB }], borderColor: k.wrong, borderWidth: 1.5, borderDash: [2, 3], pointRadius: 0, fill: false });

        const total = 900;
        this.timelineChart = UI.chart('mem-timeline', {
            type: 'line',
            data: { datasets },
            options: {
                responsive: true, maintainAspectRatio: false, parsing: true,
                interaction: { mode: 'nearest', intersect: false },
                animation: {
                    x: { type: 'number', easing: 'linear', duration: 12, from: NaN, delay: ctx => ctx.type === 'data' ? ctx.index * (total / 81) + ctx.datasetIndex * 60 : 0 },
                    y: { type: 'number', easing: 'linear', duration: 12, from: ctx => ctx.chart.scales.y.getPixelForValue(0), delay: ctx => ctx.type === 'data' ? ctx.index * (total / 81) + ctx.datasetIndex * 60 : 0 }
                },
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: { callbacks: { title: i => `${i[0].parsed.x.toFixed(2)} h`, label: c => `${c.dataset.label.split(' · ')[0]}: ${c.parsed.y.toFixed(2)} GB` } }
                },
                scales: {
                    x: { type: 'linear', min: 0, title: { display: true, text: 'Elapsed hours' } },
                    y: { min: 0, max: 13, title: { display: true, text: 'RSS (GB)' } }
                }
            }
        });
    },

    renderConvert(benchmarks) {
        const rows = [...benchmarks].sort((a, b) => a.peak_rss_gb - b.peak_rss_gb);
        const k = UI.colors();
        UI.chart('mem-convert', {
            type: 'bar',
            data: {
                labels: rows.map(b => `${b.model_size.toUpperCase()} ${b.operation}`),
                datasets: [{
                    label: 'Peak RSS (GB)',
                    data: rows.map(b => b.peak_rss_gb),
                    backgroundColor: rows.map(b => b.operation === 'quantize' ? UI.alpha('sas', 0.8) : UI.alpha('mas', 0.8)),
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y', responsive: true, maintainAspectRatio: false,
                animation: { delay: ctx => ctx.type === 'data' ? ctx.dataIndex * 90 : 0 },
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => `${c.parsed.x.toFixed(2)} GB of ${rows[c.dataIndex].cap_gb} GB cap` } } },
                scales: { x: { beginAtZero: true, title: { display: true, text: 'GB' } }, y: { grid: { display: false }, ticks: { color: k.text } } }
            }
        });
    }
});
