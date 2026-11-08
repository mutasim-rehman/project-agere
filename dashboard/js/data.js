/**
 * Data layer: every headline number is derived from the case-level exports so the
 * dashboard cannot drift from the statistical report.
 */

window.Data = {
    PROFILES: ['primary', 'direct_control', 'repair_ablation'],
    PROFILE_LABEL: { primary: 'Primary', direct_control: 'Direct control', repair_ablation: 'Repair ablation' },

    // Sampled controller-plus-worker peak RSS (GB) from TIER_16_V2_STATISTICAL_EVALUATION_REPORT.md §3.
    // memory_timelines.json holds worker-only samples, which read lower.
    REPORT_PEAK_GB: {
        'tier16-sas-primary': 10.062, 'tier16-mas-primary': 10.929,
        'tier16-sas-direct_control': 10.040, 'tier16-mas-direct_control': 10.901,
        'tier16-sas-repair_ablation': 10.074, 'tier16-mas-repair_ablation': 10.913
    },
    APP_CEILING_GB: 11.5,
    NOMINAL_CAP_GB: 12.8,

    async cases16() {
        return (await App.fetchJson('data/tier16_v2/case_outcomes.json')) || [];
    },

    async cases8() {
        return (await App.fetchJson('data/le16_v2/tier8_case_outcomes.json')) || [];
    },

    summarize(rows) {
        const s = { n: rows.length, C: 0, W: 0, H: 0, rawC: 0, rawW: 0, rawH: 0, exec: 0, initC: 0, gen: 0, prompt: 0, secs: 0, repairs: 0, evid: 0 };
        for (const r of rows) {
            if (r.reported_outcome === 'correct') s.C++;
            else if (r.reported_outcome === 'withheld') s.H++;
            else s.W++;
            if (r.raw_outcome === 'correct') s.rawC++;
            else if (r.raw_outcome === 'withheld') s.rawH++;
            else s.rawW++;
            s.exec += r.execution_valid ? 1 : 0;
            s.initC += r.initial_reported_correct ? 1 : 0;
            s.gen += r.generated_tokens || 0;
            s.prompt += r.prompt_tokens || 0;
            s.secs += r.inference_seconds || 0;
            s.repairs += r.repair_attempted ? 1 : 0;
            s.evid += r.annotated_evidence_complete ? 1 : 0;
        }
        s.acc = s.n ? s.C / s.n : 0;
        s.rawAcc = s.n ? s.rawC / s.n : 0;
        s.coverage = s.n ? (s.C + s.W) / s.n : 0;
        s.withheldRate = s.n ? s.H / s.n : 0;
        s.precision = (s.C + s.W) ? s.C / (s.C + s.W) : null;
        s.secPerCase = s.n ? s.secs / s.n : 0;
        s.secPerCorrect = s.C ? s.secs / s.C : null;
        s.genPerCase = s.n ? s.gen / s.n : 0;
        s.hours = s.secs / 3600;
        return s;
    },

    async jobs16() {
        if (this._jobs16) return this._jobs16;
        const rows = await this.cases16();
        const byJob = {};
        rows.forEach(r => (byJob[r.job] = byJob[r.job] || []).push(r));
        const out = {};
        for (const [job, list] of Object.entries(byJob)) {
            out[job] = { ...this.summarize(list), job, arm: list[0].arm, profile: list[0].profile, peakGb: this.REPORT_PEAK_GB[job] };
        }
        this._jobs16 = out;
        return out;
    },

    async pair(profile = 'primary') {
        const jobs = await this.jobs16();
        return { mas: jobs[`tier16-mas-${profile}`], sas: jobs[`tier16-sas-${profile}`] };
    },

    /** 3x3 matrix of per-question reported outcome: rows = SAS, cols = MAS. */
    async transitions(profile = 'primary', metric = 'reported') {
        const rows = await this.cases16();
        const key = metric === 'raw' ? 'raw_outcome' : 'reported_outcome';
        const mas = {}, sas = {};
        rows.forEach(r => {
            if (r.profile !== profile) return;
            (r.arm === 'mas' ? mas : sas)[r.case_id] = r[key];
        });
        const states = ['correct', 'wrong', 'withheld'];
        const m = Object.fromEntries(states.map(s => [s, Object.fromEntries(states.map(t => [t, 0]))]));
        Object.keys(mas).forEach(id => { if (sas[id]) m[sas[id]][mas[id]]++; });
        return m;
    },

    async companies(profile = 'primary') {
        const rows = await this.cases16();
        const map = {};
        rows.forEach(r => {
            if (r.profile !== profile) return;
            const c = map[r.company] = map[r.company] || { company: r.company, reports: new Set(), mas: [], sas: [] };
            c.reports.add(r.report);
            c[r.arm].push(r);
        });
        return Object.values(map).map(c => {
            const mas = this.summarize(c.mas), sas = this.summarize(c.sas);
            return { company: c.company, reports: c.reports.size, n: sas.n, mas, sas, gap: sas.acc - mas.acc };
        }).sort((a, b) => b.n - a.n || a.company.localeCompare(b.company));
    },

    async tier8Conditions() {
        const inv = (await App.fetchJson('data/le16_v2/tier8_condition_inventory.json')) || [];
        const map = {};
        inv.forEach(r => {
            const c = map[r.job] = map[r.job] || { job: r.job, n: r.n, reports: r.reports, peakGb: r.peak_rss_bytes / 1e9, secs: r.inference_seconds, gen: r.generated_tokens };
            c[r.metric === 'case_success' ? 'reported' : 'raw'] = { C: r.correct, W: r.wrong, H: r.withheld };
        });
        return Object.values(map).map(c => {
            const [cohort, rest] = c.job.split('-').length > 1 ? [c.job.split('-')[0], c.job.split('-').slice(1).join('-')] : ['', c.job];
            const name = rest.replace(/-full-01$/, '');
            const arm = /sas/.test(name) ? 'sas' : 'mas';
            return { ...c, cohort: cohort === 'diagnostic_audit' ? 'reserved' : 'selection', name, arm };
        });
    }
};
