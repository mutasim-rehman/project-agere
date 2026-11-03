/**
 * Models & Configurations Page - Visual Research Dashboard
 */

window.App.registerPage('models', {
    async render(container, app) {
        const models = await app.fetchJson('data/model_architectures.json') || [];

        container.innerHTML = `
            <!-- Tier Configuration Comparison Cards Strip -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- 8 GB Tier -->
                <div class="stat-card border-t-4 border-t-[#64748B]">
                    <div class="stat-card-label">
                        <span>Tier 1: 8 GB Hardware</span>
                        <span class="badge badge-sas">Adapted</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">6.4 GB Cap</div>
                    <div class="stat-card-meta">SAS: 7B Q4_K_M • MAS: 0.5B+1.5B+3B</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#64748B]" style="width: 50%;"></div>
                    </div>
                </div>

                <!-- 16 GB Tier (Primary) -->
                <div class="stat-card border-t-4 border-t-[#2563EB] bg-[#EFF6FF]">
                    <div class="stat-card-label">
                        <span>Tier 2: 16 GB Hardware</span>
                        <span class="badge badge-mas">Primary Study</span>
                    </div>
                    <div class="stat-card-value text-[#2563EB]">12.8 GB Cap</div>
                    <div class="stat-card-meta">SAS: 14B Q4_K_M • MAS: 1.5B+7B+3B</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#2563EB]" style="width: 80%;"></div>
                    </div>
                </div>

                <!-- 32 GB Tier -->
                <div class="stat-card border-t-4 border-t-[#94A3B8]">
                    <div class="stat-card-label">
                        <span>Tier 3: 32 GB Server</span>
                        <span class="badge badge-withheld">Projected</span>
                    </div>
                    <div class="stat-card-value text-[#172033]">25.6 GB Cap</div>
                    <div class="stat-card-meta">SAS: 32B Q4_K_M • MAS: 3B+14B+7B</div>
                    <div class="progress-track">
                        <div class="progress-fill bg-[#94A3B8]" style="width: 100%;"></div>
                    </div>
                </div>
            </div>

            <!-- Visual Parameter & Memory Chart -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Qwen2.5 Memory Footprint: Native FP16 vs GGUF Q4_K_M</h3>
                        <p class="text-xs text-[#64748B]">RAM footprint in Gigabytes across parameter scales</p>
                    </div>
                    <span class="badge badge-mas">Quantization Savings</span>
                </div>
                <div class="pt-4">
                    <div class="w-full h-64">
                        <canvas id="models-footprint-chart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Model Architectural Specifications Table -->
            <div class="card">
                <div class="card-header-clean">
                    <div>
                        <h3 class="text-sm font-bold text-[#172033]">Qwen2.5 Architectural Specifications</h3>
                        <p class="text-xs text-[#64748B]">Hidden dimensions, attention heads, layers, and context length</p>
                    </div>
                </div>

                <div class="table-container max-h-72 overflow-y-auto mt-4">
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

        this.renderChart();
    },

    renderChart() {
        const ctx = document.getElementById('models-footprint-chart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['0.5B', '1.5B', '3B', '7B', '14B', '32B'],
                datasets: [
                    {
                        label: 'Native FP16 RAM (GB)',
                        data: [1.2, 3.4, 6.8, 15.2, 29.8, 68.0],
                        backgroundColor: '#2563EB',
                        borderRadius: 4
                    },
                    {
                        label: 'GGUF Q4_K_M RAM (GB)',
                        data: [0.4, 1.1, 2.3, 4.8, 9.4, 20.2],
                        backgroundColor: '#64748B',
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#64748B', font: { size: 11, family: 'Inter' }, boxWidth: 12 }
                    },
                    tooltip: {
                        backgroundColor: '#172033',
                        titleColor: '#FFFFFF',
                        bodyColor: '#F8FAFC',
                        padding: 10
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#64748B', font: { size: 11, family: 'Inter' } }
                    },
                    y: {
                        grid: { color: '#E9EEF5' },
                        ticks: { color: '#64748B', callback: v => v + ' GB', font: { size: 11, family: 'JetBrains Mono' } }
                    }
                }
            }
        });
    }
});