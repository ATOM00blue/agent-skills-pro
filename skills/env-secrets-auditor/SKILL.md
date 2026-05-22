---
name: env-secrets-auditor
description: Scans code, config, and environment files for hardcoded secrets, leaked credentials, and insecure secret handling, and recommends safe fixes. Use when the user asks to check for secrets, audit env vars, find leaked API keys/passwords/tokens, review .env handling, or harden how the project manages credentials.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: security
---

# Env & Secrets Auditor

Find leaked or mishandled secrets and tell the user exactly how to remediate. **Never print a
full live secret back** — show enough to locate it (file + line + first/last few chars).

## Workflow

```
- [ ] 1. Scan source, config, and history-prone files for secret patterns
- [ ] 2. Triage each hit: real secret, test/placeholder, or false positive
- [ ] 3. Report findings: severity, location, redacted match, fix
- [ ] 4. Recommend a remediation plan (rotate, remove, prevent)
```

## Step 1 — Where secrets hide

Scan these, in priority order:
- Source files with assignments to secret-like names (`apiKey`, `password`, `token`, `secret`,
  `private_key`, `db_url` with credentials).
- Config: `.env`, `.env.*`, `config.*`, `docker-compose.yml`, CI files (`.github/workflows/*`),
  k8s manifests, Terraform/`*.tfvars`.
- Files that often get committed by accident: `.env`, `*.pem`, `*.key`, `id_rsa`,
  `credentials.json`, `serviceAccount*.json`, `.npmrc`/`.pypirc` with tokens.
- **Git history** (a removed secret in a committed file is still leaked) — recommend a history
  scan with a dedicated tool.

## Step 2 — What a secret looks like

High-signal patterns (treat as findings unless clearly a placeholder):

| Kind | Pattern hint |
| ---- | ------------ |
| AWS access key | `AKIA` / `ASIA` + 16 uppercase alphanumerics |
| AWS secret key | 40-char base64-ish near an AWS key |
| GitHub token | `ghp_`, `gho_`, `ghs_`, `github_pat_` |
| Slack token | `xoxb-`, `xoxp-`, `xapp-` |
| Stripe | `sk_live_`, `rk_live_` (and `pk_live_` publishable — lower risk) |
| Google API key | `AIza` + 35 chars |
| Private key block | `-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----` |
| JWT | three base64url segments split by `.` |
| Generic | long high-entropy string assigned to a `secret`/`token`/`password` var |
| Connection string with creds | `postgres://user:pass@host`, `mongodb+srv://...:...@` |

## Step 3 — Triage (avoid false-positive noise)

Before reporting, classify each hit:
- **Real secret:** live-looking value in a tracked file → report.
- **Placeholder/example:** `your-api-key-here`, `xxxx`, `changeme`, `${VAR}`, values in
  `.env.example` → not a leak (but flag if it's in a real `.env` that's tracked).
- **Test fixture:** clearly fake/expired test keys → low severity, note it.
- **Reference, not value:** reading `process.env.API_KEY` / `os.environ[...]` is the *correct*
  pattern → not a finding.

## Report format

For each finding, redact the value:
```
[SEVERITY] <secret kind> in <file>:<line>
Match: AKIA****************WXYZ   (redacted)
Risk: <what an attacker could do>
Fix: <specific remediation>
```
Severity: **Critical** (live prod credential / private key in tracked code),
**High** (live key, lower blast radius), **Medium** (in history only, or weak handling),
**Low** (test/placeholder, or hygiene).

## Step 4 — Remediation plan

If a real secret was committed, **rotation is mandatory** — removing it from the file is not
enough, because it's already in history and any clone/fork.

1. **Rotate immediately.** Revoke and reissue the credential at the provider. Assume it's
   compromised.
2. **Remove from the code.** Replace with an env var read at runtime:
   ```diff
   - const apiKey = "sk_live_abc123...";
   + const apiKey = process.env.STRIPE_API_KEY;  // set via the secret manager
   ```
3. **Purge from git history** if it was committed (e.g. `git filter-repo` or BFG), then force-
   push and have collaborators re-clone. Note this is disruptive.
4. **Add `.gitignore` entries** for `.env`, `*.pem`, `*.key`, etc., and commit a `.env.example`
   with empty placeholders instead.

## Secure-handling recommendations

- Keep secrets in environment variables or a secret manager (Vault, AWS/GCP Secrets Manager,
  Doppler, 1Password), injected at runtime — not in the repo or the image.
- Use a `.env` locally (git-ignored) + a committed `.env.example` documenting required keys.
- In CI, use the platform's encrypted secrets; never echo them to logs.
- Add a pre-commit secret scanner (gitleaks, trufflehog, detect-secrets) and a CI gate so new
  leaks are caught automatically.
- Scope credentials to least privilege and set expiries where the provider allows.

## Example

**Input:**
```python
# settings.py
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
DATABASE_URL = os.environ["DATABASE_URL"]
```
**Findings:**
```
[Critical] AWS access key in settings.py:2
Match: AKIA************AMPLE   (redacted)
Risk: full programmatic access to whatever this IAM key permits.
Fix: rotate the key now; read it from the environment / a secret manager; purge from history.

DATABASE_URL: OK — read from the environment (correct pattern), not a finding.
```

## Common edge cases
- **Publishable/public keys** (e.g. `pk_live_`, frontend API keys meant to ship): lower
  severity, but confirm they're domain/usage-restricted.
- **High-entropy non-secrets** (hashes, UUIDs, content hashes): not credentials — don't flag.
- **Encrypted secrets** (SOPS, sealed-secrets, age-encrypted): safe to commit; verify they're
  actually encrypted, not just renamed.
- **Reported in history only:** still requires rotation; the value is public to anyone with
  the repo.
