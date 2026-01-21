# Pyenv Setup

This project can use a local pyenv virtualenv for repeatable installs.

## Steps

```bash
cd /Users/tdeutsch/codex/tools/forked-simple-cmdb

pyenv install -s 3.11.8
pyenv virtualenv 3.11.8 simple-cmdb-3.11
pyenv local simple-cmdb-3.11

pip install -r requirements.txt
pip install pytest
```

Notes:
- `.python-version` is ignored by git; set it locally with `pyenv local`.
