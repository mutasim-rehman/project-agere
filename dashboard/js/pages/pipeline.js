/**
 * Pipeline & Cost: where MAS loses answers, and where both arms spend compute.
 */

window.App.registerPage('pipeline', {
    STAGE_LABEL: {
        select_evidence: 'Select evidence', analyze_question: 'Analyze', program: 'Write program',
        verify_program: 'Verify', repair_program_full: 'Repair', verify_program_repair: 'Re-verify'
    },
    STAGE_COLOR: {
        select_evidence: '#60a5fa', analyze_question: '#a78bfa', program: '#f472b6',
        verify_program: '#34d399', repair_program_full: '#fbbf24', verify_program_repair: '#fb923c'
    },

    async render(container, app) {
        const stages = (await app.fetchJson('data/tier16_v2/stage_metrics.json')) || [];
        const jobs = await Data.jobs16();
        const { mas, sas } = await Data.pair('primary');
        this.stages = stages;

        const st = (job, stage) => stages.find(s => s.job === job && s.stage === stage) || { calls: 0, generated_tokens: 0, inference_seconds: 0, prompt_tokens: 0 };
        const mp = s => st('tier16-mas-primary', s);
        const node = ({ step, title, model, badgeCls = 'badge-mas', desc, stats }) => `
            <div class="flow-node">
                <div class="flex items-center justify-between gap-2">
                    <span class="text-[10px] font-mono t-muted uppercase tracking-wider">${step}</span>
                    <span class="badge ${badgeCls}">${model}</span>
                </div>
                <div class="font-semibold text-sm mt-2">${title}</div>
                <p class="text-xs t-secondary mt-1 leading-relaxed">${desc}</p>
                <div class="mt-3 pt-3 border-t border-[var(--border-color)] space-y-1 text-[11px] font-mono">
                    ${stats.map(([k, v, cls = '']) => `<div class="flex justify-between gap-3"><span class="t-muted">${k}</span><span class="${cls}">${v}</span></div>`).join('')}
                </div>
            </div>`;
        const avg = s => `${(s.inference_seconds / Math.max(1, s.calls)).toFixed(1)} s`;
        const tokAvg = s => `${(s.generated_tokens / Math.max(1, s.calls)).toFixed(0)} tok`;

        const repair = jobs['tier16-mas-repair_ablation'];
        const sasRepair = jobs['tier16-sas-repair_ablation'];

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Pipeline diagnosis',
                title: `The team breaks at drafting: only <span class="grad-text">${mas.exec} of ${mas.n}</span> MAS programs were executable`,
                sub: `SAS produced ${sas.exec} executable programs from the same questions. MAS's review gate is not the bottleneck: it delivered all ${mas.initC} of its correct candidates.`
            })}

            ${UI.card({
                i: 1,
                title: 'MAS execution flow',
                sub: 'Primary profile. Per-call averages over 160 questions.',
                body: `
                    <div class="flow">
                        ${node({ step: 'Stage 1', title: 'Extractor', model: '1.5B F16', desc: 'Picks the evidence spans and table rows to use.', stats: [['avg time', avg(mp('select_evidence'))], ['avg output', tokAvg(mp('select_evidence'))]] })}
                        <div class="flow-link"></div>
                        ${node({ step: 'Stage 2', title: 'Drafter', model: '3B F16', desc: 'Analyzes the question, then writes an arithmetic program.', stats: [['analyze', avg(mp('analyze_question'))], ['program', avg(mp('program'))], ['executable', `${mas.exec} / ${mas.n}`, 'c-wrong font-semibold']] })}
                        <div class="flow-link"></div>
                        ${node({ step: 'Stage 3', title: 'Verifier', model: '0.5B F16', desc: 'Checks units, span grounding and sanity.', stats: [['avg time', avg(mp('verify_program'))], ['avg output', tokAvg(mp('verify_program'))]] })}
                        <div class="flow-link"></div>
                        ${node({ step: 'Gate', title: 'Deliver or withhold', model: 'policy', badgeCls: 'badge-withheld', desc: 'Releases the answer only when checks pass.', stats: [['delivered', `${mas.C + mas.W} / ${mas.n}`], ['withheld', `${UI.pct(mas.H, mas.n)}%`, 'c-withheld font-semibold']] })}
                    </div>`
            })}

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
                ${UI.card({
                    i: 2,
                    title: 'Candidate funnel',
                    sub: 'How many of 160 questions survive each step',
                    right: `<div class="legend"><span><i class="sw" style="background:var(--color-sas)"></i>SAS</span><span><i class="sw" style="background:var(--color-mas)"></i>MAS</span></div>`,
                    body: `
                        <div class="pr-16">
                            ${[['Questions', sas.n, mas.n], ['Executable program', sas.exec, mas.exec], ['Correct candidate', sas.initC, mas.initC], ['Delivered correct', sas.C, mas.C]].map(([label, s, m]) => `
                                <div class="funnel-row">
                                    <div class="text-xs t-secondary text-right">${label}</div>
                                    <div class="funnel-track">
                                        <div class="funnel-bar" data-w="${100 * s / 160}" style="background:linear-gradient(90deg, ${UI.alpha('sas', 0.5)}, var(--color-sas))"><span>${s}</span></div>
                                        <div class="funnel-bar" data-w="${100 * m / 160}" style="background:linear-gradient(90deg, ${UI.alpha('mas', 0.5)}, var(--color-mas)); min-width:3px"><span>${m}</span></div>
                                    </div>
                                </div>`).join('')}
                        </div>
                        <div class="mt-4">${UI.insight({ tone: 'bad', icon: 'filter-x', title: `${mas.n - mas.exec} of ${mas.n} MAS questions were lost before review`, body: `A better gate cannot fix this. Any accept/reject rule on these candidates is capped at ${mas.initC} correct answers.` })}</div>`
                })}
                ${UI.card({
                    i: 3,
                    title: 'Where the CPU time goes',
                    sub: 'Total inference hours per job, split by stage',
                    body: `<div class="h-80"><canvas id="pipe-time"></canvas></div>`
                })}
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                ${UI.insight({ i: 4, tone: 'mas', icon: 'zap', title: `SAS program writing is the single biggest cost`, body: `${(st('tier16-sas-primary', 'program').inference_seconds / 3600).toFixed(1)} h of the ${sas.hours.toFixed(1)} h primary run, about ${(st('tier16-sas-primary', 'program').inference_seconds / 160).toFixed(0)} s per question on a 14B model.` })}
                ${UI.insight({ i: 5, tone: 'warn', icon: 'wrench', title: `Repair costs ${(repair.hours - mas.hours).toFixed(2)} h for zero MAS gain`, body: `${repair.repairs} MAS repairs, identical final outcomes. SAS repair adds ${(sasRepair.hours - sas.hours).toFixed(2)} h for +${sasRepair.C - sas.C} correct and +${sasRepair.W - sas.W} wrong.` })}
                ${UI.insight({ i: 6, tone: 'sas', icon: 'gauge', title: `MAS: ${mas.secPerCase.toFixed(0)} s per question, ${UI.num(mas.secPerCorrect)} s per correct answer`, body: `SAS: ${sas.secPerCase.toFixed(0)} s per question and ${UI.num(sas.secPerCorrect)} s per correct answer. Speed per question doesn't translate into useful output.` })}
            </div>

            ${UI.card({
                i: 7,
                title: 'Generated tokens per stage',
                sub: 'Analysis stages hit their 128-token allowance on nearly every case',
                body: `<div class="h-72"><canvas id="pipe-tokens"></canvas></div>`
            })}

            ${UI.disclosure({
                i: 8,
                title: 'Stage-by-stage telemetry',
                meta: `${stages.length} stage records`,
                body: `
                    <div class="table-container max-h-[420px]">
                        <table class="data-table">
                            <thead><tr><th>Job</th><th>Role</th><th>Stage</th><th class="text-right">Calls</th><th class="text-right">Prompt tok</th><th class="text-right">Gen tok</th><th class="text-right">Seconds</th><th class="text-right">Gen / call</th><th class="text-right">Skips</th></tr></thead>
                            <tbody>
                                ${stages.map(s => `
                                    <tr>
                                        <td class="font-mono text-xs">${s.job.replace('tier16-', '')}</td>
                                        <td><span class="badge ${s.role === 'sas' ? 'badge-sas' : 'badge-mas'}">${s.role}</span></td>
                                        <td class="text-xs"><span class="inline-block w-2 h-2 rounded-full mr-1.5" style="background:${this.STAGE_COLOR[s.stage]}"></span>${this.STAGE_LABEL[s.stage] || s.stage}</td>
                                        <td class="font-mono text-xs text-right">${s.calls}</td>
                                        <td class="font-mono text-xs text-right t-secondary">${UI.num(s.prompt_tokens)}</td>
                                        <td class="font-mono text-xs text-right">${UI.num(s.generated_tokens)}</td>
                                        <td class="font-mono text-xs text-right t-secondary">${UI.num(s.inference_seconds, 0)}</td>
                                        <td class="font-mono text-xs text-right t-muted">${(s.generated_tokens / Math.max(s.calls, 1)).toFixed(1)}</td>
                                        <td class="font-mono text-xs text-right ${s.context_or_budget_skips ? 'c-wrong' : 't-muted'}">${s.context_or_budget_skips}</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>`
            })}
        `;

        this.renderCharts();
    },

    renderCharts() {
        const stages = this.stages;
        const jobOrder = Data.PROFILES.flatMap(p => [`tier16-sas-${p}`, `tier16-mas-${p}`]);
        const labels = jobOrder.map(j => `${j.includes('-sas-') ? 'SAS' : 'MAS'} · ${Data.PROFILE_LABEL[j.split('-').slice(2).join('-')]}`);
        const stageKeys = Object.keys(this.STAGE_LABEL);
        const series = (field, scale) => stageKeys.map(sk => ({
            label: this.STAGE_LABEL[sk],
            data: jobOrder.map(j => { const s = stages.find(x => x.job === j && x.stage === sk); return s ? s[field] / scale : 0; }),
            backgroundColor: this.STAGE_COLOR[sk], borderRadius: 4, borderSkipped: false, barPercentage: 0.7
        }));

        const opts = (unit, digits) => ({
            indexAxis: 'y', responsive: true, maintainAspectRatio: false,
            animation: { delay: ctx => ctx.type === 'data' ? ctx.datasetIndex * 140 + ctx.dataIndex * 40 : 0 },
            plugins: {
                legend: { position: 'top', align: 'start' },
                tooltip: { mode: 'index', intersect: false, filter: i => i.parsed.x > 0, callbacks: { label: c => `${c.dataset.label}: ${c.parsed.x.toFixed(digits)} ${unit}` } }
            },
            scales: { x: { stacked: true, title: { display: true, text: unit } }, y: { stacked: true, grid: { display: false } } }
        });

        UI.chart('pipe-time', { type: 'bar', data: { labels, datasets: series('inference_seconds', 3600) }, options: opts('hours', 2) });
        UI.chart('pipe-tokens', { type: 'bar', data: { labels, datasets: series('generated_tokens', 1) }, options: opts('tokens', 0) });
    }
});
