# OutboundAI — Render Deployment Guide

## Architecture on Render

Render runs **two separate services** from the same repository:

| Service | Type | What it does | Port |
|---|---|---|---|
| `outboundai-web` | Web Service | FastAPI dashboard + REST API | `$PORT` (dynamic) |
| `outboundai-worker` | Background Worker | LiveKit AI voice agent | None (no HTTP) |

Both services share the same environment variable group (`outboundai-config`).

---

## Pre-Requisites

Before deploying to Render, you need these accounts set up:

- [ ] **LiveKit Cloud** account — [cloud.livekit.io](https://cloud.livekit.io) → create a project → get URL, API Key, Secret
- [ ] **Google AI Studio** — [aistudio.google.com](https://aistudio.google.com) → get Gemini API Key
- [ ] **Vobiz** — [vobiz.ai](https://vobiz.ai) → get SIP credentials
- [ ] **Supabase** — [supabase.com](https://supabase.com) → create a project → get URL + Service Key
- [ ] **GitHub** — push this repo to GitHub first

---

## Step 1 — Set Up Supabase Schema

1. Go to your Supabase project → **SQL Editor**
2. Paste the entire contents of `supabase_schema.sql`
3. Click **Run** ✅

---

## Step 2 — Push to GitHub

```bash
cd "c:\SSD WINDOW\code\bullk-call-agent"
git init
git add .
git commit -m "feat: OutboundAI initial deployment"
git remote add origin https://github.com/YOUR_USERNAME/outbound-ai.git
git push -u origin main
```

> Make sure `.env` is in `.gitignore` (it is) — never push real credentials.

---

## Step 3 — Deploy via Render Blueprint (Recommended)

The `render.yaml` file in this repo defines both services automatically.

1. Go to [render.com](https://render.com) → **Dashboard**
2. Click **New** → **Blueprint**
3. Connect your **GitHub** account and select your `outbound-ai` repository
4. Render will detect `render.yaml` and show you two services to create:
   - `outboundai-web` (Web Service)
   - `outboundai-worker` (Background Worker)
5. Click **Apply** — Render starts building both services

---

## Step 4 — Configure Environment Variables

After the services are created, fill in the secret values:

1. Go to **Dashboard** → **Environment** → **Environment Groups**
2. Find `outboundai-config`
3. Fill in every value:

| Variable | Where to get it |
|---|---|
| `LIVEKIT_URL` | LiveKit Cloud → Project → Keys (e.g. `wss://your-project.livekit.cloud`) |
| `LIVEKIT_API_KEY` | LiveKit Cloud → Project → Keys |
| `LIVEKIT_API_SECRET` | LiveKit Cloud → Project → Keys |
| `GOOGLE_API_KEY` | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `GEMINI_MODEL` | `gemini-3.1-flash-live-preview` (already set) |
| `GEMINI_TTS_VOICE` | `Aoede` (already set, change if needed) |
| `VOBIZ_SIP_DOMAIN` | Vobiz dashboard (e.g. `abc123.sip.vobiz.ai`) |
| `VOBIZ_USERNAME` | Vobiz account username |
| `VOBIZ_PASSWORD` | Vobiz account password |
| `VOBIZ_OUTBOUND_NUMBER` | Your Vobiz number in E.164 (e.g. `+919876543210`) |
| `OUTBOUND_TRUNK_ID` | Leave blank — you'll fill this after Step 6 |
| `DEFAULT_TRANSFER_NUMBER` | Fallback human agent number (E.164) |
| `SUPABASE_URL` | Supabase → Project Settings → API → Project URL |
| `SUPABASE_SERVICE_KEY` | Supabase → Project Settings → API → service_role key |

> **Optional vars** (Twilio, S3, Cal.com) can be left blank — features degrade gracefully.

4. Click **Save** — Render will automatically **redeploy** both services with the new values.

---

## Step 5 — Wait for Build + Verify

Build takes 3–5 minutes (installing packages + downloading Silero VAD model).

**Check web service logs** — you should see:
```
✅ Supabase connected
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:XXXXX
```

**Check worker service logs** — you should see:
```
✅ Supabase connected
INFO:server: registered worker {"agent_name": "outbound-caller", ...}
```

If worker shows `registered worker` → **the agent is live and listening for jobs** ✅

---

## Step 6 — Create the Vobiz SIP Trunk

This connects LiveKit to Vobiz so the agent can dial numbers.

1. Open your deployed dashboard URL (shown in Render → `outboundai-web` → service URL)
2. Go to **⚙️ Settings**
3. Verify LiveKit and Vobiz fields are filled (they pull from env vars)
4. Click **⚡ Create SIP Trunk in LiveKit**
5. Copy the returned **Trunk ID** (e.g. `ST_xxxxxxxxxxxxxxxxxx`)
6. Go back to Render → **Environment Groups** → `outboundai-config`
7. Set `OUTBOUND_TRUNK_ID` to the trunk ID
8. Save → Render redeploys automatically

---

## Step 7 — First Test Call

1. Open dashboard → **📞 Single Call**
2. Enter your own phone number (E.164, e.g. `+919876543210`)
3. Fill in Lead Name, Business Name, Service Type
4. Click **⚡ Initiate Call**
5. Your phone rings within 3–5 seconds
6. Priya introduces herself and follows the booking script ✅

---

## Render Service Plans

| Service | Minimum Plan | Notes |
|---|---|---|
| `outboundai-web` | **Free** | Works, but sleeps after 15 min inactivity → first request slow |
| `outboundai-worker` | **Starter ($7/mo)** | Background workers require paid plan on Render |

> **Recommendation**: Use **Starter** for both. Free web + Starter worker = ~$7/mo. The web service going to sleep is acceptable since the dashboard is human-operated.

---

## Render vs Coolify

| Feature | Render | Coolify (VPS) |
|---|---|---|
| Setup time | 10 minutes | 30–60 minutes |
| Cost | $7–14/mo | $4/mo (Hetzner) + your time |
| SSL/HTTPS | Automatic ✅ | Automatic via Caddy ✅ |
| Custom domains | Yes ✅ | Yes ✅ |
| Persistent disk | No (use Supabase) | Yes |
| Two-process apps | Two services ✅ | start.sh in Docker ✅ |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Worker shows `OUTBOUND_TRUNK_ID not set` | Complete Step 6 — set trunk ID in env group |
| `Supabase connection failed` | Check `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` are correct |
| `registered worker` not appearing | Check `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` |
| Agent goes silent mid-call | All 3 silence-prevention configs are applied — check Gemini API key quota |
| Dashboard loads but API calls fail | Both services use same env group — check all vars are saved |
| Build fails on `libgomp1` | Only happens with Docker deploy; native Python runtime installs skip this |
| Worker restarts every few minutes | Normal — LiveKit agent reconnects after idle timeout |

---

## Local Development

To test locally before pushing to Render:

```bash
# 1. Copy env template
cp .env.example .env
# Edit .env with real values

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download VAD model
python agent.py download-files

# 4. Terminal 1: Start FastAPI
uvicorn server:app --host 0.0.0.0 --port 8000

# 5. Terminal 2: Start agent worker
python agent.py start

# 6. Open: http://localhost:8000
```
