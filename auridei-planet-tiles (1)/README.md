# AURIDEI planet tiles (GitHub Actions)

Builds Mars from free NASA/USGS data (Viking color mosaic + MOLA/HRSC elevation)
on GitHub's servers and uploads the tiles to Cloudflare R2, served at
`https://tiles.auridei.com/mars/`. Nothing runs on your own computer.

## One-time setup

### 1. Cloudflare R2 (~10 minutes)
1. Cloudflare dashboard → **R2 Object Storage** → **Create bucket** → name it `auridei-tiles`.
2. Bucket → **Settings** → **Custom Domains** → **Connect domain** → `tiles.auridei.com`.
3. Bucket → **Settings** → **CORS policy** → **Add CORS policy** → paste:
   ```json
   [{"AllowedOrigins":["*"],"AllowedMethods":["GET","HEAD"],"AllowedHeaders":["*"],"MaxAgeSeconds":86400}]
   ```
4. R2 overview page → **Manage API tokens** → **Create API token**:
   - Permissions: **Object Read & Write**
   - Specify bucket: **auridei-tiles**
   - Create, then copy the **Access Key ID** and **Secret Access Key** (shown once).
5. Also copy your **Account ID** (R2 overview page, right side).

### 2. GitHub repository (~5 minutes)
1. github.com → **New repository** → name `auridei-planet-tiles`.
   **Public is recommended**: public repos get faster build machines and unlimited
   free minutes, and nothing secret is stored in the files (the keys go in secrets).
2. Upload the contents of this folder (keep the `.github` folder — it holds the workflow).
   Easiest: on the new repo page click **uploading an existing file**, then drag in
   **everything inside** this folder, including `.github`.
   If the `.github` folder won't drag in, create the file manually: **Add file → Create new file**,
   name it `.github/workflows/build-mars-tiles.yml`, and paste the contents of that file.
3. Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**, three times:
   - `R2_ACCOUNT_ID` = your Cloudflare Account ID
   - `R2_ACCESS_KEY_ID` = the Access Key ID
   - `R2_SECRET_ACCESS_KEY` = the Secret Access Key

## Run it
Repo → **Actions** tab → **Build Mars tiles** → **Run workflow** → keep "both" and "8" → **Run workflow**.

Two jobs run at the same time — color tiles and terrain. Each takes roughly 1–5 hours.
You can close the browser; GitHub emails you when it finishes or fails.

If a job fails, open it, copy the red error lines, and send them to Claude. You can re-run
just one part with "imagery" or "terrain".

## Check it worked
- https://tiles.auridei.com/mars/imagery/0/0/0.jpg (western half of Mars)
- https://tiles.auridei.com/mars/terrain/layer.json

Then tell Claude, and the app gets switched over.

## Data (public domain)
- Mars Viking Colorized Global Mosaic 232m — NASA / USGS Astrogeology
- Mars MGS MOLA – MEX HRSC Blended DEM Global 200m — NASA / ESA / DLR / USGS Astrogeology
