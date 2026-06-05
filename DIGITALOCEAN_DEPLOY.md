# OutboundAI — DigitalOcean App Platform Deployment Guide

This guide describes how to deploy **OutboundAI** to DigitalOcean App Platform with a stateless, production-grade architecture.

---

## 🏗️ Architecture on DigitalOcean

DigitalOcean App Platform runs **two separate components** from a single repository using your `Dockerfile`:

| Component | Type | What it does | Run Command | Cost / Tier |
|---|---|---|---|---|
| `outboundai-web` | Web Service | FastAPI Dashboard + API | `uvicorn server:app --host 0.0.0.0 --port ${PORT}` | $5/mo (`apps-s-1vcpu-0.5gb`) |
| `outboundai-worker` | Background Worker | LiveKit AI Agent Worker | `python agent.py start` | $5/mo (`apps-s-1vcpu-0.5gb`) |

* **Total Cost**: $10.00 / month.
* **Database**: Stateless connection to **Supabase** (external).
* **Storage**: Calls recorded directly to **Supabase Storage / S3**.

---

## 🚀 Step-by-Step Deployment Instructions

### 1. Database Setup (Supabase)
Before deploying, make sure your Supabase schema is initialized:
1. Go to your **Supabase Dashboard** -> **SQL Editor**.
2. Copy the contents of [`supabase_schema.sql`](file:///c:/SSD%20WINDOW/code/bullk-call-agent/supabase_schema.sql).
3. Click **Run** to execute the query and initialize the 7 required tables.

### 2. Push Code to GitHub
Ensure all your files, including `.gitignore`, `Dockerfile`, and `app.yaml.example` (or `app.yaml` if you are using private git), are pushed to your GitHub repository:
```bash
git add .
git commit -m "Configure for DigitalOcean deployment"
git push origin main
```

---

### 3. Deploy to DigitalOcean

There are **two ways** to deploy this spec:

#### Method A: Using the DigitalOcean CLI (`doctl`) — Recommended
This is the fastest method and automatically configures all environment variables from your local `app.yaml` file:

1. Install and authenticate `doctl`:
   ```bash
   doctl auth init
   ```
2. Create the app from your spec file:
   ```bash
   doctl apps create --spec app.yaml
   ```
3. Monitor the deployment progress:
   ```bash
   doctl apps list
   ```

#### Method B: Using the DigitalOcean Web Console
If you prefer not to use the CLI:
1. Go to the **DigitalOcean Control Panel** -> **Apps** -> **Create App**.
2. Select **GitHub** as the source, select your repository (`gemini-outbound`), and choose the `main` branch.
3. Click **Next** to let DigitalOcean analyze the repository.
4. It will detect the `Dockerfile` and suggest a single service. Click **Edit** or click **Add Component**:
   * Create a **Web Service** component called `outboundai-web`:
     * Set build method: **Dockerfile**.
     * HTTP Port: `8080`.
     * Run Command: `uvicorn server:app --host 0.0.0.0 --port ${PORT}`
   * Create a **Worker** component called `outboundai-worker`:
     * Set build method: **Dockerfile**.
     * Run Command: `python agent.py start`
5. Go to the **App-Level Settings** -> **Environment Variables** -> Add the environment variables from [`app.yaml`](file:///c:/SSD%20WINDOW/code/bullk-call-agent/app.yaml) or your local `.env`. Ensure sensitive keys (like api keys and secrets) have the **Encrypt** option checked.
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
  `[outbound-agent] INFO: Loaded google.realtime.RealtimeModel`
  `[outbound-agent] INFO: registered worker`

---

## 🛠️ SIP Trunk Configuration (Outbound Calls)

Once both components are successfully deployed:
1. Open your OutboundAI dashboard URL.
2. Go to the **Settings** tab and confirm all credentials (LiveKit, Vobiz, Supabase) are shown as `configured`.
3. Go to the **Setup** tab and click **⚡ Create SIP Trunk**.
4. This registers your Vobiz SIP credentials with LiveKit Cloud.
5. In the pop-up, **copy the generated SIP Trunk ID** (starts with `ST_...`).
6. Go back to your DigitalOcean Control Panel -> your App -> **Settings** -> **Environment Variables**.
7. Locate `OUTBOUND_TRUNK_ID` and replace the placeholder value with the new trunk ID.
8. Click **Save** to trigger a quick redeployment.

Once the redeployment completes, you are fully live! Try dispatching a single call to verify the connection.
