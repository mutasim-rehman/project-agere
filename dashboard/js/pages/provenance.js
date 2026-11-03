/**
 * Provenance: milestones, documentation and pinned model revisions.
 */

window.App.registerPage('provenance', {
    async render(container, app) {
        const docs = (await app.fetchJson('data/docs_index.json')) || [];
        const manifests = (await app.fetchJson('data/manifests_summary.json')) || {};
        const archive = (await app.fetchJson('data/archive_stats.json')) || {};
        const artifacts = (manifests.hf_snapshots || {}).artifacts || [];

        const repos = {};
        artifacts.forEach(a => {
            const r = repos[a.repo_id] = repos[a.repo_id] || { repo: a.repo_id, revision: a.revision, files: 0, bytes: 0 };
            r.files++;
            r.bytes += a.size_bytes || 0;
        });
        const repoList = Object.values(repos).sort((a, b) => a.repo.localeCompare(b.repo, undefined, { numeric: true }));

        const docIcon = name => /PAPER/.test(name) ? 'file-text' : /STAT|REPORT/.test(name) ? 'bar-chart-3' : /METHOD|PROTOCOL/.test(name) ? 'flask-conical' : /DECISION/.test(name) ? 'git-commit' : 'book-open';

        const milestones = [
            ['Phase 1 · Protocol lock', 'Oct 2026', 'Defined the RAM parity protocol (RUPP) and equalized thinking-token budgets.'],
            ['Phase 2 · Offline conversion', 'Oct 2026', 'Converted and quantized Qwen2.5 weights from snapshots pinned to exact revisions, recording peak RSS for every operation.'],
            ['8 GB development', 'Oct 2026', '15 configurations on 101 questions, with adapter training and critic experiments.'],
            ['16 GB study', '28–30 Oct 2026', '6 jobs, 960 outputs. Two swap breaches invalidated and recovered under memory.swap.max = 0.', true],
            ['Submission lock & handoff', '2 Nov 2026', `Derived data, statistical reports and ${UI.num(archive.total_files || 0)} evidence files packaged for offline re-analysis.`]
        ];

        container.innerHTML = `
            ${UI.hero({
                eyebrow: 'Audit trail',
                title: 'Every number traces back to a hashed file',
                sub: 'Model revisions are pinned, datasets are checksummed, and failed attempts stay in the record instead of being quietly dropped.'
            })}

            <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
                ${UI.kpi({ label: 'Pinned model repos', value: repoList.length, foot: `${artifacts.length} hashed files`, tone: 'mas', icon: 'pin', i: 1 })}
                ${UI.kpi({ label: 'Evidence files', value: archive.total_files || 0, foot: `${archive.total_mb || 0} MB on SSD`, tone: 'sas', icon: 'hard-drive', i: 2 })}
                ${UI.kpi({ label: 'Research documents', value: docs.length, foot: `${docs.reduce((a, d) => a + (d.size_kb || 0), 0).toFixed(0)} KB of write-ups`, tone: 'correct', icon: 'files', i: 3 })}
                ${UI.kpi({ label: 'Invalidated attempts kept', value: 2, foot: 'Swap-breach runs retained in provenance', tone: 'wrong', icon: 'archive-restore', i: 4 })}
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-5 gap-6">
                ${UI.card({
                    cls: 'xl:col-span-2', i: 5,
                    title: 'Milestones',
                    body: `
                        <div class="tl">
                            ${milestones.map(([t, d, body, alert], i) => `
                                <div class="tl-item reveal ${alert ? 'alert' : ''}" style="--i:${6 + i}">
                                    <div class="tl-dot"></div>
                                    <div class="flex items-baseline justify-between gap-2"><div class="text-sm font-semibold">${t}</div><div class="text-[11px] font-mono t-muted shrink-0">${d}</div></div>
                                    <div class="text-xs t-secondary mt-0.5 leading-relaxed">${body}</div>
                                </div>`).join('')}
                        </div>`
                })}
                ${UI.card({
                    cls: 'xl:col-span-3', i: 6,
                    title: 'Documentation',
                    sub: 'Markdown and PDF reports in the repository root',
                    body: `
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                            ${docs.map(d => `
                                <div class="p-3.5 rounded-xl flex gap-3 card-hover" style="background:var(--bg-surface-elevated); border:1px solid var(--border-light); transition: transform .3s var(--ease-out)">
                                    <div class="w-9 h-9 rounded-lg grid place-items-center shrink-0" style="background:rgba(var(--color-mas-rgb),.12); color:var(--color-mas)"><i data-lucide="${docIcon(d.filename)}" class="w-4 h-4"></i></div>
                                    <div class="min-w-0">
                                        <div class="flex items-center gap-2"><span class="font-semibold text-sm truncate">${UI.esc(d.title)}</span><span class="badge py-0 shrink-0">${d.size_kb} KB</span></div>
                                        <div class="font-mono text-[10px] t-muted truncate">${UI.esc(d.filename)}</div>
                                        <p class="text-xs t-secondary mt-1 leading-relaxed">${UI.esc(d.description)}</p>
                                    </div>
                                </div>`).join('')}
                        </div>`
                })}
            </div>

            ${UI.disclosure({
                i: 7,
                title: 'Pinned Hugging Face revisions',
                meta: `${repoList.length} repositories`,
                open: true,
                body: `
                    <div class="table-container">
                        <table class="data-table">
                            <thead><tr><th>Repository</th><th>Revision</th><th class="text-right">Files hashed</th><th class="text-right">Metadata size</th></tr></thead>
                            <tbody>
                                ${repoList.map(r => `
                                    <tr>
                                        <td class="font-mono text-xs font-semibold">${UI.esc(r.repo)}</td>
                                        <td class="font-mono text-xs t-secondary">${UI.esc(r.revision)}</td>
                                        <td class="font-mono text-xs text-right">${r.files}</td>
                                        <td class="font-mono text-xs text-right t-muted">${(r.bytes / 1024).toFixed(1)} KB</td>
                                    </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>`
            })}
        `;
    }
});
