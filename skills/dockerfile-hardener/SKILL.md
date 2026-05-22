---
name: dockerfile-hardener
description: Hardens and optimizes Dockerfiles for security and size — non-root user, pinned base images, multi-stage builds, minimal layers, no leaked secrets, and a proper healthcheck. Use when the user shares a Dockerfile, asks to harden, secure, or shrink a container image, reduce attack surface, or follow Docker best practices.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: devops
---

# Dockerfile Hardener

Review a Dockerfile and return a hardened version that is smaller, more secure, and
reproducible. Report each change with the reason and severity.

## Workflow

```
- [ ] 1. Read the Dockerfile and identify the language/runtime
- [ ] 2. Run the hardening checklist
- [ ] 3. Report findings (severity + reason) and the rewritten Dockerfile
- [ ] 4. Suggest a .dockerignore and a quick scan command
```

## Hardening checklist

### Security (highest priority)

1. **Run as non-root.** Containers default to root. Create and switch to an unprivileged user.
   ```dockerfile
   RUN addgroup --system app && adduser --system --ingroup app app
   USER app
   ```
2. **Pin the base image** to a digest (or at least a specific minor tag), never `:latest`.
   ```dockerfile
   FROM node:22.11-bookworm-slim@sha256:<digest>
   ```
3. **Never bake secrets into layers.** Anything in `ENV`, `ARG`, or a `COPY`'d `.env` is
   recoverable from image history. Use BuildKit secrets or runtime env vars.
   ```dockerfile
   RUN --mount=type=secret,id=npm_token \
       NPM_TOKEN=$(cat /run/secrets/npm_token) npm ci
   ```
4. **Use minimal base images** — `-slim`, `alpine`, `distroless`, or `scratch` — to shrink the
   attack surface. Fewer packages, fewer CVEs.
5. **Drop privileges and capabilities** at runtime (document for the user): `--read-only`,
   `--cap-drop=ALL`, `--security-opt=no-new-privileges`.
6. **Don't install unnecessary tools** (curl, build toolchains) in the final image; keep them
   in a build stage only.

### Image size & build speed

7. **Multi-stage build:** compile/install in a builder stage, copy only the artifacts into a
   tiny runtime stage.
8. **Order layers from least to most frequently changing.** Copy dependency manifests and
   install before copying source, so dependency layers stay cached.
   ```dockerfile
   COPY package.json package-lock.json ./
   RUN npm ci --omit=dev
   COPY . .
   ```
9. **Combine related `RUN` steps** and clean package caches in the same layer (a separate
   cleanup layer doesn't reclaim space).
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
       && rm -rf /var/lib/apt/lists/*
   ```
10. **Add a `.dockerignore`** so `.git`, `node_modules`, secrets, and test files never enter
    the build context.

### Correctness & operability

11. **Use exec-form `CMD`/`ENTRYPOINT`** (`["node","server.js"]`) so signals reach the process
    and the container shuts down cleanly; add an init (`--init` or tini) if you fork children.
12. **Add a `HEALTHCHECK`** so orchestrators know when the app is actually ready.
13. **Set `WORKDIR`** explicitly; don't rely on `/`.
14. **Pin dependency installs** to lockfiles (`npm ci`, `pip install -r requirements.txt`
    with hashes, `go mod download`).

## Severity guide

- **Critical:** runs as root, baked-in secret, `:latest` base, no dependency pinning.
- **High:** no multi-stage (bloated image with build tools), no `.dockerignore`.
- **Medium:** poor layer caching, shell-form CMD, missing healthcheck.
- **Low:** style, comments, ordering polish.

## Example: before → after (Node)

**Before:**
```dockerfile
FROM node:latest
WORKDIR /app
COPY . .
RUN npm install
ENV API_KEY=sk_live_abc123
CMD npm start
```

**After:**
```dockerfile
# syntax=docker/dockerfile:1
FROM node:22.11-bookworm-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22.11-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY --from=build --chown=app:app /app/node_modules ./node_modules
COPY --from=build --chown=app:app /app/dist ./dist
COPY --from=build --chown=app:app /app/package.json ./
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/healthz').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
ENTRYPOINT ["node", "dist/server.js"]
```

Changes: pinned base, multi-stage to drop dev deps and build tools, non-root user, removed the
baked-in secret (pass `API_KEY` at runtime), cache-friendly layer order, exec-form entrypoint,
and a healthcheck.

## Recommended `.dockerignore`

```
.git
node_modules
npm-debug.log
Dockerfile
.dockerignore
.env
*.md
dist
coverage
.vscode
```

## Verify

Suggest scanning the built image and checking the user:
```bash
docker scout cves <image>     # or: trivy image <image>
docker run --rm <image> whoami   # should NOT print "root"
docker history <image>           # confirm no secrets in layers
```

## Common edge cases

- **Apps that must bind to port <1024:** prefer a high port + reverse proxy; only grant
  `CAP_NET_BIND_SERVICE` if truly required.
- **Compiled languages (Go/Rust):** build static binaries and use `FROM scratch` or
  `gcr.io/distroless/static` for a near-zero-CVE image.
- **Native build dependencies:** install them in the builder stage only.
- **Files the app writes at runtime:** mount a volume or `tmpfs`; keep the root filesystem
  read-only where possible.
