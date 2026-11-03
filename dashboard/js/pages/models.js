/**
 * Models & Configurations Page - Academic Light Theme
 */

window.App.registerPage('models', {
    async render(container, app) {
        const models = await app.fetchJson('data/model_architectures.json') || [];

        container.innerHTML = `
            <!-- Top Summary Card (Clean White Surface) -->
            <div class="card bg-white border border-[#E2E8F0]">
                <div class="space-y-1 max-w-4xl">
                    <div class="text-[11px] font-bold uppercase tracking-wider font-mono text-[#2563EB]">
                        Architecture Specification & Serving Recipes
                    </div>
                    <h2 class="text-base font-bold text-[#172033]">
                        Model Ecosystem & Physical Tier Resource Limits
                    </h2>
                    <p class="text-xs text-[#64748B] leading-relaxed">
                        To ensure strict fairness across parameter scales, all models originate from the single unified Qwen2.5-Instruct architecture. Monolithic baselines use GGUF Q4_K_M post-training quantization, while multi-agent teams utilize native FP16/BF16 weights.
                    </p>
                </div>
            </div>

            <!-- Tier Configuration Comparison Cards (Clean White Cards) -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- 8 GB Tier -->
                <div class="card p-5 border-t-4 border-t-[#64748B]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#64748B] font-mono">Tier 1</span>
                        <span class="badge badge-sas">8 GB RAM</span>
                    </div>
                    <div class="font-bold text-base text-[#172033] mt-2">8 GB Tier (Nominal)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-[#172033]">
                            <span>Process RSS Cap:</span>
                            <span class="text-[#2563EB] font-bold">6.4 GB</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>OS Reserve (20%):</span>
                            <span>1.6 GB</span>
                        </div>
                        <div class="flex justify-between text-[#172033]">
                            <span>SAS Model:</span>
                            <span class="font-semibold">Qwen2.5-7B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-[#172033]">
                            <span>MAS Team:</span>
                            <span>0.5B + 1.5B + 3B (FP16)</span>
                        </div>
                    </div>
                </div>

                <!-- 16 GB Tier (Primary) -->
                <div class="card p-5 border-t-4 border-t-[#2563EB] bg-[#F8FAFC]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#2563EB] font-mono">Tier 2 (Primary)</span>
                        <span class="badge badge-mas">Completed Study</span>
                    </div>
                    <div class="font-bold text-base text-[#172033] mt-2">16 GB Tier (Analyst Workstation)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-[#172033]">
                            <span>Process RSS Cap:</span>
                            <span class="text-[#2563EB] font-bold">12.8 GB</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>OS Reserve (20%):</span>
                            <span>3.2 GB</span>
                        </div>
                        <div class="flex justify-between text-[#172033]">
                            <span>SAS Model:</span>
                            <span class="font-semibold">Qwen2.5-14B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-[#172033]">
                            <span>MAS Team:</span>
                            <span>1.5B + 7B + 3B (FP16)</span>
                        </div>
                    </div>
                </div>

                <!-- 32 GB Tier -->
                <div class="card p-5 border-t-4 border-t-[#CBD5E1]">
                    <div class="flex items-center justify-between">
                        <span class="text-xs font-bold text-[#94A3B8] font-mono">Tier 3</span>
                        <span class="badge badge-withheld">Unevaluated</span>
                    </div>
                    <div class="font-bold text-base text-[#172033] mt-2">32 GB Tier (Server RAM)</div>
                    <div class="space-y-2 mt-4 text-xs font-mono">
                        <div class="flex justify-between text-[#172033]">
                            <span>Process RSS Cap:</span>
                            <span>25.6 GB</span>
                        </div>
                        <div class="flex justify-between text-[#64748B]">
                            <span>OS Reserve (20%):</span>
                            <span>6.4 GB</span>
                        </div>
                        <div class="flex justify-between text-[#172033]">
                            <span>SAS Model:</span>
                            <span>Qwen2.5-32B (Q4_K_M)</span>
                        </div>
                        <div class="flex justify-between text-[#172033]">
                            <span>MAS Team:</span>
                            <span>3B + 14B + 7B (FP16)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Model Architectural Specifications Table -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Qwen2.5 Model Specifications</h3>
                        <p class="text-xs text-[#64748B]">Parameters, hidden dimensions, attention heads, and context window lengths</p>
                    </div>
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
                                    <td class="font-mono text-xs font-bold text-[#172033]">${m.model_id}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.architecture}</td>
                                    <td class="font-mono text-xs text-[#2563EB] font-medium">${m.hidden_size}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.num_hidden_layers}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.num_attention_heads}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.num_key_value_heads}</td>
                                    <td class="font-mono text-xs text-[#64748B]">${m.vocab_size?.toLocaleString()}</td>
                                    <td class="font-mono text-xs text-[#172033] font-bold">${m.max_position_embeddings?.toLocaleString()}</td>
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
