/**
 * Models & Tiers: which Qwen2.5 model plays which role, and how each tier spends its memory budget.
 */

window.App.registerPage('models', {
    ROLES: {
        '0.5B': [['mas', '16 GB MAS verifier · F16'], ['muted', 'Historical 8 GB MAS roles']],
        '1.5B': [['mas', '16 GB MAS extractor · F16']],
        '3B': [['mas', '16 GB MAS drafter · F16'], ['mas', '8 GB shared MAS backbone · Q4']],
        '7B': [['sas', '8 GB SAS · Q4 + adapter']],
        '14B': [['sas', '16 GB SAS · Q4_K_M']],
        '32B': [['muted', '32 GB tier · not evaluated']]
    },

    async render(container, app) {
        const raw = (await app.fetchJson('data/model_architectures.json')) || [];
        const jobs = await Data.jobs16();
        const conds = await Data.tier8Conditions();

        const byId = {};
        raw.forEach(m => { if (!byId[m.model_id] || (m.hidden_size && !byId[m.model_id].hidden_size)) byId[m.model_id] = m; });
        const models = Object.values(byId).map(m => ({ ...m, size: (m.model_id.match(/(\d+(?:\.\d+)?B)/) || [])[1] }))
            .sort((a, b) => parseFloat(a.size) - parseFloat(b.size));

        const peak8 = arm => Math.max(...conds.filter(c => c.arm === arm).map(c => c.peakGb));
        const tiers = [
            { name: '8 GB', cap: 6.4, reserve: 1.6, status: 'Development', statusCls: 'badge-withheld', sas: 'Qwen2.5-7B Q4 + adapter', mas: 'Shared 3B Q4 role backbone', sasPeak: peak8('sas'), masPeak: peak8('mas') },
            { name: '16 GB', cap: Data.APP_CEILING_GB, reserve: 16 - Data.NOMINAL_CAP_GB, status: 'Primary study', statusCls: 'badge-correct', sas: 'Qwen2.5-14B Q4_K_M', mas: '1.5B + 3B + 0.5B F16 (resident)', sasPeak: jobs['tier16-sas-primary'].peakGb, masPeak: jobs['tier16-mas-primary'].peakGb, primary: true },
            { name: '32 GB', cap: 25.6, reserve: 6.4, status: 'Not evaluated', statusCls: '', sas: 'Qwen2.5-32B Q4_K_M (planned)', mas: 'Larger F16 team (planned)' }
        ];

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Model family · Qwen2.5-Instruct',
                title: 'One budget, two bets: <span class="c-mas">many small precise models</span> or <span class="c-sas">one large compressed model</span>',
                sub: 'Every model comes from the same Qwen2.5-Instruct family, so the comparison is about deployment recipe rather than vendor. SAS uses GGUF Q4_K_M quantization; the MAS team runs at full F16 precision.'
            })}

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                ${tiers.map((t, i) => `
                    <div class="card card-hover reveal ${t.primary ? 'ring-1 ring-[rgba(var(--color-mas-rgb),.45)]' : ''}" style="--i:${i + 1}">
                        <div class="flex items-center justify-between">
                            <div class="text-xl font-bold tracking-tight">${t.name}</div>
                            <span class="badge ${t.statusCls}">${t.status}</span>
                        </div>
                        <div class="text-xs t-muted mt-1 font-mono">${t.cap} GB app budget · ${t.reserve.toFixed(1)} GB nominal OS reserve</div>
                        <div class="space-y-3 mt-5">
                            ${['sas', 'mas'].map(arm => `
                                <div>
                                    <div class="flex justify-between text-xs mb-1.5">
                                        <span class="flex items-center gap-2 min-w-0">${UI.armBadge(arm)}<span class="t-secondary truncate">${t[arm]}</span></span>
                                        <span class="font-mono shrink-0 ml-2">${t[arm + 'Peak'] ? t[arm + 'Peak'].toFixed(2) + ' GB' : '—'}</span>
                                    </div>
                                    ${UI.meter(t[arm + 'Peak'] || 0, t.cap, `var(--color-${arm})`)}
                                </div>`).join('')}
                        </div>
                        <div class="text-[11px] t-muted mt-3">${t.sasPeak ? 'Bars show measured peak RSS against the app budget' : 'Configured but never run'}</div>
                    </div>`).join('')}
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
                ${UI.card({
                    cls: 'xl:col-span-2', i: 4,
                    title: 'Model scale',
                    sub: 'Transformer layers and hidden width',
                    body: `<div class="h-72"><canvas id="mdl-scale"></canvas></div>`
                })}
                ${UI.card({
                    cls: 'xl:col-span-3', i: 5,
                    title: 'Who plays which role',
                    sub: 'Architecture details from each pinned config.json',
                    body: `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                            ${models.map(m => `
                                <div class="p-3.5 rounded-xl" style="background:var(--bg-surface-elevated); border:1px solid var(--border-light)">
                                    <div class="flex items-center justify-between">
                                        <div class="font-semibold">Qwen2.5-${m.size}</div>
                                        <span class="badge">${m.torch_dtype}</span>
                                    </div>
                                    <div class="flex flex-wrap gap-1.5 mt-2">
                                        ${(this.ROLES[m.size] || []).map(([tone, label]) => `<span class="badge ${tone === 'muted' ? '' : 'badge-' + tone}">${label}</span>`).join('')}
                                    </div>
                                    <div class="grid grid-cols-4 gap-2 mt-3 text-center">
                                        ${[['layers', m.num_hidden_layers], ['hidden', m.hidden_size], ['heads', m.num_attention_heads], ['kv', m.num_key_value_heads]].map(([k, v]) => `
                                            <div><div class="font-mono text-sm font-semibold">${v ?? '—'}</div><div class="text-[10px] t-muted">${k}</div></div>`).join('')}
                                    </div>
                                </div>`).join('')}
                        </div>`
                })}
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                ${UI.insight({ i: 6, tone: 'mas', icon: 'cpu', title: 'Shared runtime settings', body: 'CPU inference, eight threads, greedy decoding, seed 42, 4,096-token context per call, no GPU layers, mmap off.' })}
                ${UI.insight({ i: 7, tone: 'sas', icon: 'coins', title: 'Same token ceiling, not the same compute', body: 'Both arms get 2,048 generated tokens per case across all stages. Prompts, call counts and FLOPs still differ.' })}
                ${UI.insight({ i: 8, tone: 'warn', icon: 'git-branch', title: 'Recipes, not isolated factors', body: 'Size, precision, role count and prompts change together, so the study cannot attribute the gap to any single one.' })}
            </div>
        `;

        this.renderScale(models);
    },

    renderScale(models) {
        const rows = models.filter(m => m.hidden_size);
        const colorFor = size => {
            const r = (this.ROLES[size] || [])[0];
            return r && r[0] !== 'muted' ? UI.css(`--color-${r[0]}`) : UI.css('--text-muted');
        };
        UI.chart('mdl-scale', {
            type: 'bubble',
            data: {
                datasets: [{
                    label: 'Models',
                    data: rows.map(m => ({ x: m.num_hidden_layers, y: m.hidden_size, r: 5 + 2.4 * Math.sqrt(parseFloat(m.size)), size: m.size })),
                    backgroundColor: rows.map(m => colorFor(m.size) + '66'),
                    borderColor: rows.map(m => colorFor(m.size)), borderWidth: 2
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                animation: { duration: 1300, easing: 'easeOutBack', delay: ctx => ctx.dataIndex * 110 },
                plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => `Qwen2.5-${c.raw.size}: ${c.raw.x} layers × ${c.raw.y} hidden` } } },
                scales: { x: { title: { display: true, text: 'Layers' }, suggestedMin: 16, suggestedMax: 70 }, y: { title: { display: true, text: 'Hidden size' }, suggestedMin: 0, suggestedMax: 6000 } }
            }
        });
    }
});
