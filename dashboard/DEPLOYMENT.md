# Deploying the dashboard to Vercel

The dashboard is a static HTML/CSS/JavaScript site. Its prepared research data and
figures are committed inside `dashboard/`. Python is used for research tooling and
the optional local server; it is not a production web backend.

Import the GitHub repository and use these project settings:

- Root Directory: repository root (leave the field empty).
- Framework Preset: Other.
- Build Command: enable Override and leave empty.
- Install Command: enable Override and leave empty.
- Output Directory: `dashboard`.

The repository-root `vercel.json` explicitly sets the framework, install/build
commands and output directory. Keep the Vercel Root Directory at the repository
root so this configuration is loaded. Only `dashboard/` is served as static output;
research scripts and evidence archives outside that folder are not site assets.

Deploy the latest `main` commit containing `vercel.json`. If a failed deployment
reports `PYTHON_ENTRYPOINT_NOT_FOUND`, check the Root Directory and selected commit
before redeploying. Do not add an `app.py` or start `run_dashboard.py` as a build
command: the local server runs continuously, while Vercel serves the static files.

Dashboard navigation uses browser hash fragments and does not require a catch-all
rewrite. Relative `js/`, `css/`, `data/` and `figures/` URLs resolve from the site
root. External chart, styling and icon libraries are loaded from their existing
CDN URLs.

Vercel references:

- [Configuration properties](https://vercel.com/docs/project-configuration/vercel-json)
- [Static builds and root directory settings](https://vercel.com/docs/builds/configure-a-build)
