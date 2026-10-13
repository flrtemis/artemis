# OWNER ACTION REQUIRED: enable GitHub Pages

This branch contains the Pages-ready static site in root `docs/index.html` and
`docs/assets/`. It was prepared for local testing, **not published or verified
live by the agent**. A push does not configure Pages. No Pages settings or
publishing Actions have been changed.

Once the feature branch is available on GitHub:

1. Open **`flrtemis/artemis` → Settings → Pages**.
2. Under **Build and deployment**, set **Source: Deploy from a branch**.
3. Select **`arena/b4094b40-artemis`** and folder **`/docs`**.
4. Click **Save** and wait for GitHub's deployment to complete.
5. Check **https://flrtemis.github.io/artemis/**. Please report back if it fails.

If the reviewed feature is *later* merged into `main`, select **`main` + `/docs`**
for a stable published source. Do not merge just to enable Pages. Publication
verification waits for your settings action. An Actions publishing approach is
optional and would require your approval first.

## Review without deploying

From the repository root:

```bash
python3 artemis/scripts/serve_pages.py --port 4173
# Open http://localhost:4173/artemis/
```

This serves only the public static `docs` folder under the real project prefix.
It never hosts Ollama, accesses private state, requests a camera/microphone or
calls the ARTEMIS backend. Normal browser links to GitHub remain external;
fonts/styles/scripts/images/recorded trace are local assets. JavaScript only
enhances the recorded walkthrough and copy button.

`docs/ATTRIBUTION.md` explains the actual screenshots/evidence and license limits.
The application quickstart is in the root README and `artemis/README.md`.
