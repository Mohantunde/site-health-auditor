# Contributing

Thank you for considering a contribution.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
pytest
```

On Windows:

```powershell
.venv\Scripts\activate
```

## Pull requests

- Keep changes focused.
- Add or update tests when behavior changes.
- Update the README when adding user-facing functionality.
- Never include credentials, private URLs, customer data, or production secrets.
