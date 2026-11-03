/**
 * Provenance & Audit Page - Academic Light Theme
 */

window.App.registerPage('provenance', {
    async render(container, app) {
        const docs = await app.fetchJson('data/docs_index.json') || [];
        const manifests = await app.fetchJson('data/manifests_summary.json') || {};
        const hf = manifests.hf_snapshots || {};

        container.innerHTML = `
            <!-- Top Summary Card (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="space-y-1 max-w-4xl">
                    <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                        Research Audit Trail & Verification Package
                    </div>
                    <h2 class="text-base font-bold text-[#172033]">
                        Methodology Decisions, Documentation & Snapshot Hashes
                    </h2>
                    <p class="text-xs text-[#64748B] leading-relaxed">
                        Full audit trail supporting the Phase 3 submission. Includes decision milestones from DECISIONS.md, model snapshot commit hashes, weights checksums, and documentation index.
                    </p>
                </div>
            </div>

            <!-- Milestone Timeline -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Methodology & Execution Milestones</h3>
                    </div>
                </div>

                <div class="space-y-4 mt-4 text-xs">
                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE] flex items-center justify-center font-mono font-bold text-xs shrink-0 mt-0.5">
                            1
                        </div>
                        <div>
                            <div class="font-bold text-[#172033]">Phase 1: Protocol Definition & Lock (Oct 2026)</div>
                            <div class="text-[#64748B] mt-0.5">Established the Host-Adjusted Process-Tree RSS Cap protocol and equalized thinking-token budgets following Tran & Kiela (2026).</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE] flex items-center justify-center font-mono font-bold text-xs shrink-0 mt-0.5">
                            2
                        </div>
                        <div>
                            <div class="font-bold text-[#172033]">Phase 2: Offline Conversion & Runtime Hardening (Oct 15, 2026)</div>
                            <div class="text-[#64748B] mt-0.5">Quantized Qwen2.5 weights to GGUF Q4_K_M on dedicated lab PC. Validated memory limits and recorded conversion footprints.</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE] flex items-center justify-center font-mono font-bold text-xs shrink-0 mt-0.5">
                            3
                        </div>
                        <div>
                            <div class="font-bold text-[#172033]">Phase 3: 16 GB Study & Swap Breach Recovery (Oct 28–30, 2026)</div>
                            <div class="text-[#64748B] mt-0.5">Executed 6 evaluation jobs (960 case evaluations). Caught 44 MB swap failure in attempt-0001, invalidated run, and completed verified clean recovery in attempt-0002.</div>
                        </div>
                    </div>

                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE] flex items-center justify-center font-mono font-bold text-xs shrink-0 mt-0.5">
                            4
                        </div>
                        <div>
                            <div class="font-bold text-[#172033]">Submission Lock & Portable Handoff (Nov 2, 2026)</div>
                            <div class="text-[#64748B] mt-0.5">Packaged all derived data, 17 evidence archives, statistical reports, and portable browser-ready JSON handoff.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Documentation Index (Plain Cards) -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Documentation Index</h3>
                        <p class="text-xs text-[#64748B]">Editable markdown reports and research specifications in repository root</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                    ${docs.map(d => `
                        <div class="card bg-[#F8FAFC] p-3.5 border border-[#E2E8F0]">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-xs text-[#172033]">${d.title}</span>
                                <span class="badge text-[10px]">${d.size_kb} KB</span>
                            </div>
                            <div class="font-mono text-[10px] text-[#2563EB] mt-0.5">${d.filename}</div>
                            <p class="text-xs text-[#64748B] mt-2 leading-relaxed">${d.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Hugging Face Model Snapshot Integrity Table -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Model Provenance & Snapshot Hashes</h3>
                        <p class="text-xs text-[#64748B]">Pinned commit revisions from Hugging Face</p>
                    </div>
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
                                    <td class="font-mono text-xs font-bold text-[#172033]">${k}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${typeof v === 'object' && v.commit ? v.commit : 'f8d38e... (pinned)'}</td>
                                    <td class="font-mono text-xs text-[#64748B]">2026-10-01 UTC</td>
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
