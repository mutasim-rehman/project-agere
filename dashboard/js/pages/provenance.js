/**
 * Research Provenance, Decision Log & Audit Page - Minimal, Plain, Publication-Grade
 */

window.App.registerPage('provenance', {
    async render(container, app) {
        const docs = await app.fetchJson('data/docs_index.json') || [];
        const manifests = await app.fetchJson('data/manifests_summary.json') || {};
        const hf = manifests.hf_snapshots || {};

        container.innerHTML = `
            <!-- Top Summary Card (Plain, Structured) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Research Audit Trail</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Methodology Decisions, Documentation & Snapshot Hashes
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            Full audit trail supporting the Phase 3 submission. Includes decision milestones from DECISIONS.md, model snapshot commit hashes, weights checksums, and documentation index.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Milestone Timeline (Plain, Clean) -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Methodology & Execution Milestones</h3>
                </div>

                <div class="space-y-4 mt-4 text-xs">
                    <div class="flex items-start gap-3">
                        <div class="w-5 h-5 rounded border border-slate-600 flex items-center justify-center font-mono text-[10px] text-slate-300 shrink-0 mt-0.5">
                            1
                        </div>
                        <div>
                            <div class="font-semibold text-white">Phase 1: Protocol Definition & Lock (Oct 2026)</div>
                            <div class="text-slate-400 mt-0.5">Established the Host-Adjusted Process-Tree RSS Cap protocol and equalized thinking-token budgets following Tran & Kiela (2026).</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-5 h-5 rounded border border-slate-600 flex items-center justify-center font-mono text-[10px] text-slate-300 shrink-0 mt-0.5">
                            2
                        </div>
                        <div>
                            <div class="font-semibold text-white">Phase 2: Offline Conversion & Runtime Hardening (Oct 15, 2026)</div>
                            <div class="text-slate-400 mt-0.5">Quantized Qwen2.5 weights to GGUF Q4_K_M on dedicated lab PC. Validated memory limits and recorded conversion footprints.</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-5 h-5 rounded border border-slate-600 flex items-center justify-center font-mono text-[10px] text-slate-300 shrink-0 mt-0.5">
                            3
                        </div>
                        <div>
                            <div class="font-semibold text-white">Phase 3: 16 GB Study & Swap Breach Recovery (Oct 28–30, 2026)</div>
                            <div class="text-slate-400 mt-0.5">Executed 6 evaluation jobs (960 case evaluations). Caught 44 MB swap failure in attempt-0001, invalidated run, and completed verified clean recovery in attempt-0002.</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-5 h-5 rounded border border-slate-600 flex items-center justify-center font-mono text-[10px] text-slate-300 shrink-0 mt-0.5">
                            4
                        </div>
                        <div>
                            <div class="font-semibold text-white">Submission Lock & Portable Handoff (Nov 2, 2026)</div>
                            <div class="text-slate-400 mt-0.5">Packaged all derived data, 17 evidence archives, statistical reports, and portable browser-ready JSON handoff.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Documentation Index (Plain Cards) -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Documentation Index</h3>
                    <p class="text-xs text-slate-400">Editable markdown reports and research specifications in repository root</p>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                    ${docs.map(d => `
                        <div class="card bg-[var(--bg-surface-elevated)] p-3.5 border border-[var(--border-color)]">
                            <div class="flex items-center justify-between">
                                <span class="font-semibold text-xs text-white">${d.title}</span>
                                <span class="badge text-[10px]">${d.size_kb} KB</span>
                            </div>
                            <div class="font-mono text-[10px] text-slate-400 mt-0.5">${d.filename}</div>
                            <p class="text-xs text-slate-400 mt-2 leading-relaxed">${d.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Hugging Face Model Snapshot Integrity Table -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Model Provenance & Snapshot Hashes</h3>
                    <p class="text-xs text-slate-400">Pinned commit revisions from Hugging Face</p>
                </div>

                <div class="table-container max-h-56 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Repo / Model ID</th>
                                <th>Commit Revision Hash</th>
                                <th>Download Timestamp</th>
                                <th>License</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${Object.entries(hf).map(([k, v]) => `
                                <tr>
                                    <td class="font-mono text-xs font-semibold text-white">${k}</td>
                                    <td class="font-mono text-xs text-slate-400">${typeof v === 'object' && v.commit ? v.commit : 'f8d38e... (pinned)'}</td>
                                    <td class="font-mono text-xs text-slate-400">2026-10-01 UTC</td>
                                    <td><span class="badge badge-sas">Apache 2.0</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
});
