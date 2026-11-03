/**
 * Models & Configurations Page - Minimal, Plain, Publication-Grade
 */

window.App.registerPage('models', {
    async render(container, app) {
        const models = await app.fetchJson('data/model_architectures.json') || [];

        container.innerHTML = `
            <!-- Top Summary Card (Plain, Structured) -->
            <div class="card p-5 border border-slate-700 bg-slate-900/40">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
                    <div>
                        <div class="text-xs uppercase tracking-wider font-mono text-slate-400">Architecture Specification</div>
                        <h2 class="text-base font-semibold text-white mt-1">
                            Model Ecosystem & Physical Tier Resource Limits
                        </h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-4xl leading-relaxed">
                            To ensure strict fairness across parameter scales, all models originate from the single unified Qwen2.5-Instruct architecture. Monolithic baselines use GGUF Q4_K_M post-training quantization, while multi-agent teams utilize native FP16/BF16 weights.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Tier Configuration Comparison Cards (Plain, Minimal) -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- 8 GB Tier -->
                <div class="card p-5">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-400 font-mono">Tier 1</span>
                        <span class="badge badge-sas">8 GB RAM</span>
                    </div>
                    <div class="font-semibold text-base text-white mt-2">8 GB Tier (Nominal)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-slate-300">
                            <span>Process RSS Cap:</span>
                            <span class="text-white font-semibold">6.4 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-400">
                            <span>OS Reserve (20%):</span>
                            <span>1.6 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Model:</span>
                            <span class="text-white">Qwen2.5-7B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Team:</span>
                            <span class="text-white">0.5B + 1.5B + 3B (F16)</span>
                        </div>
                    </div>
                </div>

                <!-- 16 GB Tier (Primary) -->
                <div class="card p-5 border-slate-500">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-300 font-mono">Tier 2 (Primary)</span>
                        <span class="badge badge-mas">Completed</span>
                    </div>
                    <div class="font-semibold text-base text-white mt-2">16 GB Tier (Analyst RAM)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-slate-300">
                            <span>Process RSS Cap:</span>
                            <span class="text-white font-semibold">12.8 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-400">
                            <span>OS Reserve (20%):</span>
                            <span>3.2 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Model:</span>
                            <span class="text-white font-semibold">Qwen2.5-14B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Team:</span>
                            <span class="text-white">1.5B + 7B + 3B (F16)</span>
                        </div>
                    </div>
                </div>

                <!-- 32 GB Tier -->
                <div class="card p-5">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-semibold text-slate-400 font-mono">Tier 3</span>
                        <span class="badge badge-withheld">Unevaluated</span>
                    </div>
                    <div class="font-semibold text-base text-white mt-2">32 GB Tier (Server RAM)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-slate-300">
                            <span>Process RSS Cap:</span>
                            <span class="text-white">25.6 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-400">
                            <span>OS Reserve (20%):</span>
                            <span>6.4 GB</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>SAS Model:</span>
                            <span class="text-white">Qwen2.5-32B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span>MAS Team:</span>
                            <span class="text-white">3B + 14B + 7B (F16)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Model Architectural Specifications Table -->
            <div class="card">
                <div class="pb-3 border-b border-[var(--border-color)]">
                    <h3 class="text-sm font-semibold text-white">Qwen2.5 Model Specifications</h3>
                    <p class="text-xs text-slate-400">Parameters, hidden dimensions, attention heads, and context window lengths</p>
                </div>

                <div class="table-container max-h-80 overflow-y-auto mt-4">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Model Identifier</th>
                                <th>Architecture</th>
                                <th>Hidden Size</th>
                                <th>Layers</th>
                                <th>Attn Heads</th>
                                <th>KV Heads</th>
                                <th>Vocab Size</th>
                                <th>Context Length</th>
                                <th>Precision</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${models.map(m => `
                                <tr>
                                    <td class="font-mono text-xs font-semibold text-white">${m.model_id}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.architecture}</td>
                                    <td class="font-mono text-xs text-white">${m.hidden_size}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.num_hidden_layers}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.num_attention_heads}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.num_key_value_heads}</td>
                                    <td class="font-mono text-xs text-slate-400">${m.vocab_size?.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-white font-medium">${m.max_position_embeddings?.toLocaleString()}</td>
                                    <td><span class="badge badge-sas font-mono">${m.torch_dtype}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
});
