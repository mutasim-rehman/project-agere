/**
 * Case Explorer: filter 1,728 case outputs, with a live summary of the current selection.
 */

window.App.registerPage('cases', {
    state: {
        allCases: [],
        filteredCases: [],
        predictions: null,
        tier: '16',
        arm: 'all',
        profile: 'all',
        outcome: 'all',
        company: 'all',
        search: '',
        page: 1,
        pageSize: 15
    },

    async loadPredictions() {
        if (!this.state.predictions) this.state.predictions = (await App.fetchJson('data/case_predictions_sample.json')) || {};
        return this.state.predictions;
    },

    async render(container, app) {
        this.state.allCases = this.state.tier === '8' ? await Data.cases8() : await Data.cases16();
        this.loadPredictions();

        container.innerHTML = `
            <section class="card reveal" style="--i:0">
                <div class="flex flex-col xl:flex-row xl:items-end gap-3">
                    <div class="grid grid-cols-2 md:grid-cols-5 gap-3 flex-1">
                        ${this.select('filter-tier', 'RAM tier', [['16', '16 GB (960)'], ['8', '8 GB (768)']], this.state.tier)}
                        ${this.select('filter-arm', 'Arm', [['all', 'Both arms'], ['mas', 'MAS team'], ['sas', 'SAS monolith']], this.state.arm)}
                        ${this.select('filter-profile', 'Profile', this.profileOptions(), this.state.profile)}
                        ${this.select('filter-outcome', 'Outcome', [['all', 'Any outcome'], ['correct', 'Correct'], ['wrong', 'Wrong'], ['withheld', 'Withheld']], this.state.outcome)}
                        <div id="company-select-wrap"></div>
                    </div>
                    <div class="flex items-center gap-2">
                        <div class="relative flex-1 xl:w-64">
                            <i data-lucide="search" class="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 t-muted"></i>
                            <input id="case-search-input" type="text" placeholder="Case ID or ticker…" class="input-search w-full pl-8" value="${UI.esc(this.state.search)}">
                        </div>
                        <button id="case-reset-btn" class="btn"><i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>Reset</button>
                    </div>
                </div>
            </section>

            <div id="case-summary" class="grid grid-cols-1 lg:grid-cols-4 gap-4"></div>

            <section class="card p-0 overflow-hidden reveal" style="--i:3">
                <div class="table-container border-0 rounded-none max-h-[560px]">
                    <table class="data-table">
                        <thead>
                            <tr><th>Case</th><th>Company</th><th>Arm</th><th>Profile</th><th>Reported</th><th>Raw exec</th><th class="text-right">Tokens</th><th class="text-right">Latency</th><th></th></tr>
                        </thead>
                        <tbody id="case-table-body"></tbody>
                    </table>
                </div>
                <div class="px-4 py-3 border-t border-[var(--border-color)] flex items-center justify-between text-xs">
                    <div id="case-pagination-info" class="t-secondary font-mono"></div>
                    <div class="flex items-center gap-2">
                        <button id="case-prev-btn" class="btn py-1"><i data-lucide="chevron-left" class="w-3.5 h-3.5"></i></button>
                        <span id="case-page-num" class="font-mono t-primary px-2"></span>
                        <button id="case-next-btn" class="btn py-1"><i data-lucide="chevron-right" class="w-3.5 h-3.5"></i></button>
                    </div>
                </div>
            </section>
        `;

        this.renderCompanySelect();
        this.bindEvents(app);
        this.applyFilters();
    },

    select(id, label, options, value) {
        return `
            <label class="block">
                <span class="block text-[11px] t-muted mb-1">${label}</span>
                <select id="${id}" class="select-filter w-full">
                    ${options.map(([v, l]) => `<option value="${v}" ${v === value ? 'selected' : ''}>${l}</option>`).join('')}
                </select>
            </label>`;
    },

    profileOptions() {
        return this.state.tier === '8'
            ? [['all', 'All conditions'], ['control', 'Control'], ['crossed', 'Crossed'], ['baseline', 'Baseline']]
            : [['all', 'All profiles'], ['primary', 'Primary'], ['direct_control', 'Direct control'], ['repair_ablation', 'Repair ablation']];
    },

    renderCompanySelect() {
        const companies = Array.from(new Set(this.state.allCases.map(c => c.company).filter(Boolean))).sort();
        if (!companies.includes(this.state.company)) this.state.company = 'all';
        document.getElementById('company-select-wrap').innerHTML =
            this.select('filter-company', 'Company', [['all', `All (${companies.length})`], ...companies.map(c => [c, c])], this.state.company);
        document.getElementById('filter-company').addEventListener('change', e => { this.state.company = e.target.value; this.state.page = 1; this.applyFilters(); });
    },

    bindEvents() {
        const on = (id, key) => document.getElementById(id)?.addEventListener('change', e => {
            this.state[key] = e.target.value;
            this.state.page = 1;
            this.applyFilters();
        });

        document.getElementById('filter-tier')?.addEventListener('change', async e => {
            this.state.tier = e.target.value;
            this.state.profile = 'all';
            this.state.page = 1;
            this.state.allCases = this.state.tier === '8' ? await Data.cases8() : await Data.cases16();
            const prof = document.getElementById('filter-profile');
            prof.innerHTML = this.profileOptions().map(([v, l]) => `<option value="${v}">${l}</option>`).join('');
            this.renderCompanySelect();
            this.applyFilters();
        });
        on('filter-arm', 'arm');
        on('filter-profile', 'profile');
        on('filter-outcome', 'outcome');

        let t;
        document.getElementById('case-search-input')?.addEventListener('input', e => {
            clearTimeout(t);
            t = setTimeout(() => { this.state.search = e.target.value.toLowerCase().trim(); this.state.page = 1; this.applyFilters(); }, 150);
        });

        document.getElementById('case-reset-btn')?.addEventListener('click', () => {
            Object.assign(this.state, { arm: 'all', profile: 'all', outcome: 'all', company: 'all', search: '', page: 1 });
            ['filter-arm', 'filter-profile', 'filter-outcome', 'filter-company'].forEach(id => { const el = document.getElementById(id); if (el) el.value = 'all'; });
            document.getElementById('case-search-input').value = '';
            this.applyFilters();
        });

        document.getElementById('case-prev-btn')?.addEventListener('click', () => {
            if (this.state.page > 1) { this.state.page--; this.renderTableRows(); }
        });
        document.getElementById('case-next-btn')?.addEventListener('click', () => {
            if (this.state.page < Math.ceil(this.state.filteredCases.length / this.state.pageSize)) { this.state.page++; this.renderTableRows(); }
        });
    },

    profileOf(c) {
        return c.profile || (c.condition || '').replace(/^(diagnostic_audit|model_selection)-/, '').replace(/-full-01$/, '');
    },

    applyFilters() {
        const st = this.state;
        let list = st.allCases;
        if (st.arm !== 'all') list = list.filter(c => c.arm === st.arm);
        if (st.profile !== 'all') list = list.filter(c => c.profile === st.profile || (c.condition && c.condition.includes(st.profile)));
        if (st.outcome !== 'all') list = list.filter(c => c.reported_outcome === st.outcome);
        if (st.company !== 'all') list = list.filter(c => c.company === st.company);
        if (st.search) list = list.filter(c => c.case_id?.toLowerCase().includes(st.search) || c.company?.toLowerCase().includes(st.search));
        st.filteredCases = list;
        this.renderSummary();
        this.renderTableRows();
    },

    renderSummary() {
        const list = this.state.filteredCases;
        const box = document.getElementById('case-summary');
        if (!box) return;
        const by = arm => Data.summarize(list.filter(c => c.arm === arm));
        const s = by('sas'), m = by('mas');
        const all = Data.summarize(list);
        const armRow = (arm, x) => x.n ? `
            <div>
                <div class="flex justify-between text-xs mb-1.5"><span class="font-semibold c-${arm}">${arm.toUpperCase()}</span><span class="font-mono t-muted">${x.n} outputs · ${UI.pct(x.C, x.n)}% correct</span></div>
                ${UI.stackbar(x.C, x.W, x.H, x.n)}
            </div>` : '';

        box.innerHTML = `
            ${UI.kpi({ label: 'Matching outputs', value: list.length, foot: `${new Set(list.map(c => c.case_id)).size} unique questions`, icon: 'filter', i: 1 })}
            <div class="card reveal lg:col-span-2" style="--i:2">
                <div class="flex items-center justify-between mb-3"><span class="kpi-label">Outcome mix of the selection</span>${UI.outcomeLegend()}</div>
                <div class="space-y-3">${armRow('sas', s)}${armRow('mas', m)}${!s.n && !m.n ? '<div class="text-xs t-muted">No outputs match.</div>' : ''}</div>
            </div>
            ${UI.kpi({ label: 'Avg latency per output', value: all.secPerCase, decimals: 1, suffix: ' s', foot: `${UI.num(all.genPerCase, 0)} generated tokens on average`, tone: 'withheld', icon: 'timer', i: 3 })}
        `;
        if (window.lucide) lucide.createIcons();
        UI.animateIn(box);
    },

    renderTableRows() {
        const tbody = document.getElementById('case-table-body');
        if (!tbody) return;
        const st = this.state;
        const start = (st.page - 1) * st.pageSize;
        const pageItems = st.filteredCases.slice(start, start + st.pageSize);
        this.pageItems = pageItems;

        tbody.innerHTML = pageItems.length ? pageItems.map((c, i) => `
            <tr class="cursor-pointer" style="animation-delay:${i * 18}ms" onclick="App.pages.cases.openCaseDetail(App.pages.cases.pageItems[${i}])">
                <td class="font-mono text-xs">${UI.esc(c.case_id)}</td>
                <td class="font-medium">${UI.esc(c.company || '—')}</td>
                <td>${UI.armBadge(c.arm)}</td>
                <td class="text-xs t-secondary">${UI.esc(this.profileOf(c))}</td>
                <td>${UI.outcomeBadge(c.reported_outcome, c.reported_correct)}</td>
                <td>${UI.outcomeBadge(c.raw_outcome, c.raw_correct)}</td>
                <td class="font-mono text-xs text-right">${c.generated_tokens ?? '—'}</td>
                <td class="font-mono text-xs text-right t-secondary">${c.inference_seconds ? c.inference_seconds.toFixed(1) + ' s' : '—'}</td>
                <td class="text-right"><i data-lucide="chevron-right" class="w-4 h-4 t-muted inline"></i></td>
            </tr>`).join('')
            : `<tr><td colspan="9" class="text-center py-10 t-muted text-sm">No cases match these filters.</td></tr>`;

        const total = st.filteredCases.length;
        const end = Math.min(start + st.pageSize, total);
        document.getElementById('case-pagination-info').innerText = `${total ? start + 1 : 0}–${end} of ${UI.num(total)}`;
        document.getElementById('case-page-num').innerText = `${st.page} / ${Math.max(1, Math.ceil(total / st.pageSize))}`;
        if (window.lucide) lucide.createIcons();
    },

    async openByKey(job, caseId) {
        const rows = await Data.cases16();
        const c = rows.find(r => r.job === job && r.case_id === caseId);
        if (c) this.openCaseDetail(c);
    },

    async openCaseDetail(c) {
        const preds = await this.loadPredictions();
        const rich = c.job ? preds[`${c.job}/${c.case_id}`] : null;

        document.getElementById('modal-case-title').innerText = c.case_id;
        document.getElementById('modal-case-subtitle').innerText = `${c.company} · ${c.report} · ${c.arm.toUpperCase()} · ${this.profileOf(c)} · ${c.tier} GB`;

        const stat = (label, value) => `
            <div><div class="text-[10px] t-muted uppercase tracking-wider">${label}</div><div class="mt-1 text-sm font-semibold font-mono">${value}</div></div>`;

        let siblings = '';
        if (c.tier === 16) {
            const all = (await Data.cases16()).filter(r => r.case_id === c.case_id);
            siblings = UI.card({
                title: 'Same question across all six jobs',
                sub: 'Reported-answer outcome',
                body: `
                    <div class="grid grid-cols-3 gap-2 text-xs">
                        ${Data.PROFILES.map(p => `
                            <div class="rounded-lg p-3" style="background:var(--bg-surface-elevated)">
                                <div class="t-muted mb-2">${Data.PROFILE_LABEL[p]}</div>
                                ${['sas', 'mas'].map(arm => {
                                    const r = all.find(x => x.profile === p && x.arm === arm);
                                    const here = r && r.job === c.job;
                                    return `<div class="flex items-center justify-between py-0.5 ${here ? 'font-semibold' : ''}">${UI.armBadge(arm)}${r ? UI.outcomeBadge(r.reported_outcome, r.reported_correct) : '—'}</div>`;
                                }).join('')}
                            </div>`).join('')}
                    </div>`
            });
        }

        const program = rich && rich.steps ? `
            <div class="flex flex-wrap items-center gap-2">
                ${rich.steps.map((s, i) => `
                    <div class="flex items-center gap-2">
                        <div class="rounded-lg px-3 py-2 text-xs font-mono" style="background:var(--bg-surface-elevated); border:1px solid var(--border-color)">
                            <span class="t-muted">#${i}</span> ${UI.esc(s.left?.value)} <span class="c-accent font-semibold">${UI.esc(s.op)}</span> ${UI.esc(s.right?.value)}
                        </div>
                        ${i < rich.steps.length - 1 ? '<i data-lucide="arrow-right" class="w-3.5 h-3.5 t-muted"></i>' : ''}
                    </div>`).join('')}
            </div>
            <div class="text-xs t-secondary mt-3">Decision <span class="badge">${UI.esc(rich.decision)}</span> · unit <span class="badge">${UI.esc(rich.answer_unit || 'unspecified')}</span></div>` : '';

        document.getElementById('modal-case-body').innerHTML = `
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-xl" style="background:var(--bg-surface-elevated)">
                <div><div class="text-[10px] t-muted uppercase tracking-wider">Reported</div><div class="mt-1">${UI.outcomeBadge(c.reported_outcome, c.reported_correct)}</div></div>
                <div><div class="text-[10px] t-muted uppercase tracking-wider">Raw execution</div><div class="mt-1">${UI.outcomeBadge(c.raw_outcome, c.raw_correct)}</div></div>
                ${stat('Tokens (prompt + gen)', `${UI.num(c.prompt_tokens ?? 0)} + ${c.generated_tokens ?? 0}`)}
                ${stat('Inference', c.inference_seconds ? c.inference_seconds.toFixed(1) + ' s' : '—')}
            </div>
            ${program ? UI.card({ title: 'Calculation program', sub: UI.esc(rich.formula), body: program }) : ''}
            ${siblings}
            ${c.tier === 16 ? `
                <div class="flex flex-wrap gap-2 text-xs">
                    <span class="badge ${c.execution_valid ? 'badge-correct' : 'badge-wrong'}">execution ${c.execution_valid ? 'valid' : 'invalid'}</span>
                    <span class="badge ${c.repair_attempted ? 'badge-withheld' : ''}">repair ${c.repair_attempted ? 'attempted' : 'not attempted'}</span>
                    <span class="badge ${c.annotated_evidence_complete ? 'badge-correct' : 'badge-withheld'}">gold evidence ${c.annotated_evidence_complete ? 'retrieved' : 'incomplete'}</span>
                    <span class="badge">${UI.esc(c.attempt || '')}</span>
                </div>` : ''}
        `;
        App.openModal('case-modal');
        UI.animateIn(document.getElementById('modal-case-body'));
    }
});
