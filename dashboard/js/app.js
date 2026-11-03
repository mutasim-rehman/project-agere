/**
 * Project Agere Dashboard - Core Application Manager
 */

window.App = {
    state: {
        activeTab: 'overview',
        theme: 'dark',
        data: {},
        activeCase: null,
        loading: false
    },

    pages: {},

    registerPage(id, pageModule) {
        this.pages[id] = pageModule;
    },

    async init() {
        console.log("[App] Initializing Project Agere Dashboard...");
        
        // Theme init
        this.initTheme();

        // Bind nav click events
        document.querySelectorAll('.nav-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = el.getAttribute('data-tab');
                this.navigate(tab);
            });
        });

        // Theme toggle button
        const themeBtn = document.getElementById('theme-toggle');
        if (themeBtn) {
            themeBtn.addEventListener('click', () => this.toggleTheme());
        }

        // Handle URL hash navigation
        window.addEventListener('hashchange', () => this.handleHashChange());

        // Preload core aggregates
        await this.loadCoreData();

        // Navigate to hash or default 'overview'
        const initialTab = window.location.hash.replace('#', '') || 'overview';
        this.navigate(initialTab);
    },

    initTheme() {
        const savedTheme = localStorage.getItem('agere_theme') || 'dark';
        this.setTheme(savedTheme);
    },

    toggleTheme() {
        const newTheme = this.state.theme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    },

    setTheme(theme) {
        this.state.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('agere_theme', theme);
        
        const icon = document.querySelector('#theme-toggle i');
        if (icon) {
            icon.setAttribute('data-lucide', theme === 'dark' ? 'sun' : 'moon');
            if (window.lucide) lucide.createIcons();
        }
    },

    async loadCoreData() {
        try {
            const res = await fetch('data/derived_aggregates.json');
            this.state.data.aggregates = await res.json();
            console.log("[App] Core aggregates loaded successfully.");
        } catch (err) {
            console.error("[App] Failed to load core aggregates:", err);
        }
    },

    async fetchJson(path) {
        if (this.state.data[path]) {
            return this.state.data[path];
        }
        try {
            const res = await fetch(path);
            const json = await res.json();
            this.state.data[path] = json;
            return json;
        } catch (err) {
            console.error(`[App] Error fetching ${path}:`, err);
            return null;
        }
    },

    handleHashChange() {
        const hash = window.location.hash.replace('#', '');
        const tab = hash.split('?')[0] || 'overview';
        if (tab !== this.state.activeTab) {
            this.navigate(tab);
        }
    },

    async navigate(tabId) {
        if (!this.pages[tabId]) {
            console.warn(`[App] Page '${tabId}' not registered, falling back to overview.`);
            tabId = 'overview';
        }

        this.state.activeTab = tabId;
        window.location.hash = tabId;

        // Update active nav styling
        document.querySelectorAll('.nav-item').forEach(el => {
            if (el.getAttribute('data-tab') === tabId) {
                el.classList.add('active');
            } else {
                el.classList.remove('active');
            }
        });

        const titleMap = {
            overview: 'Executive Overview',
            comparison: 'MAS vs SAS Head-to-Head Comparison',
            cases: 'Case & Outcome Explorer (1,728 Instances)',
            statistics: 'Inferential Statistics & Hypothesis Testing (126 Tests)',
            pipeline: 'Pipeline Stages & Token Cost Analysis',
            hardware: 'Hardware RSS Telemetry & Swap Audit',
            runs: 'Experiment Runs & Historical Logs',
            datasets: 'Datasets, Financial Reports & Splits',
            models: 'Model Architectures & Quantization Configs',
            provenance: 'Research Provenance, Decision Log & Audit'
        };

        const pageTitle = document.getElementById('page-title');
        if (pageTitle) {
            pageTitle.innerText = titleMap[tabId] || 'Project Agere';
        }

        const container = document.getElementById('content-container');
        container.innerHTML = `
            <div class="flex items-center justify-center p-24 text-slate-500">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
            </div>
        `;

        try {
            await this.pages[tabId].render(container, this);
            if (window.lucide) {
                lucide.createIcons();
            }
        } catch (err) {
            console.error(`[App] Error rendering page ${tabId}:`, err);
            container.innerHTML = `
                <div class="p-6 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
                    <h3 class="font-bold text-sm">Failed to render ${tabId}</h3>
                    <p class="text-xs mt-1 font-mono">${err.message}</p>
                </div>
            `;
        }
    },

    openModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.add('active');
    },

    closeModal(id) {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
    },

    showFigure(src, title, caption) {
        document.getElementById('figure-modal-title').innerText = title || 'Publication Graphic';
        document.getElementById('figure-modal-caption').innerText = caption || '';
        document.getElementById('figure-modal-img').src = src;
        this.openModal('figure-modal');
    },

    showCaseDetails(caseObj) {
        const titleEl = document.getElementById('modal-case-title');
        const subEl = document.getElementById('modal-case-subtitle');
        const bodyEl = document.getElementById('modal-case-body');

        titleEl.innerText = `Case: ${caseObj.case_id}`;
        subEl.innerText = `${caseObj.company} • ${caseObj.report} • ${caseObj.arm.toUpperCase()} (${caseObj.profile})`;

        const repBadge = caseObj.reported_correct ? '<span class="badge badge-correct">Reported Correct</span>' : (caseObj.reported_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Reported Wrong</span>');
        const rawBadge = caseObj.raw_correct ? '<span class="badge badge-correct">Raw Correct</span>' : (caseObj.raw_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Raw Wrong</span>');

        bodyEl.innerHTML = `
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-[var(--bg-surface-elevated)] p-4 rounded-lg">
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Reported Match</div>
                    <div class="mt-1">${repBadge}</div>
                </div>
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Raw Match</div>
                    <div class="mt-1">${rawBadge}</div>
                </div>
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Tokens Generated</div>
                    <div class="text-sm font-bold font-mono text-white mt-1">${caseObj.generated_tokens ?? 'N/A'}</div>
                </div>
                <div>
                    <div class="text-[10px] text-slate-400 uppercase font-mono">Inference Time</div>
                    <div class="text-sm font-bold font-mono text-white mt-1">${caseObj.inference_seconds ? caseObj.inference_seconds.toFixed(2) + 's' : 'N/A'}</div>
                </div>
            </div>

            <div class="card p-4">
                <div class="text-xs font-bold text-slate-400 uppercase font-mono mb-2">Dual Verification Audit</div>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Execution Valid: <span class="font-bold text-white">${caseObj.execution_valid ? 'True' : 'False'}</span> • 
                    Repair Attempted: <span class="font-bold text-white">${caseObj.repair_attempted ? 'Yes' : 'No'}</span> • 
                    Evidence Annotated Complete: <span class="font-bold text-white">${caseObj.annotated_evidence_complete ? 'Yes' : 'No'}</span>
                </p>
            </div>

            <div class="card p-4">
                <div class="text-xs font-bold text-slate-400 uppercase font-mono mb-2">Protocol Reference</div>
                <p class="text-xs text-slate-400 leading-relaxed">
                    Case is part of the 16 GB FinQA Evaluation cohort under 12.8 GB host-adjusted process-tree RSS cap. Denominator is 160 instances.
                </p>
            </div>
        `;

        this.openModal('case-modal');
    },

    showReproduceModal() {
        const bodyEl = document.getElementById('modal-case-body');
        document.getElementById('modal-case-title').innerText = "Reproduction & Offline Commands";
        document.getElementById('modal-case-subtitle').innerText = "Run verified pipeline without external SSD";

        bodyEl.innerHTML = `
            <div class="space-y-4">
                <div class="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-lg">
                    <h4 class="font-bold text-emerald-400 text-sm">Standalone Re-analysis (Zero Setup)</h4>
                    <p class="text-xs text-slate-300 mt-1">
                        All statistical evaluation tables, p-values, bootstrap intervals, and figures can be verified without model downloads or GPUs.
                    </p>
                </div>

                <div class="card p-3">
                    <div class="text-xs font-mono text-slate-400 mb-2">1. Verify and unpack SSD Evidence Archives:</div>
                    <pre class="bg-slate-950 p-2 rounded text-xs font-mono text-emerald-400 overflow-x-auto">python dashboard_handoff/restore_evidence.py</pre>
                </div>

                <div class="card p-3">
                    <div class="text-xs font-mono text-slate-400 mb-2">2. Recompute Statistical Hypothesis Tests:</div>
                    <pre class="bg-slate-950 p-2 rounded text-xs font-mono text-cyan-400 overflow-x-auto">python scripts/reporting/paper_statistical_tests.py</pre>
                </div>

                <div class="card p-3">
                    <div class="text-xs font-mono text-slate-400 mb-2">3. Regenerate High-Res Publication Figures:</div>
                    <pre class="bg-slate-950 p-2 rounded text-xs font-mono text-cyan-400 overflow-x-auto">python scripts/reporting/paper_figures.py</pre>
                </div>
            </div>
        `;
        this.openModal('case-modal');
    },

    exportData() {
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.state.data, null, 2));
        const dlAnchorElem = document.createElement('a');
        dlAnchorElem.setAttribute("href", dataStr);
        dlAnchorElem.setAttribute("download", `agere_${this.state.activeTab}_data.json`);
        dlAnchorElem.click();
    }
};

