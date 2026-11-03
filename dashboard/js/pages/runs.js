/**
 * 8 GB tier & runs: the development inventory and evidence catalog.
 */

window.App.registerPage('runs', {
    state: { search: '', metric: 'reported' },

    async render(container, app) {
        const evidence = (await app.fetchJson('data/le16_v2/tier8_evidence_catalog.json')) || [];
        const archive = (await app.fetchJson('data/archive_stats.json')) || {};
        const conds = await Data.tier8Conditions();
        this.evidence = evidence;
        this.conds = conds;

        const pairs = conds.filter(c => c.arm === 'mas').map(m => {
            const s = conds.find(c => c.arm === 'sas' && c.cohort === m.cohort && c.name === m.name.replace(/mas$/, 'sas'));
            return s ? { cohort: m.cohort, name: m.name.replace(/_mas$/, ''), mas: m, sas: s } : null;
        }).filter(Boolean);
        const sasWins = pairs.filter(p => p.sas.reported.C > p.mas.reported.C).length;
        const avgPeak = arm => conds.filter(c => c.arm === arm).reduce((a, c) => a + c.peakGb, 0) / conds.filter(c => c.arm === arm).length;
        const totalOutputs = conds.reduce((a, c) => a + c.n, 0);

        container.innerHTML = `
            ${UI.hero({
                eyebrow: '8 GB development tier',
                title: `SAS leads in <span class="grad-text">${sasWins} of ${pairs.length}</span> matched 8 GB pairs`,
                sub: '15 completed configurations on 101 FinQA questions from 30 reports, all within a 6.4 GB nominal budget. These are development runs with repeated questions, not independent replications.'
            })}

            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
                ${UI.kpi({ label: 'Configurations', value: conds.length, foot: `${totalOutputs} case outputs`, icon: 'layers', i: 1 })}
                ${UI.kpi({ label: 'Avg SAS peak RSS', value: avgPeak('sas'), decimals: 2, suffix: ' GB', foot: '7B Q4 + trained adapter', tone: 'sas', icon: 'memory-stick', i: 2 })}
                ${UI.kpi({ label: 'Avg MAS peak RSS', value: avgPeak('mas'), decimals: 2, suffix: ' GB', foot: 'Shared 3B Q4 role backbone', tone: 'mas', icon: 'memory-stick', i: 3 })}
                ${UI.kpi({ label: 'Evidence on SSD', value: archive.total_mb || 645, decimals: 0, suffix: ' MB', foot: `${UI.num(archive.total_files || 2598)} files · ${evidence.length} cataloged artifacts`, tone: 'withheld', icon: 'archive', i: 4 })}
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
                ${UI.card({
                    cls: 'xl:col-span-3', i: 5,
                    title: 'Matched MAS vs SAS pairs',
                    sub: 'Correct answers on the same questions. Each row is one configuration pair.',
                    body: `<div class="h-72"><canvas id="runs-pairs"></canvas></div>`
                })}
                ${UI.card({
                    cls: 'xl:col-span-2', i: 6,
                    title: 'Evidence archive',
                    sub: 'Files by category',
                    body: `<div class="h-56"><canvas id="runs-archive"></canvas></div>`
                })}
            </div>

            ${UI.card({
                i: 7,
                title: 'Every 8 GB configuration',
                sub: 'Outcome mix per configuration, sorted by correct answers',
                right: `<div class="flex items-center gap-3">${UI.outcomeLegend()}<div class="seg" id="runs-metric"><button data-v="reported" class="on">Reported</button><button data-v="raw">Raw</button></div></div>`,
                body: `<div id="runs-bars" class="space-y-2.5"></div>`
            })}

            ${UI.disclosure({
                i: 8,
                title: 'Historical evidence catalog',
                meta: `${evidence.length} artifacts`,
                body: `
                    <input id="evidence-search" type="text" placeholder="Filter by file or status…" class="input-search w-full md:w-80 mb-3">
                    <div class="table-container max-h-96">
                        <table class="data-table">
                            <thead><tr><th>Artifact</th><th>Status</th><th>SHA-256</th></tr></thead>
                            <tbody id="evidence-table-body"></tbody>
                        </table>
                    </div>`
            })}
        `;

        this.renderBars();
        this.renderEvidenceRows();
        this.renderCharts(pairs, archive);

        document.getElementById('runs-metric').addEventListener('click', e => {
            const b = e.target.closest('button');
            if (!b) return;
            b.parentElement.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
            this.state.metric = b.dataset.v;
            this.renderBars();
        });
        document.getElementById('evidence-search')?.addEventListener('input', e => {
            this.state.search = e.target.value.toLowerCase().trim();
            this.renderEvidenceRows();
        });
    },

    renderBars() {
        const m = this.state.metric;
        const rows = [...this.conds].sort((a, b) => b[m].C / b.n - a[m].C / a.n);
        const box = document.getElementById('runs-bars');
        box.innerHTML = rows.map(c => `
            <div class="grid grid-cols-12 items-center gap-3">
                <div class="col-span-12 md:col-span-4 flex items-center gap-2 min-w-0 text-xs">
                    ${UI.armBadge(c.arm)}
                    <span class="truncate" title="${c.job}">${c.name.replace(/_/g, ' ')}</span>
                    <span class="badge py-0 ${c.cohort === 'reserved' ? 'badge-withheld' : ''}">${c.cohort}</span>
                </div>
                <div class="col-span-9 md:col-span-6">${UI.stackbar(c[m].C, c[m].W, c[m].H, c.n)}</div>
                <div class="col-span-3 md:col-span-2 text-right font-mono text-xs"><span class="t-primary">${UI.pct(c[m].C, c.n)}%</span> <span class="t-muted">· ${c.peakGb.toFixed(2)} GB</span></div>
            </div>`).join('');
        UI.animateIn(box);
    },

    renderCharts(pairs, archive) {
        UI.chart('runs-pairs', {
            type: 'bar',
            data: {
                labels: pairs.map(p => `${p.cohort} · ${p.name.replace(/_/g, ' ')}`),
                datasets: ['sas', 'mas'].map(arm => ({
                    label: arm.toUpperCase(),
                    data: pairs.map(p => 100 * p[arm].reported.C / p[arm].n),
                    backgroundColor: UI.alpha(arm, 0.85), borderRadius: 6, barPercentage: 0.8, categoryPercentage: 0.7
                }))
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { delay: ctx => ctx.type === 'data' ? ctx.dataIndex * 110 + ctx.datasetIndex * 60 : 0 },
                plugins: {
                    legend: { position: 'top', align: 'end' },
                    tooltip: { callbacks: { label: c => { const p = pairs[c.dataIndex][c.dataset.label.toLowerCase()]; return `${c.dataset.label}: ${p.reported.C}/${p.n} correct (${c.parsed.y.toFixed(1)}%)`; } } }
                },
                scales: { x: { grid: { display: false } }, y: { beginAtZero: true, ticks: { callback: v => v + '%' } } }
            }
        });

        const cats = archive.by_category || [];
        const palette = [UI.css('--color-sas'), UI.css('--color-mas'), UI.css('--color-withheld'), UI.css('--color-correct')];
        UI.chart('runs-archive', {
            type: 'doughnut',
            data: { labels: cats.map(c => c.category), datasets: [{ data: cats.map(c => c.count), backgroundColor: palette, borderWidth: 0, hoverOffset: 8 }] },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '68%',
                animation: { animateRotate: true, duration: 1300 },
                plugins: {
                    legend: { position: 'right' },
                    tooltip: { callbacks: { label: c => `${c.label}: ${UI.num(c.parsed)} files · ${cats[c.dataIndex].mb} MB` } }
                }
            }
        });
    },

    renderEvidenceRows() {
        const tbody = document.getElementById('evidence-table-body');
        if (!tbody) return;
        const q = this.state.search;
        const items = q ? this.evidence.filter(it => `${it.file} ${it.status}`.toLowerCase().includes(q)) : this.evidence;
        const tone = s => /complete|verified|pass|proven|True/i.test(s) ? 'badge-correct' : /fail|refused|rejected|interrupted|stopped/i.test(s) ? 'badge-wrong' : /launched|prepared|superseded/i.test(s) ? 'badge-withheld' : '';
        tbody.innerHTML = items.length ? items.map(it => `
            <tr>
                <td class="font-mono text-xs">${UI.esc(it.file.split('/').pop())}<div class="text-[10px] t-muted">${UI.esc(it.file.split('/').slice(0, -1).join('/'))}</div></td>
                <td><span class="badge ${tone(it.status)}">${UI.esc(String(it.status).replace(/_/g, ' '))}</span></td>
                <td class="font-mono text-[11px] t-muted">${UI.esc((it.sha256 || '').slice(0, 12))}…</td>
            </tr>`).join('') : `<tr><td colspan="3" class="text-center py-6 t-muted text-xs">No matching artifacts.</td></tr>`;
    }
});
