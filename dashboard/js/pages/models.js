/**
 * Models & Configurations Page
 */

window.App.registerPage('models', {
    async render(container, app) {
        const models = await app.fetchJson('data/model_architectures.json') || [];
        const configs = await app.fetchJson('data/configs_summary.json') || {};
        const tiers = configs.tiers || {};

        container.innerHTML = `
            <!-- Top Header -->
            <div class="card bg-gradient-to-r from-slate-900 to-purple-950/20 border-purple-500/30 p-5">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="badge badge-sas">Model Family</span>
                            <span class="text-xs text-slate-400 font-mono">Qwen2.5-Instruct Ecosystem</span>
                        </div>
                        <h2 class="text-lg font-bold text-white mt-1">
                            Model Specifications, Tier Allocations & Quantization Recipes
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
                            To ensure strict fairness across parameter scales, all models originate from the single unified Qwen2.5-Instruct architecture. Monolithic baselines use GGUF Q4_K_M post-training quantization, while multi-agent teams utilize native FP16/BF16 weights.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Tier Configuration Comparison Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- 8 GB Tier -->
                <div class="card p-5 border-l-4 border-slate-500">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-slate-400 uppercase font-mono">Tier 1</span>
                        <span class="badge">8 GB Physical RAM</span>
                    </div>
                    <div class="font-bold text-lg text-white mt-2">8 GB Tier (Nominal)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-slate-300">
                            <span>Process RSS Cap:</span>
                            <span class="text-emerald-400 font-bold">6.4 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>OS & Background Reserve:</span>
                            <span class="text-slate-400">1.6 GB (20%)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Monolith:</span>
                            <span class="text-purple-400 font-bold">7B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Team:</span>
                            <span class="text-emerald-400">0.5B + 1.5B + 3B (F16)</span>
                        </div>
                    </div>
                </div>

                <!-- 16 GB Tier (Primary) -->
                <div class="card p-5 border-l-4 border-emerald-500 bg-emerald-950/10">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-emerald-400 uppercase font-mono">Tier 2 (Primary)</span>
                        <span class="badge badge-mas">Completed Study</span>
                    </div>
                    <div class="font-bold text-lg text-white mt-2">16 GB Tier (Analyst RAM)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-slate-300">
                            <span>Process RSS Cap:</span>
                            <span class="text-emerald-400 font-bold">12.8 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>OS & Background Reserve:</span>
                            <span class="text-slate-400">3.2 GB (20%)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Monolith:</span>
                            <span class="text-purple-400 font-bold">14B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Team:</span>
                            <span class="text-emerald-400">1.5B + 7B + 3B (F16)</span>
                        </div>
                    </div>
                </div>

                <!-- 32 GB Tier -->
                <div class="card p-5 border-l-4 border-slate-700">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-slate-500 uppercase font-mono">Tier 3</span>
                        <span class="badge badge-withheld">Unevaluated</span>
                    </div>
                    <div class="font-bold text-lg text-white mt-2">32 GB Tier (Server RAM)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-slate-300">
                            <span>Process RSS Cap:</span>
                            <span class="text-slate-400 font-bold">25.6 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>OS & Background Reserve:</span>
                            <span class="text-slate-400">6.4 GB (20%)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Monolith:</span>
                            <span class="text-purple-400 font-bold">32B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Team:</span>
                            <span class="text-slate-400">3B + 14B + 7B (F16)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Model Architectural Specifications Table -->
            <div class="card">
                <div class="flex items-center justify-between pb-3 border-b border-[var(--border-color)]">
                    <div>
                        <h3 class="text-sm font-bold text-white flex items-center gap-2">
                            <i data-lucide="cpu" class="w-4 h-4 text-cyan-400"></i>
                            Qwen2.5 Architectural Parameters (Extracted from Weight Configs)
                        </h3>
                        <p class="text-xs text-slate-400 mt-0.5">Parameters, hidden dimensions, attention heads, and context window lengths</p>
                    </div>
                </div>

                <div class="table-container max-h-80 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Model Name</th>
                                <th>Architecture</th>
                                <th>Hidden Size</th>
                                <th>Layers</th>
                                <th>Attn Heads</th>
                                <th>KV Heads</th>
                                <th>Vocab Size</th>
                                <th>Max Context</th>
                                <th>Precision</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${models.map(m => `
                                <tr>
                                    <td class="font-mono text-xs font-bold text-white">${m.model_id}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.architecture}</td>
                                    <td class="font-mono text-xs text-cyan-400">${m.hidden_size}</td>
                                    <td class="font-mono text-xs">${m.num_hidden_layers}</td>
                                    <td class="font-mono text-xs">${m.num_attention_heads}</td>
                                    <td class="font-mono text-xs">${m.num_key_value_heads}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.vocab_size?.toLocaleString()}</td>
                                    <td class="font-mono text-xs font-bold text-emerald-400">${m.max_position_embeddings?.toLocaleString()}</td>
                                    <td><span class="badge badge-mas font-mono">${m.torch_dtype}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
});

