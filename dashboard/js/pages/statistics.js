/**
 * Statistics: the 126-test battery as a picture first, table second.
 */

window.App.registerPage('statistics', {
    state: { tests: [], tierFilter: 'all', metricFilter: 'all', search: '' },

    figures: [
        ['P01_paired_transitions', 'Paired transitions', 'State transitions between MAS and SAS across correct, wrong and withheld.'],
        ['P02_bootstrap_distributions', 'Bootstrap distributions', 'Report-cluster bootstrap distributions for paired differences.'],
        ['P03_report_scatter', 'Report scatter', 'Accuracy dispersion by company-year report.'],
        ['P04_program_complexity', 'Program complexity', 'Outcomes by reference program length.'],
        ['P05_latency_distributions', 'Latency', 'Per-case inference latency by arm.'],
        ['P06_memory_timelines', 'Memory timelines', 'Process-tree RSS over each run.'],
        ['P07_stage_costs', 'Stage costs', 'Token and time cost per pipeline stage.'],
        ['P08_tier8_inventory', '8 GB inventory', 'All 15 completed 8 GB configurations.'],
        ['P09_utility_kappa', 'Utility & kappa', 'Utility sensitivity and metric agreement.']
    ],

    async render(container, app) {
        if (!this.state.tests.length) {
            this.state.tests = ((await app.fetchJson('data/paper/paper_statistical_tests.rows.json')) || []).map(t => ({
                ...t, deff: parseFloat(t.deff_report), tierNum: String(t.tier).replace('tier', '')
            }));
        }
        const tests = this.state.tests;
        const iidSig = tests.filter(t => t.exact_mcnemar_p < 0.05).length;
        const clSig = tests.filter(t => t.durkalski_report_p < 0.05).length;
        const lost = tests.filter(t => t.exact_mcnemar_p < 0.05 && t.durkalski_report_p >= 0.05).length;
        const deffs = tests.map(t => t.deff).filter(v => !isNaN(v) && v > 0).sort((a, b) => a - b);
        const medDeff = deffs[Math.floor(deffs.length / 2)];
        const primary = tests.find(t => t.tier === 'tier16' && t.comparison === 'primary' && t.metric === 'reported' && t.event === 'C');

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Inferential statistics',
                title: `Clustering matters: <span class="grad-text">${lost} of ${iidSig}</span> naive "significant" results disappear`,
                sub: 'Questions from the same 10-K report are correlated. Treating them as independent overstates certainty. The primary SAS advantage survives every adjustment.',
                right: `<div class="text-right"><div class="text-xs t-muted">Primary contrast, report-clustered</div><div class="text-2xl font-bold font-mono c-correct mt-1">p = ${UI.fmtP(primary?.durkalski_report_p)}</div></div>`
            })}

            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
                ${UI.kpi({ label: 'Hypothesis tests', value: tests.length, foot: '21 contrasts × 2 metrics × 3 outcomes', icon: 'list-checks', i: 1 })}
                ${UI.kpi({ label: 'Significant, case-IID', value: iidSig, foot: 'Exact McNemar p < 0.05', tone: 'withheld', icon: 'alert-triangle', i: 2 })}
                ${UI.kpi({ label: 'Significant, report-clustered', value: clSig, foot: 'Durkalski p < 0.05', tone: 'correct', icon: 'shield-check', i: 3 })}
                ${UI.kpi({ label: 'Median design effect', value: medDeff, decimals: 2, suffix: '×', foot: `Range ${deffs[0].toFixed(2)}–${deffs[deffs.length - 1].toFixed(2)}× variance inflation`, tone: 'mas', icon: 'sigma', i: 4 })}
            </div>

            ${UI.card({
                i: 5,
                title: 'Effect size vs evidence strength',
                sub: 'Each point is one test. Points above the dashed line are significant after report clustering. Hover for details.',
                right: `<div class="seg" id="volcano-p"><button data-v="durkalski_report_p" class="on">Clustered p</button><button data-v="exact_mcnemar_p">Case-IID p</button></div>`,
                body: `<div id="stat-volcano" class="w-full h-[400px]"></div>`
            })}

            ${UI.card({
                i: 6,
                title: 'Publication figures',
                sub: 'Click to open at full resolution',
                body: `
                    <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-9 gap-3">
                        ${this.figures.map(([f, t, c], i) => `
                            <div class="card figure-tile card-hover reveal" style="--i:${7 + i * 0.5}" onclick="App.showFigure('figures/paper/${f}.png', '${f.slice(0, 3)} · ${t}', '${c}')">
                                <div class="overflow-hidden h-24"><img src="figures/paper/${f}.png" alt="${t}" loading="lazy" class="w-full h-24 object-cover"></div>
                                <div class="px-2.5 py-2"><div class="text-[10px] font-mono c-accent">${f.slice(0, 3)}</div><div class="text-xs font-medium truncate">${t}</div></div>
                            </div>`).join('')}
                    </div>`
            })}

            ${UI.disclosure({
                i: 7,
                title: 'Full hypothesis table',
                meta: `${tests.length} rows`,
                body: `
                    <div class="flex flex-wrap items-center gap-2 mb-3">
                        <select id="stat-tier-filter" class="select-filter">
                            <option value="all">Both tiers</option><option value="16">16 GB</option><option value="8">8 GB</option>
                        </select>
                        <select id="stat-metric-filter" class="select-filter">
                            <option value="all">Both metrics</option><option value="reported">Reported answer</option><option value="raw">Raw execution</option>
                        </select>
                        <input id="stat-search-input" type="text" placeholder="Filter contrast…" class="input-search">
                        <span id="stat-count" class="text-xs t-muted ml-auto"></span>
                    </div>
                    <div class="table-container max-h-[480px]">
                        <table class="data-table">
                            <thead><tr><th>Contrast</th><th>Tier</th><th>Metric</th><th>Outcome</th><th>n</th><th class="text-right">Δ</th><th>Bootstrap 95% CI</th><th class="text-right">McNemar p</th><th class="text-right">Clustered p</th><th class="text-right">DEFF</th></tr></thead>
                            <tbody id="stat-table-body"></tbody>
                        </table>
                    </div>`
            })}
        `;

        this.bindEvents();
        this.renderTable();
        this.renderVolcano('durkalski_report_p');
    },

    bindEvents() {
        const update = () => this.renderTable();
        document.getElementById('stat-tier-filter')?.addEventListener('change', e => { this.state.tierFilter = e.target.value; update(); });
        document.getElementById('stat-metric-filter')?.addEventListener('change', e => { this.state.metricFilter = e.target.value; update(); });
        document.getElementById('stat-search-input')?.addEventListener('input', e => { this.state.search = e.target.value.toLowerCase().trim(); update(); });
        document.getElementById('volcano-p')?.addEventListener('click', e => {
            const b = e.target.closest('button');
            if (!b) return;
            b.parentElement.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
            this.renderVolcano(b.dataset.v);
        });
    },

    renderVolcano(pKey) {
        const el = document.getElementById('stat-volcano');
        if (!el || !window.Plotly) return;
        const k = UI.colors();
        const eventName = { C: 'correct', W: 'wrong', H: 'withheld' };
        const groups = [
            { name: '16 GB', filter: t => t.tier === 'tier16', color: k.sas },
            { name: '8 GB', filter: t => t.tier === 'tier8', color: k.mas }
        ];
        const yOf = t => Math.min(28, -Math.log10(Math.max(t[pKey], 1e-28)));
        const yMax = Math.max(...this.state.tests.map(yOf)) * 1.12 + 0.5;
        const traces = groups.map(g => {
            const rows = this.state.tests.filter(g.filter);
            return {
                type: 'scatter', mode: 'markers', name: g.name,
                x: rows.map(t => 100 * t.delta),
                y: rows.map(() => 0),
                marker: {
                    size: rows.map(t => t.event === 'C' ? 12 : 8),
                    color: rows.map(t => t[pKey] < 0.05 ? g.color : 'rgba(0,0,0,0)'),
                    line: { color: g.color, width: 1.5 },
                    symbol: rows.map(t => t.metric === 'raw' ? 'square' : 'circle'),
                    opacity: 0.9
                },
                customdata: rows.map(yOf),
                hovertemplate: rows.map(t => `<b>${UI.esc(t.label)}</b><br>${t.metric} · ${eventName[t.event]}<br>Δ ${(100 * t.delta).toFixed(1)} pp<br>p = ${UI.fmtP(t[pKey])}<extra>${g.name}</extra>`)
            };
        });
        const layout = UI.plotLayout({
            margin: { l: 55, r: 20, t: 10, b: 45 },
            xaxis: { title: { text: 'Effect size Δ (percentage points)' }, zeroline: true, zerolinewidth: 1.5 },
            yaxis: { title: { text: '−log₁₀ p' }, range: [-0.3, yMax] },
            legend: { orientation: 'h', y: 1.08, x: 1, xanchor: 'right' },
            shapes: [{ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: -Math.log10(0.05), y1: -Math.log10(0.05), line: { color: k.withheld, dash: 'dash', width: 1.5 } }],
            annotations: [{ xref: 'paper', x: 0.005, y: -Math.log10(0.05), yanchor: 'bottom', xanchor: 'left', text: 'p = 0.05', showarrow: false, font: { color: k.withheld, size: 10 } }]
        });
        Plotly.newPlot(el, traces, layout, UI.plotConfig).then(() => {
            Plotly.animate(el, { data: traces.map(t => ({ y: t.customdata })), traces: [0, 1] },
                { transition: { duration: 1000, easing: 'cubic-out' }, frame: { duration: 1000, redraw: false } });
        });
    },

    renderTable() {
        const tbody = document.getElementById('stat-table-body');
        if (!tbody) return;
        const st = this.state;
        let list = st.tests;
        if (st.tierFilter !== 'all') list = list.filter(t => t.tierNum === st.tierFilter);
        if (st.metricFilter !== 'all') list = list.filter(t => t.metric === st.metricFilter);
        if (st.search) list = list.filter(t => (t.label || '').toLowerCase().includes(st.search) || (t.comparison || '').toLowerCase().includes(st.search));
        document.getElementById('stat-count').innerText = `${list.length} tests`;
        const ev = { C: 'correct', W: 'wrong', H: 'withheld' };

        tbody.innerHTML = list.length ? list.map(t => {
            const sig = t.durkalski_report_p < 0.05;
            return `
                <tr>
                    <td class="text-xs font-medium">${UI.esc(t.label || t.comparison)}</td>
                    <td class="font-mono text-xs t-secondary">${t.tierNum} GB</td>
                    <td class="text-xs t-secondary">${t.metric}</td>
                    <td>${UI.outcomeBadge(ev[t.event])}</td>
                    <td class="font-mono text-xs t-muted">${t.n}</td>
                    <td class="font-mono text-xs text-right font-semibold ${t.delta < 0 ? 'c-wrong' : t.delta > 0 ? 'c-correct' : 't-muted'}">${t.delta > 0 ? '+' : ''}${(100 * t.delta).toFixed(1)}</td>
                    <td class="font-mono text-[11px] t-secondary">[${(100 * t.boot95_low).toFixed(1)}, ${(100 * t.boot95_high).toFixed(1)}]</td>
                    <td class="font-mono text-xs text-right t-secondary">${UI.fmtP(t.exact_mcnemar_p)}</td>
                    <td class="font-mono text-xs text-right ${sig ? 'c-correct font-semibold' : 't-muted'}">${UI.fmtP(t.durkalski_report_p)}</td>
                    <td class="font-mono text-xs text-right t-muted">${isNaN(t.deff) ? '—' : t.deff.toFixed(2)}</td>
                </tr>`;
        }).join('') : `<tr><td colspan="10" class="text-center py-6 t-muted text-xs">No matching tests.</td></tr>`;
    }
});
