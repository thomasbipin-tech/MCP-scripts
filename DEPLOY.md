# Deploying DealProof to the cloud (phone-accessible full app)

This deploys the **whole app** — API + database + document upload + processing +
login + the React UI — to a public HTTPS URL you can open on your phone. It runs
as **one web service + one Postgres database** (the pipeline runs inline, so no
Redis/Celery/MinIO are needed for a hosted deployment).

The image is `Dockerfile.web`: FastAPI serves both the API (`/api/...`) and the
built React UI (`/`). It was smoke-tested serving the SPA, the API, the sample
report JSON, and the source PDFs from a single port.

---

## Option A — Render (one-click Blueprint, recommended)

1. Push this branch (already done) and sign in at <https://render.com> (free tier is fine).
2. **New → Blueprint** → connect your GitHub and pick `thomasbipin-tech/MCP-scripts`.
3. When asked for the branch, choose **`claude/dealproof-diligence-platform-spy5jm`**.
4. Render reads `render.yaml` and proposes: a **web service** (`dealproof`) + a
   **Postgres** database (`dealproof-db`). Click **Apply**.
5. Wait for the build (~3–5 min the first time — it builds the frontend and the
   Python image). When it's live, Render shows a URL like
   `https://dealproof.onrender.com`.

Open that URL on your phone. On first boot the app creates its schema and seeds
the live sample deal, so the landing page and the sample report work immediately.

`render.yaml` already wires `DATABASE_URL` from the managed DB and generates a
`JWT_SECRET`. Note: the free web service sleeps after inactivity, so the first
request after idle takes ~30s to wake.

## Option B — Railway

1. <https://railway.app> → **New Project → Deploy from GitHub repo** → this repo,
   the DealProof branch.
2. Railway detects `Dockerfile.web` (set the Dockerfile path if prompted).
3. **Add a Postgres** plugin; Railway sets `DATABASE_URL` automatically.
4. Add env var `JWT_SECRET` (any long random string). Deploy → open the URL.

## Option C — Any Docker host / VM

```bash
docker build -f Dockerfile.web -t dealproof .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e JWT_SECRET="$(openssl rand -hex 32)" \
  dealproof
# then put it behind your reverse proxy / domain with HTTPS
```
(Omit `DATABASE_URL` to run on an ephemeral local SQLite file for a quick look.)

---

## Using the app once it's up

The whole flow is clickable in the UI (verified end-to-end in a headless
browser at phone width):

- **Sample report** — no login needed; seeded and published on boot. Open the
  landing page and tap **View sample report** (`/#/report`).
- **The working app** — tap **Sign in** / **Launch app** → the login page has
  **"Continue as admin (demo)"** / **"Continue as buyer (demo)"** shortcuts
  (magic-link email also works; in demo mode the link is returned instantly).
  Then: **New Deal** → open it → **drag-and-drop the PDFs** (adjust any detected
  document type) → **Process documents** → (as admin) **Publish report** →
  **Pay/Unlock** → the full report renders, with a **Download PDF** button.
  Sign in as **admin** to be able to publish.

Pre-seeded logins: `admin@dealproof.test` (admin) and `buyer@dealproof.test`.
The same operations are also available programmatically at **`/api/docs`**.

## Notes

- **Demo login:** `ENV=development` makes `/api/auth/request` return the magic
  token in the response so you can log in without an email provider. For a real
  deployment set `ENV=production` and add `RESEND_API_KEY` to email magic links.
- **Claude narration:** add `ANTHROPIC_API_KEY` to switch report prose from the
  deterministic writer to Claude (still guarded by the grounding check).
- **Uploaded files** are stored on the instance's local disk by default
  (ephemeral on free tiers). Set `S3_ENDPOINT`/`S3_*` to use MinIO/R2/S3 for
  durable storage.
- This does **not** touch your GitHub Pages site — the AI Music Studio stays live
  there, untouched.
