/**
 * Project Agere Dashboard - Core Application Manager
 */

window.App = {
    state: {
        activeTab: 'overview',
        theme: 'dark',
        data: {},
        charts: [],
        renderToken: 0
    },

    pages: {},

    pageMeta: {
        overview: ['Overview', '16 GB FinQA study · 160 questions · 50 reports · 36 companies'],
        comparison: ['MAS vs SAS', 'Head-to-head on the same 160 questions, primary profile'],
        cases: ['Case Explorer', '1,728 case outputs across the 16 GB and 8 GB tiers'],
        statistics: ['Statistics', '126 paired hypothesis tests with cluster-robust inference'],
        pipeline: ['Pipeline & Cost', 'Where the time and tokens go, stage by stage'],
        hardware: ['Memory & Swap', 'Process RSS telemetry and the swap-breach audit'],
        runs: ['8 GB Tier & Runs', '15 configurations on 101 questions plus the evidence catalog'],
        datasets: ['Companies & Data', 'Where each architecture wins and loses, by company'],
        models: ['Models & Tiers', 'Qwen2.5 family, quantization and memory budgets'],
        provenance: ['Provenance', 'Milestones, documentation and pinned model revisions']
    },

    registerPage(id, pageModule) {
        this.pages[id] = pageModule;
    },

    async init() {
        this.initTheme();

        document.querySelectorAll('.nav-item').forEach(el => {
            el.addEventListener('click', (e) => {
                e.preventDefault();
                this.navigate(el.getAttribute('data-tab'));
            });
        });

        document.getElementById('theme-toggle')?.addEventListener('click', () => this.toggleTheme());
        window.addEventListener('hashchange', () => this.handleHashChange());
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal('case-modal');
                this.closeModal('figure-modal');
            }
        });

        await this.loadCoreData();

        const initialTab = window.location.hash.replace('#', '').split('?')[0] || 'overview';
        this.navigate(initialTab);
    },

    initTheme() {
        this.setTheme(localStorage.getItem('agere_theme') || 'dark', false);
    },

    toggleTheme() {
        this.setTheme(this.state.theme === 'dark' ? 'light' : 'dark', true);
    },

    setTheme(theme, rerender) {
        this.state.theme = theme;
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('agere_theme', theme);

        const btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.innerHTML = `<i data-lucide="${theme === 'dark' ? 'sun' : 'moon'}" class="w-4 h-4"></i>`;
            if (window.lucide) lucide.createIcons();
        }
        if (window.UI) UI.applyChartDefaults();
        if (rerender && this.pages[this.state.activeTab]) this.navigate(this.state.activeTab, { keepScroll: true });
    },

    async loadCoreData() {
        this.state.data.aggregates = await this.fetchJson('data/derived_aggregates.json');
    },

    async fetchJson(path) {
        if (this.state.data[path]) return this.state.data[path];
        try {
            const res = await fetch(path);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const json = await res.json();
            this.state.data[path] = json;
            return json;
        } catch (err) {
            console.error(`[App] Error fetching ${path}:`, err);
            return null;
        }
    },

    handleHashChange() {
        const tab = window.location.hash.replace('#', '').split('?')[0] || 'overview';
        if (tab !== this.state.activeTab) this.navigate(tab);
    },

    trackChart(chart) {
        this.state.charts.push(chart);
        return chart;
    },

    destroyCharts() {
        this.state.charts.forEach(c => { try { c.destroy(); } catch (_) { /* already gone */ } });
        this.state.charts = [];
        document.querySelectorAll('.js-plotly-plot').forEach(el => { try { Plotly.purge(el); } catch (_) { /* noop */ } });
    },

    async navigate(tabId, opts = {}) {
        if (!this.pages[tabId]) tabId = 'overview';

        const token = ++this.state.renderToken;
        this.state.activeTab = tabId;
        if (window.location.hash.replace('#', '') !== tabId) history.replaceState(null, '', `#${tabId}`);

        document.querySelectorAll('.nav-item').forEach(el => {
            el.classList.toggle('active', el.getAttribute('data-tab') === tabId);
        });

        const [title, subtitle] = this.pageMeta[tabId] || ['Project Agere', ''];
        document.getElementById('page-title').innerText = title;
        document.getElementById('page-subtitle').innerText = subtitle;

        const scroller = document.getElementById('main-scroll');
        const prevScroll = scroller ? scroller.scrollTop : 0;

        this.destroyCharts();
        const container = document.getElementById('content-container');
        container.classList.remove('page-enter');
        container.innerHTML = `
            <div class="skeleton h-40"></div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                ${'<div class="skeleton h-28"></div>'.repeat(4)}
            </div>
            <div class="skeleton h-72"></div>
        `;

        try {
            await this.pages[tabId].prepare?.(this);
            if (token !== this.state.renderToken) return;

            container.innerHTML = '';
            await this.pages[tabId].render(container, this);
            if (token !== this.state.renderToken) return;

            void container.offsetWidth;
            container.classList.add('page-enter');
            if (window.lucide) lucide.createIcons();
            UI.animateIn(container);
            if (scroller) scroller.scrollTop = opts.keepScroll ? prevScroll : 0;
        } catch (err) {
            console.error(`[App] Error rendering page ${tabId}:`, err);
            container.innerHTML = `
                <div class="insight tone-bad">
                    <div class="insight-icon"><i data-lucide="alert-triangle" class="w-4 h-4"></i></div>
                    <div>
                        <div class="insight-title">This page failed to render</div>
                        <div class="insight-body font-mono">${UI.esc(err.message)}</div>
                    </div>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    },

    openModal(id) {
        document.getElementById(id)?.classList.add('active');
        if (window.lucide) lucide.createIcons();
    },

    closeModal(id) {
        document.getElementById(id)?.classList.remove('active');
    },

    showFigure(src, title, caption) {
        document.getElementById('figure-modal-title').innerText = title || 'Figure';
        document.getElementById('figure-modal-caption').innerText = caption || '';
        document.getElementById('figure-modal-img').src = src;
        this.openModal('figure-modal');
    },

    showReproduceModal() {
        document.getElementById('modal-case-title').innerText = 'Reproduce the analysis';
        document.getElementById('modal-case-subtitle').innerText = 'No model downloads or GPU needed: everything recomputes from saved outputs';

        const step = (n, label, cmd) => `
            <div class="flex gap-3 items-start reveal" style="--i:${n}">
                <div class="w-7 h-7 rounded-full grid place-items-center text-xs font-bold shrink-0" style="background: rgba(var(--color-mas-rgb), .15); color: var(--color-mas)">${n}</div>
                <div class="flex-1 min-w-0">
                    <div class="text-xs t-secondary mb-1.5">${label}</div>
                    <div class="flex items-center gap-2">
                        <pre class="flex-1 bg-black/40 px-3 py-2 rounded-md text-xs font-mono c-correct overflow-x-auto">${cmd}</pre>
                        <button class="btn p-2" title="Copy" onclick="navigator.clipboard?.writeText('${cmd}'); this.innerHTML='<i data-lucide=check class=w-3.5\\ h-3.5></i>'; lucide.createIcons();">
                            <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>
                </div>
            </div>`;

        document.getElementById('modal-case-body').innerHTML = `
            ${step(1, 'Verify and unpack the SSD evidence archives', 'python dashboard_handoff/restore_evidence.py')}
            ${step(2, 'Recompute the 126 hypothesis tests', 'python scripts/reporting/paper_statistical_tests.py')}
            ${step(3, 'Regenerate publication figures', 'python scripts/reporting/paper_figures.py')}
            ${step(4, 'Rebuild dashboard data and launch', 'python run_dashboard.py')}
        `;
        this.openModal('case-modal');
    },

    exportData() {
        const blob = new Blob([JSON.stringify(this.state.data, null, 2)], { type: 'application/json' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = `agere_${this.state.activeTab}_data.json`;
        a.click();
        setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    }
};
