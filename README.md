# Site Health Auditor

A lightweight open-source command-line tool for checking the availability and basic SEO health of multiple websites.

It is useful for developers, agencies, and website owners who manage several sites and want one repeatable report instead of checking every website manually.

## Features

- Checks HTTP status and response time
- Confirms HTTPS usage
- Reads the page title and meta description
- Counts H1 headings
- Checks canonical URLs and robots meta tags
- Tests `robots.txt` and common sitemap locations
- Audits several sites concurrently
- Creates Markdown and JSON reports
- Supports scheduled audits through GitHub Actions
- Uses a simple YAML configuration file

## Installation

```bash
git clone https://github.com/Mohantunde/site-health-auditor.git
cd site-health-auditor
python -m venv .venv
```

Activate the environment:

**Windows**

```powershell
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

## Configuration

Copy the example configuration:

```bash
cp sites.example.yml sites.yml
```

On Windows:

```powershell
copy sites.example.yml sites.yml
```

Edit `sites.yml`:

```yaml
sites:
  - name: Example Website
    url: https://example.com
    enabled: true
```

## Run an audit

```bash
python -m site_health_auditor --config sites.yml
```

Reports are saved to:

- `reports/site-health-report.md`
- `reports/site-health-report.json`

Optional arguments:

```bash
python -m site_health_auditor   --config sites.yml   --timeout 15   --workers 5   --fail-on-error
```

## GitHub Actions

The included workflow runs the audit every Monday and can also be triggered manually.

Before enabling it:

1. Add a `sites.yml` file to the repository.
2. Open the **Actions** tab in GitHub.
3. Enable workflows.
4. Run **Website health audit** manually once.

The reports are uploaded as workflow artifacts.

## Scope

This is a practical first-line audit. It does not replace a security assessment, accessibility audit, Lighthouse test, or professional SEO review.

## Contributing

Bug reports, feature requests, and pull requests are welcome.

## License

MIT
