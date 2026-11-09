/**
 * Shared UI toolkit: theme-aware colors, chart defaults, reusable components and motion.
 */

window.UI = {
    esc(s) {
        return String(s ?? '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));
    },

    css(name) {
        return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    },

    colors() {
        const c = n => this.css(n);
        return {
            mas: c('--color-mas'), sas: c('--color-sas'),
            correct: c('--color-correct'), wrong: c('--color-wrong'), withheld: c('--color-withheld'),
            accent: c('--color-accent'),
            text: c('--text-primary'), text2: c('--text-secondary'), muted: c('--text-muted'),
            grid: c('--grid-color'), border: c('--border-color'), surface: c('--bg-surface-solid'),
            rgb: n => c(`--color-${n}-rgb`)
        };
    },

    alpha(name, a) {
        return `rgba(${this.css(`--color-${name}-rgb`)}, ${a})`;
    },

    applyChartDefaults() {
        if (!window.Chart) return;
        const k = this.colors();
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 11;
        Chart.defaults.color = k.text2;
        Chart.defaults.borderColor = k.grid;
        Chart.defaults.animation.duration = 1100;
        Chart.defaults.animation.easing = 'easeOutQuart';
        Chart.defaults.plugins.legend.labels.boxWidth = 10;
        Chart.defaults.plugins.legend.labels.boxHeight = 10;
        Chart.defaults.plugins.legend.labels.useBorderRadius = true;
        Chart.defaults.plugins.legend.labels.borderRadius = 3;
        Chart.defaults.plugins.legend.labels.color = k.text2;
        Object.assign(Chart.defaults.plugins.tooltip, {
            backgroundColor: k.surface, titleColor: k.text, bodyColor: k.text2,
            borderColor: k.border, borderWidth: 1, padding: 10, cornerRadius: 8,
            titleFont: { weight: '600' }, boxPadding: 4, usePointStyle: true
        });
        Chart.defaults.scale.grid.color = k.grid;
        Chart.defaults.scale.border = { display: false };
    },

    chart(canvasId, config) {
        const el = document.getElementById(canvasId);
        if (!el || !window.Chart) return null;
        return App.trackChart(new Chart(el, config));
    },

    plotLayout(extra = {}) {
        const k = this.colors();
        const axis = { gridcolor: k.grid, zerolinecolor: k.border, tickfont: { color: k.text2, size: 10, family: 'JetBrains Mono' }, title: { font: { color: k.text2, size: 11 } } };
        return {
            paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)',
            font: { family: 'Inter', color: k.text2, size: 11 },
            margin: { l: 50, r: 20, t: 10, b: 40 },
            hoverlabel: { bgcolor: k.surface, bordercolor: k.border, font: { color: k.text, family: 'Inter', size: 12 } },
            legend: { font: { color: k.text2, size: 11 }, orientation: 'h', y: -0.18 },
            ...extra,
            xaxis: { ...axis, ...(extra.xaxis || {}), title: { ...axis.title, ...((extra.xaxis || {}).title || {}) } },
            yaxis: { ...axis, ...(extra.yaxis || {}), title: { ...axis.title, ...((extra.yaxis || {}).title || {}) } }
        };
    },

    plotConfig: { responsive: true, displayModeBar: false },

    /* ---------- Formatting ---------- */
    pct(n, d, digits = 1) {
        return d ? (100 * n / d).toFixed(digits) : '0.0';
    },

    fmtP(p) {
        if (p == null || isNaN(p)) return '—';
        if (p < 0.001) return p.toExponential(1).replace('e-', '×10⁻').replace(/⁻(\d+)/, (_, d) => '⁻' + d.split('').map(x => '⁰¹²³⁴⁵⁶⁷⁸⁹'[x]).join(''));
        return p.toFixed(3);
    },

    num(n, digits = 0) {
        return Number(n).toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits });
    },

    /* ---------- Components ---------- */
    kpi({ label, value, decimals = 0, prefix = '', suffix = '', foot = '', tone = 'accent', icon = 'activity', i = 0 }) {
        const color = tone === 'accent' ? 'var(--color-accent)' : `var(--color-${tone})`;
        const rgb = tone === 'accent' ? '129, 140, 248' : `var(--color-${tone}-rgb)`;
        return `
            <div class="card kpi card-hover reveal" style="--i:${i}; --kpi-color:${color}; --kpi-rgb:${rgb}">
                <div class="kpi-icon"><i data-lucide="${icon}" class="w-4 h-4"></i></div>
                <div class="kpi-label">${label}</div>
                <div class="kpi-value"><span data-count="${value}" data-decimals="${decimals}" data-prefix="${prefix}" data-suffix="${suffix}">${prefix}0${suffix}</span></div>
                <div class="kpi-foot">${foot}</div>
            </div>`;
    },

    insight({ tone = 'mas', icon = 'lightbulb', title, body, i = 0 }) {
        return `
            <div class="insight tone-${tone} reveal" style="--i:${i}">
                <div class="insight-icon"><i data-lucide="${icon}" class="w-4 h-4"></i></div>
                <div class="min-w-0">
                    <div class="insight-title">${title}</div>
                    ${body ? `<div class="insight-body">${body}</div>` : ''}
                </div>
            </div>`;
    },

    card({ title, sub = '', right = '', body, cls = '', i = 0 }) {
        return `
            <section class="card reveal ${cls}" style="--i:${i}">
                <div class="card-head">
                    <div class="min-w-0">
                        <h3 class="card-title">${title}</h3>
                        ${sub ? `<p class="card-sub">${sub}</p>` : ''}
                    </div>
                    ${right ? `<div class="shrink-0">${right}</div>` : ''}
                </div>
                ${body}
            </section>`;
    },

    hero({ eyebrow, title, sub = '', right = '' }) {
        return `
            <section class="hero reveal">
                <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
                    <div class="min-w-0">
                        <div class="eyebrow">${eyebrow}</div>
                        <h2 class="hero-title mt-2">${title}</h2>
                        ${sub ? `<p class="hero-sub">${sub}</p>` : ''}
                    </div>
                    ${right ? `<div class="shrink-0">${right}</div>` : ''}
                </div>
            </section>`;
    },

    disclosure({ title, meta = '', body, open = false, i = 0 }) {
        return `
            <details class="disclosure reveal" style="--i:${i}" ${open ? 'open' : ''}>
                <summary>
                    <span class="flex items-center gap-2"><i data-lucide="table-2" class="w-4 h-4 t-muted"></i>${title}</span>
                    <span class="flex items-center gap-3 text-xs t-muted font-normal">${meta}<i data-lucide="chevron-down" class="w-4 h-4 chev"></i></span>
                </summary>
                <div class="disclosure-body">${body}</div>
            </details>`;
    },

    stackbar(c, w, h, n, { labels = true } = {}) {
        const seg = (cls, v, title) => `<div class="${cls}" data-w="${100 * v / n}" title="${title}: ${v} of ${n} (${this.pct(v, n)}%)">${labels && v / n > 0.07 ? v : ''}</div>`;
        return `<div class="stackbar">${seg('seg-correct', c, 'Correct')}${seg('seg-wrong', w, 'Wrong')}${seg('seg-withheld', h, 'Withheld')}</div>`;
    },

    meter(value, max, color) {
        return `<div class="meter"><div data-w="${100 * value / max}" style="background:${color}"></div></div>`;
    },

    outcomeLegend() {
        return `
            <div class="legend">
                <span><i class="sw" style="background:var(--color-correct)"></i>Correct</span>
                <span><i class="sw" style="background:var(--color-wrong)"></i>Wrong</span>
                <span><i class="sw" style="background:var(--color-withheld)"></i>Withheld</span>
            </div>`;
    },

    outcomeBadge(outcome, correct) {
        if (correct || outcome === 'correct') return '<span class="badge badge-correct">correct</span>';
        if (outcome === 'withheld') return '<span class="badge badge-withheld">withheld</span>';
        return '<span class="badge badge-wrong">wrong</span>';
    },

    armBadge(arm) {
        return arm === 'mas' ? '<span class="badge badge-mas">MAS</span>' : '<span class="badge badge-sas">SAS</span>';
    },

    /* ---------- Motion ---------- */
    countUp(el) {
        const target = parseFloat(el.dataset.count);
        if (isNaN(target)) return;
        const decimals = parseInt(el.dataset.decimals || '0', 10);
        const prefix = el.dataset.prefix || '';
        const suffix = el.dataset.suffix || '';
        const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const duration = reduce ? 0 : 1300;
        const start = performance.now();
        const fmt = v => prefix + v.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
        const tick = now => {
            const t = duration ? Math.min(1, (now - start) / duration) : 1;
            const eased = 1 - Math.pow(1 - t, 4);
            el.textContent = fmt(target * eased);
            if (t < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    },

    animateIn(root) {
        const run = el => {
            if (el.dataset.count !== undefined) this.countUp(el);
            if (el.dataset.w !== undefined) el.style.width = `${Math.max(0, Math.min(100, parseFloat(el.dataset.w)))}%`;
        };
        const targets = root.querySelectorAll('[data-count], [data-w]');
        if (!('IntersectionObserver' in window)) { targets.forEach(run); return; }
        const io = new IntersectionObserver(entries => {
            entries.forEach(e => {
                if (e.isIntersecting) {
                    setTimeout(() => run(e.target), 120);
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.1 });
        targets.forEach(t => io.observe(t));
    }
};

UI.applyChartDefaults();
