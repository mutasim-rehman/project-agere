/**
 * Case & Failure Explorer Page
 */

window.App.registerPage('cases', {
    state: {
        allCases: [],
        filteredCases: [],
        predictions: {},
        tier: '16',
        arm: 'all',
        profile: 'all',
        outcome: 'all',
        company: 'all',
        search: '',
        page: 1,
        pageSize: 15
    },

    async render(container, app) {
        // Load data if not cached
        if (this.state.allCases.length === 0) {
            const cases16 = await app.fetchJson('data/tier16_v2/case_outcomes.json') || [];
            this.state.allCases = cases16;
            this.state.predictions = await app.fetchJson('data/case_predictions_sample.json') || {};
        }

        // Get unique companies
        const companies = Array.from(new Set(this.state.allCases.map(c => c.company).filter(Boolean))).sort();

        container.innerHTML = `
            <!-- Filter Toolbar -->
            <div class="card p-4 space-y-4">
                <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
                    <div class="flex items-center gap-2">
                        <i data-lucide="filter" class="w-4 h-4 text-emerald-400"></i>
                        <span class="text-sm font-bold text-white">Filter Cases</span>
                        <span id="case-count-badge" class="badge badge-mas font-mono">0 matches</span>
                    </div>
                    <div class="flex items-center gap-2 w-full lg:w-auto">
                        <input id="case-search-input" type="text" placeholder="Search Case ID or Company..." class="input-search w-full lg:w-64 text-xs">
                        <button id="case-reset-btn" class="btn btn-secondary text-xs">Reset</button>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3 pt-2 border-t border-[var(--border-color)]">
                    <div>
                        <label class="block text-[11px] text-slate-400 font-mono mb-1">RAM Tier</label>
                        <select id="filter-tier" class="select-filter w-full text-xs">
                            <option value="16" selected>16 GB Tier (960 rows)</option>
                            <option value="8">8 GB Tier (768 rows)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[11px] text-slate-400 font-mono mb-1">Deployment Arm</label>
                        <select id="filter-arm" class="select-filter w-full text-xs">
                            <option value="all">All Arms (MAS & SAS)</option>
                            <option value="mas">MAS-FP16 (Specialists)</option>
                            <option value="sas">SAS-Quant (Monolith)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[11px] text-slate-400 font-mono mb-1">Profile / Role</label>
                        <select id="filter-profile" class="select-filter w-full text-xs">
                            <option value="all">All Profiles</option>
                            <option value="primary">Primary (Verifier + Repair)</option>
                            <option value="direct_control">Direct Control (No Verifier)</option>
                            <option value="repair_ablation">Repair Ablation</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[11px] text-slate-400 font-mono mb-1">Outcome</label>
                        <select id="filter-outcome" class="select-filter w-full text-xs">
                            <option value="all">All Outcomes</option>
                            <option value="correct">Reported Correct</option>
                            <option value="wrong">Reported Wrong</option>
                            <option value="withheld">Withheld by Policy</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-[11px] text-slate-400 font-mono mb-1">Company</label>
                        <select id="filter-company" class="select-filter w-full text-xs">
                            <option value="all">All Companies (${companies.length})</option>
                            ${companies.map(comp => `<option value="${comp}">${comp}</option>`).join('')}
                        </select>
                    </div>
                </div>
            </div>

            <!-- Table of Filtered Cases -->
            <div class="card p-0 overflow-hidden">
                <div class="table-container max-h-[600px] overflow-y-auto">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Case ID</th>
                                <th>Company</th>
                                <th>Report</th>
                                <th>Arm</th>
                                <th>Profile</th>
                                <th>Reported</th>
                                <th>Raw Exec</th>
                                <th>Delivered</th>
                                <th>Tokens</th>
                                <th>Latency (s)</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="case-table-body">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>

                <!-- Pagination Footer -->
                <div class="p-3 bg-[var(--bg-surface-elevated)] border-t border-[var(--border-color)] flex items-center justify-between text-xs">
                    <div id="case-pagination-info" class="text-slate-400 font-mono">
                        Showing 0 to 0 of 0 entries
                    </div>
                    <div class="flex items-center gap-2">
                        <button id="case-prev-btn" class="btn btn-secondary text-xs py-1 px-3">Previous</button>
                        <span id="case-page-num" class="font-mono text-white px-2">Page 1</span>
                        <button id="case-next-btn" class="btn btn-secondary text-xs py-1 px-3">Next</button>
                    </div>
                </div>
            </div>
        `;

        // Apply filters & bind listeners
        this.bindEvents(app);
        await this.applyFilters();
    },

    bindEvents(app) {
        const update = async () => {
            this.state.page = 1;
            await this.applyFilters();
        };

        document.getElementById('filter-tier')?.addEventListener('change', async (e) => {
            this.state.tier = e.target.value;
            if (this.state.tier === '8') {
                const cases8 = await app.fetchJson('data/le16_v2/tier8_case_outcomes.json') || [];
                this.state.allCases = cases8;
            } else {
                const cases16 = await app.fetchJson('data/tier16_v2/case_outcomes.json') || [];
                this.state.allCases = cases16;
            }
            await update();
        });

        document.getElementById('filter-arm')?.addEventListener('change', (e) => {
            this.state.arm = e.target.value;
            update();
        });

        document.getElementById('filter-profile')?.addEventListener('change', (e) => {
            this.state.profile = e.target.value;
            update();
        });

        document.getElementById('filter-outcome')?.addEventListener('change', (e) => {
            this.state.outcome = e.target.value;
            update();
        });

        document.getElementById('filter-company')?.addEventListener('change', (e) => {
            this.state.company = e.target.value;
            update();
        });

        document.getElementById('case-search-input')?.addEventListener('input', (e) => {
            this.state.search = e.target.value.toLowerCase().trim();
            update();
        });

        document.getElementById('case-reset-btn')?.addEventListener('click', () => {
            this.state.arm = 'all';
            this.state.profile = 'all';
            this.state.outcome = 'all';
            this.state.company = 'all';
            this.state.search = '';
            document.getElementById('filter-arm').value = 'all';
            document.getElementById('filter-profile').value = 'all';
            document.getElementById('filter-outcome').value = 'all';
            document.getElementById('filter-company').value = 'all';
            document.getElementById('case-search-input').value = '';
            update();
        });

        document.getElementById('case-prev-btn')?.addEventListener('click', () => {
            if (this.state.page > 1) {
                this.state.page--;
                this.renderTableRows();
            }
        });

        document.getElementById('case-next-btn')?.addEventListener('click', () => {
            const maxPage = Math.ceil(this.state.filteredCases.length / this.state.pageSize);
            if (this.state.page < maxPage) {
                this.state.page++;
                this.renderTableRows();
            }
        });
    },

    async applyFilters() {
        let list = this.state.allCases;

        if (this.state.arm !== 'all') {
            list = list.filter(c => c.arm === this.state.arm);
        }
        if (this.state.profile !== 'all') {
            list = list.filter(c => c.profile === this.state.profile || (c.condition && c.condition.includes(this.state.profile)));
        }
        if (this.state.outcome !== 'all') {
            if (this.state.outcome === 'correct') {
                list = list.filter(c => c.reported_correct === true);
            } else if (this.state.outcome === 'withheld') {
                list = list.filter(c => c.reported_outcome === 'withheld');
            } else if (this.state.outcome === 'wrong') {
                list = list.filter(c => c.reported_correct === false && c.reported_outcome !== 'withheld');
            }
        }
        if (this.state.company !== 'all') {
            list = list.filter(c => c.company === this.state.company);
        }
        if (this.state.search) {
            list = list.filter(c => 
                (c.case_id && c.case_id.toLowerCase().includes(this.state.search)) ||
                (c.company && c.company.toLowerCase().includes(this.state.search))
            );
        }

        this.state.filteredCases = list;

        const badge = document.getElementById('case-count-badge');
        if (badge) badge.innerText = `${list.length} matches`;

        this.renderTableRows();
    },

    renderTableRows() {
        const tbody = document.getElementById('case-table-body');
        if (!tbody) return;

        const start = (this.state.page - 1) * this.state.pageSize;
        const pageItems = this.state.filteredCases.slice(start, start + this.state.pageSize);

        if (pageItems.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="text-center py-10 text-slate-500 text-xs">
                        No cases match the selected filters.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = pageItems.map(c => {
            const repBadge = c.reported_correct 
                ? '<span class="badge badge-correct">Correct</span>' 
                : (c.reported_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Wrong</span>');
            
            const rawBadge = c.raw_correct 
                ? '<span class="badge badge-correct">Match</span>' 
                : (c.raw_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Mismatch</span>');

            const armBadge = c.arm === 'mas' ? '<span class="badge badge-mas">MAS</span>' : '<span class="badge badge-sas">SAS</span>';

            return `
                <tr class="cursor-pointer" onclick='window.App.pages.cases.openCaseDetail(${JSON.stringify(c).replace(/'/g, "&apos;")})'>
                    <td class="font-mono text-xs text-white">${c.case_id}</td>
                    <td class="font-medium text-slate-300">${c.company || '—'}</td>
                    <td class="text-xs text-slate-400 font-mono">${c.report || '—'}</td>
                    <td>${armBadge}</td>
                    <td class="text-xs text-slate-300 font-mono">${c.profile || c.condition || '—'}</td>
                    <td>${repBadge}</td>
                    <td>${rawBadge}</td>
                    <td class="text-xs">${c.delivered ? '<span class="text-emerald-400">Yes</span>' : '<span class="text-slate-500">No</span>'}</td>
                    <td class="font-mono text-xs text-slate-300">${c.generated_tokens ?? '—'}</td>
                    <td class="font-mono text-xs text-slate-300">${c.inference_seconds ? c.inference_seconds.toFixed(1) : '—'}</td>
                    <td>
                        <button class="btn btn-secondary text-[10px] py-1 px-2" title="Inspect Prediction & Math Formula">
                            View
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        // Update pagination labels
        const total = this.state.filteredCases.length;
        const end = Math.min(start + this.state.pageSize, total);
        const infoEl = document.getElementById('case-pagination-info');
        if (infoEl) infoEl.innerText = `Showing ${total > 0 ? start + 1 : 0} to ${end} of ${total} entries`;

        const pageEl = document.getElementById('case-page-num');
        const maxPage = Math.max(1, Math.ceil(total / this.state.pageSize));
        if (pageEl) pageEl.innerText = `Page ${this.state.page} of ${maxPage}`;
    },

    openCaseDetail(c) {
        const key = `${c.job}/${c.case_id}`;
        const rich = this.state.predictions[key];

        const bodyEl = document.getElementById('modal-case-body');
        document.getElementById('modal-case-title').innerText = `Case Detail: ${c.case_id}`;
        document.getElementById('modal-case-subtitle').innerText = `${c.company} • ${c.arm.toUpperCase()} (${c.profile || c.condition || 'standard'})`;

        const repBadge = c.reported_correct 
            ? '<span class="badge badge-correct">Reported Correct</span>' 
            : (c.reported_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Reported Wrong</span>');

        const rawBadge = c.raw_correct 
            ? '<span class="badge badge-correct">Raw Correct</span>' 
            : (c.raw_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Raw Wrong</span>');

        bodyEl.innerHTML = `
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-[var(--bg-surface-elevated)] p-4 rounded-lg">
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Reported Answer</div>
                    <div class="mt-1">${repBadge}</div>
                </div>
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Raw Execution Match</div>
                    <div class="mt-1">${rawBadge}</div>
                </div>
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Tokens (Prompt + Gen)</div>
                    <div class="text-sm font-bold font-mono text-white mt-1">${c.prompt_tokens ?? 0} + ${c.generated_tokens ?? 0}</div>
                </div>
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Inference Latency</div>
                    <div class="text-sm font-bold font-mono text-white mt-1">${c.inference_seconds ? c.inference_seconds.toFixed(2) + 's' : 'N/A'}</div>
                </div>
            </div>

            ${rich && rich.formula ? `
                <div class="card p-4 border-indigo-500/30">
                    <div class="text-xs font-bold text-indigo-400 uppercase font-mono mb-2">Model Calculation Program</div>
                    <pre class="bg-slate-950 p-3 rounded font-mono text-xs text-emerald-400 overflow-x-auto">${rich.formula}</pre>
                    <div class="text-[11px] text-slate-400 mt-2">
                        Decision: <span class="font-bold text-white">${rich.decision}</span> • Declared Unit: <span class="font-bold text-white">${rich.answer_unit || 'unspecified'}</span>
                    </div>
                </div>
            ` : `
                <div class="card p-4">
                    <div class="text-xs font-bold text-slate-400 uppercase font-mono mb-1">Execution Audit</div>
                    <p class="text-xs text-slate-300">
                        Execution Valid: <span class="font-bold text-white">${c.execution_valid ? 'True' : 'False'}</span> • 
                        Repair Attempted: <span class="font-bold text-white">${c.repair_attempted ? 'Yes' : 'No'}</span>
                    </p>
                </div>
            `}

            <div class="card p-4">
                <div class="text-xs font-bold text-slate-400 uppercase font-mono mb-2">Protocol Reference</div>
                <p class="text-xs text-slate-400 leading-relaxed">
                    Evaluated under strict process RSS parity cap. Dual correctness requires both human-formatted output matching and direct code-block execution arithmetic matching gold values.
                </p>
            </div>
        `;

        window.App.openModal('case-modal');
    }
});

