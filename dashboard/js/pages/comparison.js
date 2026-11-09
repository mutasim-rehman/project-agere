/**
 * MAS vs SAS head-to-head.
 */

window.App.registerPage('comparison', {
    state: { profile: 'primary', metric: 'reported', endpoint: 'correct' },

    async render(container, app) {
        this.effects = (await app.fetchJson('data/tier16_v2/paired_effects.json')) || [];
        this.disagreements = (await app.fetchJson('data/tier16_v2/metric_disagreements.json')) || [];

        const seg = (group, options, active) => `
            <div class="seg" data-group="${group}">
                ${options.map(([v, l]) => `<button data-v="${v}" class="${v === active ? 'on' : ''}">${l}</button>`).join('')}
            </div>`;

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Head-to-head',
                title: 'Same questions, same RAM, very different behaviour',
                sub: 'Pick a profile and scoring metric. Every panel below recomputes from the 960 case outcomes.',
                right: `
                    <div class="flex flex-col gap-2 items-start lg:items-end">
                        ${seg('profile', [['primary', 'Primary'], ['direct_control', 'Direct control'], ['repair_ablation', 'Repair ablation']], this.state.profile)}
                        ${seg('metric', [['reported', 'Reported answer'], ['raw', 'Raw execution']], this.state.metric)}
                    </div>`
            })}

            <div id="cmp-insights" class="grid grid-cols-1 md:grid-cols-3 gap-4"></div>

            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
                ${UI.card({
                    cls: 'xl:col-span-3', i: 2,
                    title: 'Scoreboard',
                    sub: 'Bars scale to the larger of the two arms. The green dot marks the better arm on each row.',
                    right: `<div class="legend"><span><i class="sw" style="background:var(--color-sas)"></i>SAS</span><span><i class="sw" style="background:var(--color-mas)"></i>MAS</span></div>`,
                    body: `<div id="cmp-vs"></div>`
                })}
                ${UI.card({
                    cls: 'xl:col-span-2', i: 3,
                    title: 'Where each question ends up',
                    sub: 'Rows: SAS outcome. Columns: MAS outcome on the same question.',
                    body: `<div id="cmp-heat"></div>`
                })}
            </div>

            ${UI.card({
                i: 4,
                title: 'Effect sizes across every paired contrast',
                sub: 'Δ = right minus left arm in percentage points, with 95% report-cluster bootstrap intervals. Filled markers have cluster sign-flip p < 0.05.',
                right: seg('endpoint', [['correct', 'Correct'], ['wrong', 'Wrong'], ['withheld', 'Withheld']], this.state.endpoint),
                body: `<div id="cmp-forest" class="w-full h-80"></div>`
            })}

            ${UI.disclosure({
                i: 5,
                title: `Metric disagreements (${this.disagreements.length} cases)`,
                meta: 'Reported and raw-execution scoring disagree',
                body: `
                    <p class="text-xs t-secondary mb-3">Example: a model outputs 26.6667 with unit "number". That matches the rounded gold answer 26.7 but not the raw execution value 0.26667. These are numerical-convention differences, not necessarily model errors.</p>
                    <div class="table-container max-h-96">
                        <table class="data-table">
                            <thead><tr><th>Case</th><th>Reported</th><th>Raw exec</th><th>Model output</th><th>Unit</th><th>Gold answer</th><th>Gold exec</th></tr></thead>
                            <tbody>
                                ${this.disagreements.map(m => `
                                    <tr>
                                        <td class="font-mono text-xs">${UI.esc(m.case_id)}</td>
                                        <td>${m.reported_correct ? '<span class="badge badge-correct">correct</span>' : '<span class="badge badge-wrong">wrong</span>'}</td>
                                        <td>${m.raw_correct ? '<span class="badge badge-correct">correct</span>' : '<span class="badge badge-wrong">wrong</span>'}</td>
                                        <td class="font-mono text-xs">${UI.esc(m.predicted ?? '—')}</td>
                                        <td class="font-mono text-xs t-muted">${UI.esc(m.declared_unit ?? '—')}</td>
                                        <td class="font-mono text-xs">${UI.esc(m.gold_answer ?? '—')}</td>
                                        <td class="font-mono text-xs t-secondary">${UI.esc(m.gold_exe_ans ?? '—')}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>`
            })}
        `;

        container.querySelectorAll('.seg').forEach(g => {
            g.addEventListener('click', e => {
                const b = e.target.closest('button');
                if (!b) return;
                g.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
                this.state[g.dataset.group] = b.dataset.v;
                if (g.dataset.group === 'endpoint') this.renderForest();
                else this.update();
            });
        });

        await this.update();
    },

    async update() {
        const { profile, metric } = this.state;
        const { mas, sas } = await Data.pair(profile);
        const raw = metric === 'raw';
        const pick = s => raw ? { C: s.rawC, W: s.rawW, H: s.rawH } : { C: s.C, W: s.W, H: s.H };
        const m = pick(mas), s = pick(sas);
        const n = mas.n;
        const prec = x => (x.C + x.W) ? x.C / (x.C + x.W) : 0;

        const rows = [
            { label: 'Correct answers', s: s.C, m: m.C, fmt: v => `${v} · ${UI.pct(v, n)}%`, better: 'high' },
            { label: 'Wrong answers', s: s.W, m: m.W, fmt: v => `${v} · ${UI.pct(v, n)}%`, better: 'low' },
            { label: 'Withheld', s: s.H, m: m.H, fmt: v => `${v} · ${UI.pct(v, n)}%`, better: null },
            { label: 'Precision when answering', s: 100 * prec(s), m: 100 * prec(m), fmt: v => `${v.toFixed(1)}%`, better: 'high' },
            { label: 'CPU seconds / question', s: sas.secPerCase, m: mas.secPerCase, fmt: v => `${v.toFixed(0)} s`, better: 'low' },
            { label: 'CPU seconds / correct', s: s.C ? sas.secs / s.C : 0, m: m.C ? mas.secs / m.C : 0, fmt: v => v ? `${UI.num(v)} s` : 'n/a', better: 'low', nullIsWorse: true },
            { label: 'Generated tokens / question', s: sas.genPerCase, m: mas.genPerCase, fmt: v => v.toFixed(0), better: 'low' },
            { label: 'Peak RSS (GB)', s: sas.peakGb, m: mas.peakGb, fmt: v => `${v.toFixed(2)} GB`, better: 'low' }
        ];

        document.getElementById('cmp-vs').innerHTML = rows.map(r => {
            const max = Math.max(r.s, r.m) || 1;
            let win = null;
            if (r.better && r.s !== r.m) {
                if (r.nullIsWorse && (!r.s || !r.m)) win = r.s ? 's' : 'm';
                else win = (r.better === 'high' ? r.s > r.m : r.s < r.m) ? 's' : 'm';
            }
            return `
                <div class="vs-row">
                    <div class="text-right">
                        <div class="vs-val c-sas">${win === 's' ? '<span class="winner-dot"></span>' : ''}${r.fmt(r.s)}</div>
                        <div class="vs-bar left"><div data-w="${100 * r.s / max}" style="background:var(--color-sas)"></div></div>
                    </div>
                    <div class="vs-label">${r.label}</div>
                    <div>
                        <div class="vs-val c-mas">${r.fmt(r.m)}${win === 'm' ? '<span class="winner-dot"></span>' : ''}</div>
                        <div class="vs-bar"><div data-w="${100 * r.m / max}" style="background:var(--color-mas)"></div></div>
                    </div>
                </div>`;
        }).join('');

        const tr = await Data.transitions(profile, metric);
        const states = ['correct', 'wrong', 'withheld'];
        const total = states.reduce((a, r) => a + states.reduce((b, c) => b + tr[r][c], 0), 0);
        const maxCell = Math.max(...states.flatMap(r => states.map(c => tr[r][c])));
        const cellColor = (r, c) => r === c ? 'accent' : (c === 'correct' ? 'correct' : (r === 'correct' ? 'wrong' : 'withheld'));
        document.getElementById('cmp-heat').innerHTML = `
            <div class="heat-grid" style="grid-template-columns: 74px repeat(3, 1fr)">
                <div></div>
                ${states.map(c => `<div class="text-[11px] text-center c-mas font-semibold pb-1">MAS ${c}</div>`).join('')}
                ${states.map((r, ri) => `
                    <div class="text-[11px] c-sas font-semibold flex items-center">SAS ${r}</div>
                    ${states.map((c, ci) => {
                        const v = tr[r][c];
                        const a = 0.08 + 0.75 * (v / (maxCell || 1));
                        const tone = cellColor(r, c);
                        const bg = tone === 'accent' ? `rgba(129,140,248,${a})` : UI.alpha(tone, a);
                        return `<div class="heat-cell" style="background:${bg}; animation-delay:${(ri * 3 + ci) * 60}ms" title="SAS ${r} → MAS ${c}: ${v} questions">
                            ${v}<small>${UI.pct(v, total, 0)}%</small></div>`;
                    }).join('')}`).join('')}
            </div>
            <p class="text-xs t-secondary mt-4 leading-relaxed">
                <span class="font-semibold c-correct">${tr.wrong.correct + tr.withheld.correct}</span> questions where only MAS was right,
                <span class="font-semibold c-wrong">${tr.correct.wrong + tr.correct.withheld}</span> where only SAS was right.
            </p>`;

        const masOnly = tr.wrong.correct + tr.withheld.correct;
        const sasOnly = tr.correct.wrong + tr.correct.withheld;
        const metricName = raw ? 'raw execution' : 'reported answer';
        document.getElementById('cmp-insights').innerHTML = [
            UI.insight({ i: 1, tone: 'sas', icon: 'trophy', title: `SAS: ${s.C} correct vs MAS: ${m.C}`, body: `${Data.PROFILE_LABEL[profile]} profile, ${metricName} scoring. That is a ${UI.pct(s.C - m.C, n)}-point gap on the same ${n} questions.` }),
            UI.insight({ i: 1, tone: 'warn', icon: 'shield-off', title: `MAS withholds ${UI.pct(m.H, n, 0)}% of questions`, body: `Fewer wrong answers (${m.W} vs ${s.W}) come from answering less, not from answering better.` }),
            UI.insight({ i: 1, tone: masOnly ? 'good' : 'bad', icon: 'git-compare', title: `${masOnly} MAS-only wins vs ${sasOnly} SAS-only wins`, body: masOnly ? 'MAS adds some complementary coverage on this profile.' : 'MAS never solves a question that SAS missed, so routing between the two would not help.' })
        ].join('');

        if (window.lucide) lucide.createIcons();
        UI.animateIn(document.getElementById('content-container'));
        this.renderForest();
    },

    renderForest() {
        const el = document.getElementById('cmp-forest');
        if (!el || !window.Plotly) return;
        const k = UI.colors();
        const metricKey = this.state.metric === 'raw' ? 'raw_execution_match' : 'case_success';
        const endpoint = `${metricKey}/${this.state.endpoint}`;
        const names = {
            'primary': 'MAS − SAS · primary', 'direct_control': 'MAS − SAS · direct control', 'repair_ablation': 'MAS − SAS · repair ablation',
            'sas-reasoned_vs_direct': 'SAS · reasoned − direct', 'mas-reasoned_vs_direct': 'MAS · reasoned − direct',
            'sas-repair_vs_primary': 'SAS · repair − primary', 'mas-repair_vs_primary': 'MAS · repair − primary'
        };
        const rows = this.effects.filter(e => e.endpoint === endpoint);
        const y = rows.map(r => names[r.comparison] || r.comparison);
        const x = rows.map(r => 100 * r.delta);
        const sig = rows.map(r => r.cluster_signflip_p < 0.05);
        const color = rows.map((r, i) => r.comparison.startsWith('mas-') || r.comparison.startsWith('sas-') ? k[r.comparison.slice(0, 3)] : (x[i] < 0 ? k.wrong : k.correct));

        const trace = {
            type: 'scatter', mode: 'markers', y,
            x: x.map(() => 0),
            error_x: { type: 'data', symmetric: false, array: rows.map(() => 0), arrayminus: rows.map(() => 0), color: k.muted, thickness: 2, width: 6 },
            marker: { size: 13, color: color.map((c, i) => sig[i] ? c : 'rgba(0,0,0,0)'), line: { color, width: 2.5 }, symbol: 'diamond' },
            hovertemplate: rows.map(r => `<b>${names[r.comparison] || r.comparison}</b><br>Δ ${(100 * r.delta).toFixed(1)} pp<br>95% CI [${(100 * r.ci_low).toFixed(1)}, ${(100 * r.ci_high).toFixed(1)}]<br>sign-flip p = ${UI.fmtP(r.cluster_signflip_p)}<extra></extra>`)
        };
        const layout = UI.plotLayout({
            margin: { l: 200, r: 30, t: 10, b: 45 },
            showlegend: false,
            xaxis: { title: { text: 'Δ percentage points' }, range: [-100, 100], zeroline: true, zerolinewidth: 2, ticksuffix: '' },
            yaxis: { autorange: 'reversed', tickfont: { color: k.text, size: 11, family: 'Inter' }, gridcolor: k.grid },
            shapes: [{ type: 'rect', xref: 'x', yref: 'paper', x0: -2, x1: 2, y0: 0, y1: 1, fillcolor: k.grid, line: { width: 0 } }]
        });
        Plotly.newPlot(el, [trace], layout, UI.plotConfig).then(() => {
            Plotly.animate(el, {
                data: [{ x, error_x: { type: 'data', symmetric: false, array: rows.map(r => 100 * (r.ci_high - r.delta)), arrayminus: rows.map(r => 100 * (r.delta - r.ci_low)), color: k.muted, thickness: 2, width: 6 } }],
                traces: [0]
            }, { transition: { duration: 900, easing: 'cubic-out' }, frame: { duration: 900, redraw: false } });
        });
    }
});
