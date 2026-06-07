# OutboundAI — DigitalOcean App Platform Deployment Guide

This guide describes how to deploy **OutboundAI** to DigitalOcean App Platform with a stateless, production-grade architecture.

---

## 🏗️ Architecture on DigitalOcean

DigitalOcean App Platform runs **two separate components** from a single repository using your `Dockerfile`:

| Component | Type | What it does | Run Command |
|---|---|---|---|
| `outboundai-web` | Web Service | FastAPI Dashboard + API | `uvicorn server:app --host 0.0.0.0 --port ${PORT}` |
| `outboundai-worker` | Background Worker | LiveKit AI Agent Worker | `python agent.py start` |

* **Database**: Stateless connection to **Supabase** (external).
* **Storage**: Calls recorded directly to **Supabase Storage / S3**.

> ⚠️ **Both components MUST be running.** The web service serves the dashboard, but without the worker, no calls can be dispatched or answered.

---

## 🚀 Step-by-Step Deployment Instructions

### 1. Database Setup (Supabase)
Before deploying, make sure your Supabase schema is initialized:
1. Go to your **Supabase Dashboard** -> **SQL Editor**.
2. Copy the contents of [`supabase_schema.sql`](./supabase_schema.sql).
3. Click **Run** to execute the query and initialize the required tables.

### 2. Push Code to GitHub
Ensure all files are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure for DigitalOcean deployment"
git push origin main
```

> ✅ `app.yaml` already contains `github:` source blocks pointing to `manoj00sinha/gemini-outbound` — no extra source config needed.

---

### 3. Deploy to DigitalOcean

There are **two ways** to deploy this spec:

#### Method A: Using the DigitalOcean CLI (`doctl`) — Recommended
This is the fastest method and automatically configures all environment variables and both components from your local `app.yaml` file.

**Step 1 — Install doctl on Windows (no admin required):**
```powershell
# Download and extract doctl
Invoke-WebRequest -Uri "https://github.com/digitalocean/doctl/releases/download/v1.119.0/doctl-1.119.0-windows-amd64.zip" -OutFile "$env:TEMP\doctl.zip" -UseBasicParsing
Expand-Archive -Path "$env:TEMP\doctl.zip" -DestinationPath "$env:TEMP\doctl" -Force
Copy-Item "$env:TEMP\doctl\doctl.exe" "$env:USERPROFILE\doctl.exe" -Force
$env:PATH = "$env:USERPROFILE;$env:PATH"
```

**Step 2 — Authenticate with your DigitalOcean API token:**

Get your token from: **DO Console → API → Tokens → Generate New Token** (enable Write access).
```powershell
& "$env:USERPROFILE\doctl.exe" auth init --access-token YOUR_DO_TOKEN_HERE
```

**Step 3 — (If redeploying) Delete the existing broken app first:**
```powershell
# List apps to find your app ID
& "$env:USERPROFILE\doctl.exe" apps list

# Delete the old app (replace APP_ID with the actual ID)
& "$env:USERPROFILE\doctl.exe" apps delete APP_ID --force
```

**Step 4 — Create the app fresh from spec:**
```powershell
& "$env:USERPROFILE\doctl.exe" apps create --spec app.yaml
```

> ⚠️ **After creation, manually set `GOOGLE_API_KEY`** in the DO Console:
> App → Settings → App-Level Environment Variables → Edit → add `GOOGLE_API_KEY` = your actual GCP key → mark as **Encrypted** → Save.
> (This key is intentionally excluded from `app.yaml` for security — GitHub blocks pushes containing GCP keys.)

**Step 5 — Monitor deployment progress:**
```powershell
& "$env:USERPROFILE\doctl.exe" apps list
```

This single command deploys **both** `outboundai-web` (Web Service) and `outboundai-worker` (Worker) with all environment variables from `app.yaml`.

---

#### Method B: Using the DigitalOcean Web Console
If you prefer not to use the CLI:
1. Go to the **DigitalOcean Control Panel** -> **Apps** -> **Create App**.
2. Select **GitHub** as the source, select your repository (`gemini-outbound`), and choose the `main` branch.
3. Click **Next** to let DigitalOcean analyze the repository.
4. It will detect the `Dockerfile` and suggest a single service. Click **Edit** or click **Add Component**:
   * Create a **Web Service** component called `outboundai-web`:
     * Set build method: **Dockerfile**.
     * HTTP Port: `8080`.
     * Run Command: `sh -c "uvicorn server:app --host 0.0.0.0 --port $PORT"`
   * Create a **Worker** component called `outboundai-worker`:
     * Set build method: **Dockerfile**.
     * Run Command: `python agent.py start`
     * **No HTTP port** — workers don't expose ports.
5. Go to the **App-Level Environment Variables** section and add ALL variables from your local `.env` file. Mark sensitive keys (API keys, passwords, secrets) as **Encrypted**.
6. Click **Create Resources** to start the build.

---

## 🔍 Verifying the Deployment

### 1. Build Verification
During the build phase, check the logs in the DigitalOcean console:
* **Silero VAD model download**: The build processes the `Dockerfile` and downloads the Silero VAD voice model pre-emptively:
  `RUN python -c "from livekit.plugins import silero; silero.VAD.load()"`
  This ensures the agent worker starts up instantly when jobs are dispatched.

### 2. Service Verification
* **Web Service**: Navigate to your app's public URL (e.g., `https://outboundai-xxx.ondigitalocean.app/`). You should see the OutboundAI Glassmorphic Dashboard.
* **Worker Service**: Check the logs of `outboundai-worker`. You should see:
  ```
  [outbound-agent] INFO: Loaded google.realtime.RealtimeModel
  [outbound-agent] INFO: registered worker
  ```

### 3. Confirm Environment Variables Are Set
In the DO Console → your App → **Settings** → **App-Level Environment Variables**, confirm these critical keys are present:
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- `GOOGLE_API_KEY`, `GEMINI_MODEL`
- `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`
- `OUTBOUND_TRUNK_ID`

---

## 🛠️ SIP Trunk Configuration (Outbound Calls)

Once both components are successfully deployed:
1. Open your OutboundAI dashboard URL.
2. Go to the **Settings** tab and confirm all credentials (LiveKit, Vobiz, Supabase) are shown as `configured`.
3. Go to the **Setup** tab and click **⚡ Create SIP Trunk**.
4. This registers your Vobiz SIP credentials with LiveKit Cloud.
5. In the pop-up, **copy the generated SIP Trunk ID**.
6. Go back to your DigitalOcean Control Panel -> your App -> **Settings** -> **Environment Variables**.
7. Locate `OUTBOUND_TRUNK_ID` and replace the placeholder value with the new trunk ID.
8. Click **Save** to trigger a quick redeployment.

Once the redeployment completes, you are fully live! Try dispatching a single call to verify the connection.
