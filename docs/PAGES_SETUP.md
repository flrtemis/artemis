# Owner-controlled GitHub Pages — live source and Sage preview

**October 14 update:** the owner reports Pages live. A read-only GitHub check confirms
`https://flrtemis.github.io/artemis/` is built from **`main` + `/`**. That source
currently renders the older milestone-02 README, not the newer feature guide or
Sage interaction lab. The agent has not changed publishing settings, merged, or
deployed an update.

## Review this feature's guide and Sage interaction lab

This branch contains the static guide in root `docs/index.html`, the additive
shared-component interaction lab in `docs/sage-preview.html`, and local assets.
The lab has synthetic examples and **no model/backend**. Its optional browser
narration is explicitly initiated by the visitor and limited to a voice the device
reports as local; that is not proof of physical audio or the ARTEMIS voice pipeline.

**Only the owner changes Pages.** To publish this feature without a merge:

1. Open **`flrtemis/artemis` → Settings → Pages**.
2. Under **Build and deployment**, use **Source: Deploy from a branch**.
3. Select **`arena/b4094b40-artemis`** and folder **`/docs`**.
4. Click **Save** and wait for GitHub's deployment.
5. Check **https://flrtemis.github.io/artemis/**, then its **Explore Sage** link
   (`https://flrtemis.github.io/artemis/sage-preview.html`). Report any failure.

**Do not select this branch's `/` root.** It contains the owner's **read-only,
branch-only `ideas/` inbox**, which must not be served or promoted into `main`.
A branch in a public repository is not a private place for captures/credentials.
The website includes derived design, never those raw files or session data.

**Do not merge this shared branch directly.** Its owner-upload commits are
branch-only. A later reviewed promotion must select the implementation changes
without inbox commits/files. After that separate review/promotion, `main` +
`/docs` can become the stable published source. Do not merge just to publish.

No Actions publishing workflow is added or enabled. Any such approach needs the
owner's approval. Live availability of the existing site does not mean this
new preview is deployed; verify the deployed version after the owner's action.

## Local review without deploying

From the repository root:

```bash
python3 artemis/scripts/serve_pages.py --port 4173
# Guide: http://localhost:4173/artemis/
# Sage lab: http://localhost:4173/artemis/sage-preview.html
```

This serves only `docs` under the project prefix. It cannot host Ollama, read the
inbox/private runtime state, acquire the microphone/camera or call the ARTEMIS
backend. Guide assets and synthetic preview are self-hosted; normal links to
GitHub remain external. The preview declares `connect-src 'none'` and does not
collect credentials or add tracking storage.

Rebuild the preview from the application frontend:

```bash
cd artemis/frontend
npm ci
npm run typecheck
npm run build:sage-preview
```

The runtime helper and this visual lab share `SageHelper.tsx`; the runtime uses
actual canonical state/commands, while the lab exposes clearly labelled synthetic
examples only. The application build remains `npm run build`.

Attribution and licensing: [ATTRIBUTION.md](ATTRIBUTION.md).
Research/cumulative scope: `artemis/docs/SAGE_HELPER_RESEARCH.md` and
`artemis/docs/ONGOING_WORK.md`. Complete current trial/verification:
`artemis/docs/SAGE_HELPER_01.md`.
