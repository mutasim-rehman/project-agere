/**
 * Experiment Runs, Logs & Evidence Catalog Page
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
            <!-- Top Header -->
            <div class="card bg-gradient-to-r from-slate-900 to-indigo-950/20 border-indigo-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-sas">Lab Chronology</span>
                            <span class="text-xs text-slate-400 font-mono">17 Managed Archives • 2,598 Evidence Files</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Complete Lab Execution History & Historical Evidence Catalog
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            Chronicles the developmental arc of Project Agere: early naive attempts at 8 GB (with invalid KV caches), iterative counterfactual verifier curricula, 16 GB recovery jobs, and full audit logs.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Archive Overview Cards -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Total Source Files</div>
                    <div class="text-2xl font-bold font-mono text-white mt-1">${stats.total_files ?? '2,598'}</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">1,629 unique content hashes</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Total Archive Volume</div>
                    <div class="text-2xl font-bold font-mono text-cyan-400 mt-1">${stats.total_mb ? stats.total_mb + ' MB' : '645 MB'}</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">Compressed into 57 MB Git files</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">Evidence Catalog Items</div>
                    <div class="text-2xl font-bold font-mono text-emerald-400 mt-1">197 Items</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">Annotated lab artifacts</div>
                </div>
                <div class="card p-4">
                    <div class="text-xs text-slate-400 font-mono">8 GB Experimental Conditions</div>
                    <div class="text-2xl font-bold font-mono text-purple-400 mt-1">15 Conditions</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">30 recorded condition evaluations</div>
                </div>
            </div>

            <!-- 8 GB Experimental Condition Inventory (30 Rows) -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="layers" class="w-4 h-4 text-purple-400"></i>
                            8 GB Experimental Condition Inventory
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Evaluations across control, crossed, baseline, and analysis conditions</p>
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
                                <th>Latency (s)</th>
                                <th>Peak RSS (GB)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${this.state.conditions.map(c => `
                                <tr>
                                    <td class="font-mono text-xs text-white">${c.job}</td>
                                    <td class="text-xs text-slate-300 font-mono">${c.metric}</td>
                                    <td class="font-mono text-xs">${c.n}</td>
                                    <td class="font-mono text-xs">${c.reports}</td>
                                    <td class="font-mono text-xs font-bold text-emerald-400">${c.correct}</td>
                                    <td class="font-mono text-xs text-rose-400">${c.wrong}</td>
                                    <td class="font-mono text-xs text-amber-400">${c.withheld}</td>
                                    <td class="font-mono text-xs text-slate-300">${c.generated_tokens.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-slate-300">${c.inference_seconds.toFixed(1)}s</td>
                                    <td class="font-mono text-xs text-cyan-400">${(c.peak_rss_bytes / (1024**3)).toFixed(2)} GB</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Historical Evidence Catalog Browser -->
            <div class="card">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between pb-3 border-b border-[var(--border-color)] gap-3">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="file-text" class="w-4 h-4 text-cyan-400"></i>
                            Historical Evidence Catalog (197 Artifacts)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Search cataloged checkpoint logs, diagnostic runs, and traces</p>
                    </div>
                    <input id="evidence-search" type="text" placeholder="Search artifact name or path..." class="input-search text-xs w-full md:w-64">
                </div>

                <div class="table-container max-h-80 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Artifact Path / Description</th>
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
            tbody.innerHTML = `<tr><td colspan="3" class="text-center py-6 text-slate-500 text-xs">No matching evidence artifacts.</td></tr>`;
            return;
        }

        tbody.innerHTML = displayItems.map(it => {
            const pathStr = typeof it === 'string' ? it : (it.path || it.source || it.name || JSON.stringify(it));
            const cat = pathStr.includes('runs') ? 'Runs' : (pathStr.includes('datasets') ? 'Datasets' : (pathStr.includes('weights') ? 'Weights' : 'Phase 2'));
            return `
                <tr>
                    <td class="font-mono text-xs text-white">${pathStr}</td>
                    <td><span class="badge ${cat === 'Runs' ? 'badge-mas' : 'badge-sas'}">${cat}</span></td>
                    <td class="font-mono text-xs text-slate-400">dashboard_handoff/evidence/</td>
                </tr>
            `;
        }).join('');
    }
});

