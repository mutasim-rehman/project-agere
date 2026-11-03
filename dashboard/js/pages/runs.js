/**
 * Runs & Evidence Page - Academic Light Theme
 */

window.App.registerPage('runs', {
    state: {
        evidence: [],
        conditions: [],
        archiveStats: {},
        search: ''
    },

    async render(container, app) {
        if (this.state.evidence.length === 0) {
            this.state.evidence = await app.fetchJson('data/le16_v2/tier8_evidence_catalog.json') || [];
            this.state.conditions = await app.fetchJson('data/le16_v2/tier8_condition_inventory.json') || [];
            this.state.archiveStats = await app.fetchJson('data/archive_stats.json') || {};
        }

        const stats = this.state.archiveStats;

        container.innerHTML = `
            <!-- Top Summary Card (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="space-y-1 max-w-4xl">
                    <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                        Execution Provenance & Archive Telemetry
                    </div>
                    <h2 class="text-base font-bold text-[#172033]">
                        Lab Execution History & Historical Evidence Catalog
                    </h2>
                    <p class="text-xs text-[#64748B] leading-relaxed">
                        Complete chronicle of experimental iterations: initial 8 GB naive baselines (with invalid KV caches), iterative counterfactual verifier curricula, 16 GB recovery jobs, and full audit logs.
                    </p>
                </div>
            </div>

            <!-- Archive Overview Row -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Total Source Files</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">${stats.total_files ?? '2,598'}</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">1,629 unique content hashes</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Total Evidence Volume</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">${stats.total_mb ? stats.total_mb + ' MB' : '645 MB'}</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">17 managed archives</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">Cataloged Artifacts</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">197 Items</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">Indexed research outputs</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-[#64748B] font-semibold">8 GB Experimental Conditions</div>
                    <div class="text-xl font-bold font-mono text-[#172033] mt-1">15 Conditions</div>
                    <div class="text-[11px] text-[#94A3B8] font-mono mt-0.5">30 recorded evaluations</div>
                </div>
            </div>

            <!-- 8 GB Experimental Condition Inventory -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">8 GB Experimental Condition Inventory (30 Evaluations)</h3>
                        <p class="text-xs text-[#64748B]">Evaluations across control, crossed, baseline, and analysis conditions</p>
                    </div>
                    <span class="badge badge-sas">8 GB Natural Regime</span>
                </div>

                <div class="table-container max-h-72 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Job Name</th>
                                <th>Metric</th>
                                <th>n</th>
                                <th>Reports</th>
                                <th>Correct</th>
                                <th>Wrong</th>
                                <th>Withheld</th>
                                <th>Gen Tokens</th>
                                <th>Latency</th>
                                <th>Peak RSS</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.state.conditions.map(c => `
                                <tr>
                                    <td class="font-mono text-xs text-[#172033] font-medium">${c.job}</td>
                                    <td class="text-xs text-[#64748B] font-mono">${c.metric}</td>
                                    <td class="font-mono text-xs text-[#172033]">${c.n}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${c.reports}</td>
                                    <td class="font-mono text-xs font-bold text-[#15803D]">${c.correct}</td>
                                    <td class="font-mono text-xs font-bold text-[#DC2626]">${c.wrong}</td>
                                    <td class="font-mono text-xs font-bold text-[#D97706]">${c.withheld}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${c.generated_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${c.inference_seconds.toFixed(1)}s</td>
                                    <td class="font-mono text-xs text-[#172033] font-semibold">${(c.peak_rss_bytes / (1024**3)).toFixed(2)} GB</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Historical Evidence Catalog Browser -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[#E2E8F0] gap-3">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Historical Evidence Catalog (197 Artifacts)</h3>
                        <p class="text-xs text-[#64748B]">Search cataloged checkpoint logs, diagnostic runs, and traces</p>
                    </div>
                    <input id="evidence-search" type="text" placeholder="Filter artifact path..." class="input-search text-xs w-full md:w-64">
                </div>

                <div class="table-container max-h-72 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Artifact Path / Filename</th>
                                <th>Category</th>
                                <th>Archive Location</th>
                            </tr>
                        </thead>
                        <tbody id="evidence-table-body">
                            <!-- Populated dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        this.renderEvidenceRows();

        document.getElementById('evidence-search')?.addEventListener('input', (e) => {
            this.state.search = e.target.value.toLowerCase().trim();
            this.renderEvidenceRows();
        });
    },

    renderEvidenceRows() {
        const tbody = document.getElementById('evidence-table-body');
        if (!tbody) return;

        let items = this.state.evidence;
        if (this.state.search) {
            items = items.filter(it => {
                const s = JSON.stringify(it).toLowerCase();
                return s.includes(this.state.search);
            });
        }

        const displayItems = items.slice(0, 25);
        if (displayItems.length === 0) {
            tbody.innerHTML = `<tr><td colspan="3" class="text-center py-6 text-[#64748B] text-xs">No matching evidence artifacts.</td></tr>`;
            return;
        }

        tbody.innerHTML = displayItems.map(it => {
            const pathStr = typeof it === 'string' ? it : (it.path || it.source || it.name || JSON.stringify(it));
            const cat = pathStr.includes('runs') ? 'Runs' : (pathStr.includes('datasets') ? 'Datasets' : (pathStr.includes('weights') ? 'Weights' : 'Phase 2'));
            return `
                <tr>
                    <td class="font-mono text-xs text-[#172033] font-medium">${pathStr}</td>
                    <td><span class="badge ${cat === 'Runs' ? 'badge-mas' : 'badge-sas'}">${cat}</span></td>
                    <td class="font-mono text-xs text-[#64748B]">dashboard_handoff/evidence/</td>
                </tr>
            `;
        }).join('');
    }
});
