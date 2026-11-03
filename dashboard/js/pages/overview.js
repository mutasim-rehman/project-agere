/**
 * Overview: the research story in one screen.
 */

window.App.registerPage('overview', {
    async render(container, app) {
        const jobs = await Data.jobs16();
        const { mas, sas } = await Data.pair('primary');
        const effects = (await app.fetchJson('data/tier16_v2/paired_effects.json')) || [];
        const primaryC = effects.find(e => e.comparison === 'primary' && e.endpoint === 'case_success/correct') || {};
        const tr = await Data.transitions('primary');
        const cases = await Data.cases16();
        const tier8 = await Data.tier8Conditions();

        const masRescues = tr.wrong.correct + tr.withheld.correct;
        const sasCorrectMasWithheld = tr.correct.withheld;
        const ratio = mas.C ? sas.C / mas.C : Infinity;
        const speed = sas.secPerCase / mas.secPerCase;
        const costPerCorrect = mas.secPerCorrect / sas.secPerCorrect;
        const repair = jobs['tier16-mas-repair_ablation'];
        const repairExtraH = repair.hours - mas.hours;

        const waffle = (arm) => {
            const rows = cases.filter(c => c.job === `tier16-${arm}-primary`);
            const order = { correct: 0, wrong: 1, withheld: 2 };
            rows.sort((a, b) => order[a.reported_outcome] - order[b.reported_outcome] || a.case_id.localeCompare(b.case_id));
            return `<div class="waffle">${rows.map((r, i) =>
                `<i class="w-${r.reported_outcome}" style="--d:${i}" title="${UI.esc(r.case_id)} · ${r.reported_outcome}" onclick="App.pages.cases.openByKey('${r.job}','${UI.esc(r.case_id)}')"></i>`
            ).join('')}</div>`;
        };

        const ctrl8 = { sas: tier8.find(c => c.job === 'diagnostic_audit-control_sas-full-01'), mas: tier8.find(c => c.job === 'diagnostic_audit-control_mas-full-01') };

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Headline finding · 16 GB tier',
                title: `One quantized 14B model answers <span class="grad-text">${ratio.toFixed(1)}×</span> more questions correctly than a three-model full-precision team`,
                sub: `Same 160 FinQA questions, same memory ceiling, same token budget. The team rarely gets answers wrong, but only because it declines to answer ${UI.pct(mas.H, mas.n, 0)}% of the time.`,
                right: `
                    <div class="flex flex-col gap-2 items-start lg:items-end">
                        <span class="badge badge-correct"><i data-lucide="check-circle-2" class="w-3 h-3"></i>Holm p = ${UI.fmtP(primaryC.holm_primary4_p)}</span>
                        <span class="badge">Δ correct ${(primaryC.delta * 100).toFixed(1)} pp · 95% CI [${(primaryC.ci_low * 100).toFixed(1)}, ${(primaryC.ci_high * 100).toFixed(1)}]</span>
                        <span class="badge">50 report clusters · 36 companies</span>
                    </div>`
            })}

            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
                ${UI.kpi({ label: 'SAS correct answers', value: 100 * sas.acc, decimals: 1, suffix: '%', foot: `${sas.C} of ${sas.n} · Qwen2.5-14B Q4`, tone: 'sas', icon: 'target', i: 1 })}
                ${UI.kpi({ label: 'MAS correct answers', value: 100 * mas.acc, decimals: 1, suffix: '%', foot: `${mas.C} of ${mas.n} · 1.5B + 3B + 0.5B F16`, tone: 'mas', icon: 'users', i: 2 })}
                ${UI.kpi({ label: 'MAS declines to answer', value: 100 * mas.withheldRate, decimals: 1, suffix: '%', foot: `${mas.H} withheld vs ${sas.H} for SAS`, tone: 'withheld', icon: 'shield-off', i: 3 })}
                ${UI.kpi({ label: 'MAS precision when it answers', value: 100 * mas.precision, decimals: 1, suffix: '%', foot: `MAS ${UI.pct(mas.C, mas.C + mas.W)}% vs SAS ${UI.pct(sas.C, sas.C + sas.W)}%: a near tie`, tone: 'correct', icon: 'crosshair', i: 4 })}
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
                ${UI.card({
                    cls: 'xl:col-span-3', i: 5,
                    title: 'Every question, one square',
                    sub: 'Primary profile. Click any square to inspect that case.',
                    right: UI.outcomeLegend(),
                    body: `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <div class="flex items-baseline justify-between mb-3">
                                    <span class="text-sm font-semibold c-sas">SAS · single 14B</span>
                                    <span class="font-mono text-xs t-secondary">${sas.C} / ${sas.W} / ${sas.H}</span>
                                </div>
                                ${waffle('sas')}
                            </div>
                            <div>
                                <div class="flex items-baseline justify-between mb-3">
                                    <span class="text-sm font-semibold c-mas">MAS · 3-agent team</span>
                                    <span class="font-mono text-xs t-secondary">${mas.C} / ${mas.W} / ${mas.H}</span>
                                </div>
                                ${waffle('mas')}
                            </div>
                        </div>`
                })}

                <section class="xl:col-span-2 space-y-3">
                    <div class="eyebrow reveal" style="--i:5">What the data says</div>
                    ${UI.insight({ i: 6, tone: 'sas', icon: 'trophy', title: `SAS wins on useful answers by ${Math.abs(primaryC.delta * 100).toFixed(1)} points`, body: `The interval stays far from zero under both report- and company-level clustering, and under both scoring metrics.` })}
                    ${UI.insight({ i: 7, tone: 'warn', icon: 'scale', title: 'MAS is not more careful, just quieter', body: `When it does answer, MAS is right ${UI.pct(mas.C, mas.C + mas.W)}% of the time vs ${UI.pct(sas.C, sas.C + sas.W)}% for SAS. The gap is coverage: ${UI.pct(mas.C + mas.W, mas.n)}% vs ${UI.pct(sas.C + sas.W, sas.n)}%.` })}
                    ${UI.insight({ i: 8, tone: 'bad', icon: 'life-buoy', title: `MAS rescued ${masRescues} questions SAS missed`, body: `Of SAS's ${sas.C} correct answers, MAS withheld ${sasCorrectMasWithheld}. The team adds no complementary coverage.` })}
                    ${UI.insight({ i: 9, tone: 'mas', icon: 'timer', title: `${speed.toFixed(1)}× faster per question, ${costPerCorrect.toFixed(1)}× costlier per correct answer`, body: `MAS spends ${Math.round(mas.secPerCorrect / 60)} CPU-minutes per correct answer vs ${Math.round(sas.secPerCorrect / 60)} for SAS.` })}
                    ${UI.insight({ i: 10, tone: 'bad', icon: 'wrench', title: `${repair.repairs} repair attempts changed nothing`, body: `The repair loop added ${repairExtraH.toFixed(2)} h of MAS inference, and every final delivery state was identical to the primary profile.` })}
                </section>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
                ${UI.card({
                    i: 11,
                    title: 'Coverage vs precision',
                    sub: 'Each bubble is one 16 GB job. Bubble size is CPU inference hours. Up and to the right is better.',
                    body: `<div class="h-80"><canvas id="ov-bubble"></canvas></div>`
                })}
                ${UI.card({
                    i: 12,
                    title: 'All six 16 GB jobs at a glance',
                    sub: 'Reported-answer outcomes for 160 questions per job',
                    right: UI.outcomeLegend(),
                    body: `
                        <div class="space-y-4 mt-2">
                            ${Data.PROFILES.map(p => ['sas', 'mas'].map(arm => {
                                const j = jobs[`tier16-${arm}-${p}`];
                                return `
                                    <div>
                                        <div class="flex items-center justify-between text-xs mb-1.5">
                                            <span class="flex items-center gap-2">${UI.armBadge(arm)}<span class="t-secondary">${Data.PROFILE_LABEL[p]}</span></span>
                                            <span class="font-mono t-muted">${UI.pct(j.C, j.n)}% correct · ${j.hours.toFixed(1)} h</span>
                                        </div>
                                        ${UI.stackbar(j.C, j.W, j.H, j.n)}
                                    </div>`;
                            }).join('')).join('')}
                        </div>`
                })}
            </div>

            ${UI.card({
                i: 13,
                title: 'Does the gap hold at 8 GB?',
                sub: 'Correct-answer rate by tier. Different questions, adaptation and backends per tier, so this is descriptive, not a RAM-scaling law.',
                body: `
                    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
                        <div class="lg:col-span-2 h-64"><canvas id="ov-tier"></canvas></div>
                        <div class="space-y-3">
                            ${UI.insight({ tone: 'sas', icon: 'trending-up', title: 'SAS leads in both tiers', body: `8 GB reserved control: SAS ${ctrl8.sas.reported.C}/${ctrl8.sas.n} vs MAS ${ctrl8.mas.reported.C}/${ctrl8.mas.n}. At 16 GB the gap widens to ${sas.C} vs ${mas.C}.` })}
                            ${UI.insight({ tone: 'warn', icon: 'alert-circle', title: 'Not a causal RAM effect', body: 'Recipes, question sources and adaptation differ between tiers.' })}
                        </div>
                    </div>`
            })}
        `;

        this.renderCharts(jobs, sas, mas, ctrl8);
    },

    renderCharts(jobs, sas, mas, ctrl8) {
        const k = UI.colors();
        const pts = Object.values(jobs).map(j => ({
            x: 100 * j.coverage, y: j.precision == null ? 0 : 100 * j.precision, r: 6 + 2.2 * Math.sqrt(j.hours * 4),
            label: `${j.arm.toUpperCase()} · ${Data.PROFILE_LABEL[j.profile]}`, j
        }));
        UI.chart('ov-bubble', {
            type: 'bubble',
            data: {
                datasets: ['sas', 'mas'].map(arm => ({
                    label: arm === 'sas' ? 'SAS (14B Q4)' : 'MAS (3-agent F16)',
                    data: pts.filter(p => p.j.arm === arm),
                    backgroundColor: UI.alpha(arm, 0.35), borderColor: k[arm], borderWidth: 2, hoverBorderWidth: 3
                }))
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { duration: 1400, easing: 'easeOutElastic', delay: ctx => ctx.dataIndex * 120 },
                plugins: {
                    legend: { position: 'top', align: 'end' },
                    tooltip: { callbacks: { label: ctx => {
                        const j = ctx.raw.j;
                        return [`${ctx.raw.label}`, `Coverage ${(100 * j.coverage).toFixed(1)}% · Precision ${j.precision == null ? '—' : (100 * j.precision).toFixed(1) + '%'}`, `${j.C} correct / ${j.W} wrong / ${j.H} withheld · ${j.hours.toFixed(1)} h`];
                    } } }
                },
                scales: {
                    x: { min: -5, max: 100, title: { display: true, text: 'Coverage: share of questions answered (%)' }, grid: { color: k.grid } },
                    y: { min: -5, max: 100, title: { display: true, text: 'Precision: correct when answered (%)' }, grid: { color: k.grid } }
                }
            }
        });

        UI.chart('ov-tier', {
            type: 'bar',
            data: {
                labels: ['8 GB · reserved control (n=49)', '16 GB · primary (n=160)'],
                datasets: [
                    { label: 'SAS', data: [100 * ctrl8.sas.reported.C / ctrl8.sas.n, 100 * sas.acc], backgroundColor: UI.alpha('sas', 0.85), borderRadius: 8, barPercentage: 0.7, categoryPercentage: 0.6 },
                    { label: 'MAS', data: [100 * ctrl8.mas.reported.C / ctrl8.mas.n, 100 * mas.acc], backgroundColor: UI.alpha('mas', 0.85), borderRadius: 8, barPercentage: 0.7, categoryPercentage: 0.6 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { delay: ctx => ctx.type === 'data' ? ctx.dataIndex * 200 + ctx.datasetIndex * 120 : 0 },
                plugins: { legend: { position: 'top', align: 'end' }, tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}% correct` } } },
                scales: { x: { grid: { display: false } }, y: { beginAtZero: true, suggestedMax: 60, ticks: { callback: v => v + '%' } } }
            }
        });
    }
});
