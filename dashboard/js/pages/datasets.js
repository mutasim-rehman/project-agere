/**
 * Companies & Data: per-company outcomes, retrieval strata and dataset inventory.
 */

window.App.registerPage('datasets', {
    async render(container, app) {
        const companies = await Data.companies('primary');
        const cases = await Data.cases16();
        const manifests = (await app.fetchJson('data/manifests_summary.json')) || {};
        this.companies = companies;

        const sasWins = companies.filter(c => c.sas.C > c.mas.C).length;
        const masWins = companies.filter(c => c.mas.C > c.sas.C).length;
        const ties = companies.length - sasWins - masWins;
        const masZero = companies.filter(c => c.mas.C === 0).length;
        const best = [...companies].filter(c => c.n >= 4).sort((a, b) => b.sas.acc - a.sas.acc)[0];
        const hardest = [...companies].filter(c => c.n >= 4).sort((a, b) => a.sas.acc - b.sas.acc)[0];

        const strata = complete => {
            const rows = cases.filter(c => c.profile === 'primary' && c.annotated_evidence_complete === complete);
            return { sas: Data.summarize(rows.filter(r => r.arm === 'sas')), mas: Data.summarize(rows.filter(r => r.arm === 'mas')) };
        };
        const full = strata(true), partial = strata(false);

        const dl = (manifests.downloaded_datasets || {}).datasets || [];
        const synth = (manifests.synthetic_datasets || {}).files || [];

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'By company · primary profile',
                title: `SAS wins at <span class="grad-text">${sasWins} of ${companies.length}</span> companies. MAS wins at ${masWins}.`,
                sub: `MAS gets zero correct answers at ${masZero} companies. The SAS advantage is broad, not driven by a few large reports.`
            })}

            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
                ${UI.kpi({ label: 'Companies', value: companies.length, foot: `${companies.reduce((a, c) => a + c.reports, 0)} company-year 10-K reports`, icon: 'building-2', i: 1 })}
                ${UI.kpi({ label: 'Ties', value: ties, foot: 'Equal correct count for both arms', tone: 'withheld', icon: 'equal', i: 2 })}
                ${UI.kpi({ label: `Best for SAS · ${best?.company}`, value: 100 * (best?.sas.acc || 0), decimals: 0, suffix: '%', foot: `${best?.sas.C}/${best?.n} correct (MAS ${best?.mas.C})`, tone: 'sas', icon: 'award', i: 3 })}
                ${UI.kpi({ label: `Hardest · ${hardest?.company}`, value: 100 * (hardest?.sas.acc || 0), decimals: 0, suffix: '%', foot: `SAS ${hardest?.sas.C}/${hardest?.n} correct`, tone: 'wrong', icon: 'mountain', i: 4 })}
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-3 gap-6">
                ${UI.card({
                    cls: 'xl:col-span-2', i: 5,
                    title: 'Correct-answer rate by company',
                    sub: 'Dumbbells connect each arm\'s rate. Longer bars mean a bigger SAS advantage. Hover for counts.',
                    right: `<div class="legend"><span><i class="sw" style="background:var(--color-sas)"></i>SAS</span><span><i class="sw" style="background:var(--color-mas)"></i>MAS</span></div>`,
                    body: `<div id="ds-dumbbell" class="w-full" style="height:${Math.max(420, companies.length * 19 + 60)}px"></div>`
                })}
                <div class="space-y-6">
                    ${UI.card({
                        i: 6,
                        title: 'Does retrieval explain the gap?',
                        sub: 'Split by whether all gold evidence reached the model',
                        body: `
                            ${[['All gold evidence retrieved', full], ['Evidence incomplete', partial]].map(([label, s]) => `
                                <div class="mb-5">
                                    <div class="flex justify-between text-xs mb-2"><span class="font-semibold">${label}</span><span class="font-mono t-muted">${s.sas.n} questions</span></div>
                                    <div class="space-y-1.5">
                                        <div class="flex items-center gap-2"><span class="w-9 text-[11px] c-sas font-semibold">SAS</span><div class="flex-1">${UI.stackbar(s.sas.C, s.sas.W, s.sas.H, s.sas.n)}</div></div>
                                        <div class="flex items-center gap-2"><span class="w-9 text-[11px] c-mas font-semibold">MAS</span><div class="flex-1">${UI.stackbar(s.mas.C, s.mas.W, s.mas.H, s.mas.n)}</div></div>
                                    </div>
                                </div>`).join('')}
                            ${UI.insight({ tone: 'bad', icon: 'search-x', title: 'No. MAS fails even with perfect evidence', body: `With all gold evidence present, SAS answers ${full.sas.C} correctly and MAS ${full.mas.C}.` })}`
                    })}
                    ${UI.card({
                        i: 7,
                        title: 'Datasets on the SSD',
                        sub: 'From the pinned download and synthetic manifests',
                        body: `
                            <div class="space-y-2">
                                <div class="flex items-center justify-between p-3 rounded-lg" style="background:var(--bg-surface-elevated)">
                                    <div><div class="text-sm font-semibold">FinQA</div><div class="text-[11px] t-muted">Primary benchmark · SEC 10-K numerical QA</div></div>
                                    <span class="badge badge-sas">261 questions</span>
                                </div>
                                ${dl.map(d => `
                                    <div class="flex items-center justify-between p-3 rounded-lg" style="background:var(--bg-surface-elevated)">
                                        <div class="min-w-0"><div class="text-sm font-semibold truncate">${UI.esc(d.repo || d.id)}</div><div class="text-[11px] t-muted">${UI.esc(d.license || '')} · rev ${UI.esc((d.revision || '').slice(0, 7))}</div></div>
                                        <span class="badge">${(d.files || []).length} files</span>
                                    </div>`).join('')}
                            </div>
                            <div class="text-[11px] t-muted mt-4 mb-2">Synthetic · agere-synth-v1</div>
                            <div class="flex flex-wrap gap-1.5">
                                ${synth.map(f => `<span class="badge badge-mas">${UI.esc(f.dataset)} · ${UI.num(f.rows)}</span>`).join('')}
                            </div>`
                    })}
                </div>
            </div>

            ${UI.disclosure({
                i: 8,
                title: 'Per-company table',
                meta: `${companies.length} companies`,
                body: `
                    <div class="table-container max-h-96">
                        <table class="data-table">
                            <thead><tr><th>Company</th><th class="text-right">Reports</th><th class="text-right">Questions</th><th>SAS C / W / H</th><th>MAS C / W / H</th><th class="text-right">Gap (pp)</th></tr></thead>
                            <tbody>
                                ${companies.map(c => `
                                    <tr>
                                        <td class="font-mono text-xs font-semibold">${c.company}</td>
                                        <td class="font-mono text-xs text-right t-secondary">${c.reports}</td>
                                        <td class="font-mono text-xs text-right">${c.n}</td>
                                        <td class="font-mono text-xs"><span class="c-correct">${c.sas.C}</span> / <span class="c-wrong">${c.sas.W}</span> / <span class="c-withheld">${c.sas.H}</span></td>
                                        <td class="font-mono text-xs"><span class="c-correct">${c.mas.C}</span> / <span class="c-wrong">${c.mas.W}</span> / <span class="c-withheld">${c.mas.H}</span></td>
                                        <td class="font-mono text-xs text-right font-semibold ${c.gap > 0 ? 'c-sas' : c.gap < 0 ? 'c-mas' : 't-muted'}">${(100 * c.gap).toFixed(0)}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>`
            })}
        `;

        this.renderDumbbell();
    },

    renderDumbbell() {
        const el = document.getElementById('ds-dumbbell');
        if (!el || !window.Plotly) return;
        const k = UI.colors();
        const rows = [...this.companies].sort((a, b) => a.sas.acc - b.sas.acc || a.gap - b.gap);
        const y = rows.map(c => `${c.company} (${c.n})`);
        const sasX = rows.map(c => 100 * c.sas.acc);
        const masX = rows.map(c => 100 * c.mas.acc);
        const lineX = [], lineY = [];
        rows.forEach((c, i) => { lineX.push(masX[i], sasX[i], null); lineY.push(y[i], y[i], null); });

        const traces = [
            { type: 'scatter', mode: 'lines', x: lineX.map(v => v === null ? null : 0), y: lineY, line: { color: UI.alpha('sas', 0.35), width: 5 }, hoverinfo: 'skip', showlegend: false },
            { type: 'scatter', mode: 'markers', name: 'MAS', x: masX.map(() => 0), y, marker: { color: k.mas, size: 10, line: { color: k.surface, width: 1.5 } },
              hovertemplate: rows.map(c => `<b>${c.company}</b><br>MAS ${c.mas.C}/${c.n} correct · ${c.mas.H} withheld<extra></extra>`) },
            { type: 'scatter', mode: 'markers', name: 'SAS', x: sasX.map(() => 0), y, marker: { color: k.sas, size: 12, line: { color: k.surface, width: 1.5 } },
              hovertemplate: rows.map(c => `<b>${c.company}</b><br>SAS ${c.sas.C}/${c.n} correct · ${c.sas.W} wrong<extra></extra>`) }
        ];
        const layout = UI.plotLayout({
            margin: { l: 80, r: 20, t: 10, b: 40 }, showlegend: false,
            xaxis: { title: { text: 'Correct answers (%)' }, range: [-4, 104], ticksuffix: '%' },
            yaxis: { tickfont: { color: k.text, size: 10, family: 'JetBrains Mono' }, gridcolor: k.grid }
        });
        Plotly.newPlot(el, traces, layout, UI.plotConfig).then(() => {
            Plotly.animate(el, { data: [{ x: lineX }, { x: masX }, { x: sasX }], traces: [0, 1, 2] },
                { transition: { duration: 1100, easing: 'cubic-out' }, frame: { duration: 1100, redraw: false } });
        });
    }
});
