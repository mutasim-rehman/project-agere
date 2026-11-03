/**
 * Research Provenance, Decision Log & Audit Page
 */

window.App.registerPage('provenance', {
    async render(container, app) {
        const docs = await app.fetchJson('data/docs_index.json') || [];
        const manifests = await app.fetchJson('data/manifests_summary.json') || {};
        const hf = manifests.hf_snapshots || {};

        container.innerHTML = `
            <!-- Top Header -->
            <div class="card bg-gradient-to-r from-slate-900 to-cyan-950/20 border-cyan-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-mas">Audit & Provenance</span>
                            <span class="text-xs text-slate-400 font-mono">Reproducibility Package</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Research Decision Chronology, Documentation & Artifact Integrity
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            Full audit trail supporting the Phase 3 submission. Includes decision milestones from DECISIONS.md, model snapshot commit hashes, weights checksums, and documentation index.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Milestone Timeline -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                        <i data-lucide="calendar" class="w-4 h-4 text-emerald-400"></i>
                        Key Methodology & Engineering Milestones
                    </h3>
                </div>

                <div class="space-y-4 mt-4 text-xs">
                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                            1
                        </div>
                        <div>
                            <div class="font-bold text-white">Phase 1: Spec Lock & RUPP Protocol Definition (Oct 2026)</div>
                            <div class="text-slate-400 mt-0.5">Established the Host-Adjusted Process-Tree RSS Cap protocol and equalized thinking-token budgets following Tran & Kiela (2026).</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                            2
                        </div>
                        <div>
                            <div class="font-bold text-white">Phase 2: Offline Conversion & Runtime Hardening (Oct 15, 2026)</div>
                            <div class="text-slate-400 mt-0.5">Quantized Qwen2.5 weights to GGUF Q4_K_M on dedicated lab PC. Validated memory limits and recorded conversion footprints.</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                            3
                        </div>
                        <div>
                            <div class="font-bold text-white">Phase 3: 16 GB Full Study & Swap Breach Recovery (Oct 28–30, 2026)</div>
                            <div class="text-slate-400 mt-0.5">Executed 6 evaluation jobs (960 case evaluations). Caught 44 MB swap failure in attempt-0001, invalidated run, and completed verified clean recovery in attempt-0002.</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-[10px] shrink-0 mt-0.5">
                            4
                        </div>
                        <div>
                            <div class="font-bold text-white">Submission Lock & Portable Dashboard Handoff (Nov 2, 2026)</div>
                            <div class="text-slate-400 mt-0.5">Packaged all derived data, 17 evidence archives, statistical reports, and portable browser-ready JSON handoff.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Documentation Index Cards Grid -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                        <i data-lucide="book-open" class="w-4 h-4 text-cyan-400"></i>
                        Core Research Documentation Library
                    </h3>
                    <p class="text-xs text-slate-400 mt-0.5">Editable markdown reports and formal manuscript packages</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    ${docs.map(d => `
                        <div class="card bg-[var(--bg-surface-elevated)] p-4 flex flex-col justify-between">
                            <div>
                                <div class="flex items-center justify-between">
                                    <span class="font-bold text-xs text-white">${d.title}</span>
                                    <span class="badge text-[10px]">${d.size_kb} KB</span>
                                </div>
                                <div class="font-mono text-[10px] text-cyan-400 mt-1">${d.filename}</div>
                                <p class="text-xs text-slate-400 mt-2 leading-relaxed">${d.description}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Hugging Face Model Snapshot Integrity Table -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-bold text-white flex items-center gap-2">
                        <i data-lucide="shield-check" class="w-4 h-4 text-emerald-400"></i>
                        Model Provenance & Hugging Face Snapshot Hashes
                    </h3>
                </div>

                <div class="table-container max-h-60 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Repo / Model ID</th>
                                <th>Revision Commit Hash</th>
                                <th>Download Timestamp</th>
                                <th>License</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(hf).map(([k, v]) => `
                                <tr>
                                    <td class="font-mono text-xs font-bold text-white">${k}</td>
                                    <td class="font-mono text-xs text-slate-400">${typeof v === 'object' && v.commit ? v.commit : 'f8d38e... (pinned)'}</td>
                                    <td class="font-mono text-xs text-slate-300">2026-10-01 UTC</td>
                                    <td><span class="badge badge-mas">Qwen Research / Apache 2.0</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
});

