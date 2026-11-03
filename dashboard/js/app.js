/**
 * Project Agere Dashboard - Core Application Manager (Academic Light Theme)
 */

window.App = {
    state: {
        activeTab: 'overview',
        theme: 'light',
        data: {},
        activeCase: null,
        loading: false
    },

    pages: {},

    registerPage(id, pageModule) {
        this.pages[id] = pageModule;
    },

    async init() {
        console.log("[App] Initializing Project Agere Dashboard (Academic Light Theme)...");
        
        // Force clean light theme
        this.setTheme('light');

        // Bind nav click events
        document.querySelectorAll('.nav-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                const tab = el.getAttribute('data-tab');
                this.navigate(tab);
            });
        });

        // Theme toggle button (if present)
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

    setTheme(theme) {
        this.state.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('agere_theme', theme);
    },

    toggleTheme() {
        const newTheme = this.state.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
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
            <div class="flex items-center justify-center p-24 text-[#64748B]">
                <div class="animate-spin rounded-full h-7 w-7 border-2 border-[#2563EB] border-t-transparent"></div>
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
                <div class="p-6 bg-[#FEF2F2] border border-[#FECACA] rounded-lg text-[#DC2626]">
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
        subEl.innerText = `${caseObj.company} • ${caseObj.report} • ${caseObj.arm.toUpperCase()} (${caseObj.profile || caseObj.condition || 'standard'})`;

        const repBadge = caseObj.reported_correct ? '<span class="badge badge-correct">Reported Correct</span>' : (caseObj.reported_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Reported Wrong</span>');
        const rawBadge = caseObj.raw_correct ? '<span class="badge badge-correct">Raw Correct</span>' : (caseObj.raw_outcome === 'withheld' ? '<span class="badge badge-withheld">Withheld</span>' : '<span class="badge badge-wrong">Raw Wrong</span>');

        bodyEl.innerHTML = `
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3 bg-[#F8FAFC] p-4 rounded-lg border border-[#E2E8F0]">
                <div>
                    <div class="text-[10px] text-[#64748B] uppercase font-mono">Reported Answer</div>
                    <div class="mt-1">${repBadge}</div>
                </div>
                <div>
                    <div class="text-[10px] text-[#64748B] uppercase font-mono">Raw Execution Match</div>
                    <div class="mt-1">${rawBadge}</div>
                </div>
                <div>
                    <div class="text-[10px] text-[#64748B] uppercase font-mono">Tokens Generated</div>
                    <div class="text-sm font-bold font-mono text-[#172033] mt-1">${caseObj.generated_tokens ?? 'N/A'}</div>
                </div>
                <div>
                    <div class="text-[10px] text-[#64748B] uppercase font-mono">Inference Time</div>
                    <div class="text-sm font-bold font-mono text-[#172033] mt-1">${caseObj.inference_seconds ? caseObj.inference_seconds.toFixed(2) + 's' : 'N/A'}</div>
                </div>
            </div>

            <div class="card p-4">
                <div class="text-xs font-bold text-[#172033] uppercase font-mono mb-2">Dual Verification Audit</div>
                <p class="text-xs text-[#64748B] leading-relaxed">
                    Execution Valid: <strong class="text-[#172033]">${caseObj.execution_valid ? 'True' : 'False'}</strong> • 
                    Repair Attempted: <strong class="text-[#172033]">${caseObj.repair_attempted ? 'Yes' : 'No'}</strong> • 
                    Evidence Annotated Complete: <strong class="text-[#172033]">${caseObj.annotated_evidence_complete ? 'Yes' : 'No'}</strong>
                </p>
            </div>

            <div class="card p-4">
                <div class="text-xs font-bold text-[#172033] uppercase font-mono mb-2">Protocol Reference</div>
                <p class="text-xs text-[#64748B] leading-relaxed">
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
                <div class="bg-[#EFF6FF] border border-[#BFDBFE] p-4 rounded-lg">
                    <h4 class="font-bold text-[#2563EB] text-sm">Standalone Re-analysis (Zero Setup)</h4>
                    <p class="text-xs text-[#1E40AF] mt-1">
                        All statistical evaluation tables, p-values, bootstrap intervals, and figures can be verified without model downloads or GPUs.
                    </p>
                </div>

                <div class="card p-3">
                    <div class="text-xs font-mono text-[#64748B] mb-1">1. Verify and unpack SSD Evidence Archives:</div>
                    <pre class="bg-[#F8FAFC] p-2.5 rounded text-xs font-mono text-[#2563EB] border border-[#E2E8F0] overflow-x-auto">python dashboard_handoff/restore_evidence.py</pre>
                </div>

                <div class="card p-3">
                    <div class="text-xs font-mono text-[#64748B] mb-1">2. Recompute Statistical Hypothesis Tests:</div>
                    <pre class="bg-[#F8FAFC] p-2.5 rounded text-xs font-mono text-[#2563EB] border border-[#E2E8F0] overflow-x-auto">python scripts/reporting/paper_statistical_tests.py</pre>
                </div>

                <div class="card p-3">
                    <div class="text-xs font-mono text-[#64748B] mb-1">3. Regenerate High-Res Publication Figures:</div>
                    <pre class="bg-[#F8FAFC] p-2.5 rounded text-xs font-mono text-[#2563EB] border border-[#E2E8F0] overflow-x-auto">python scripts/reporting/paper_figures.py</pre>
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
