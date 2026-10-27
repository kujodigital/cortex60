# ☁️ Running Cortex60 + VeriPulse in the Cloud (100% Free via GitHub Actions & GitHub Pages)

Your repository now unifies **VeriPulse** (Live Reddit, Medium, BBC, and Hacker News multi-source fact-checker) with **Cortex60** (1-Hour Cognitive Enhancement App).

Every time the cloud schedule runs, it:
1. **Polls & Cross-Verifies Live Sources**: Pulls breaking discussions and articles from Reddit (`r/worldnews`, `r/technology`, `r/science`), Medium tags, BBC News, Ars Technica, Nature News, and Hacker News.
2. **Feeds Live Verified Modules into Cortex60**: Converts verified stories into **Block 1 (The Insight Engine)** 10-minute reading modules + 5-minute active recall questions and adds them to **Block 4 (SM-2 Spaced Repetition)**.
3. **Pushes a Unified Briefing to Your Phone/Inbox**: Sends the Zero-Fluff Verified News Pointers + your Daily 4 × 15-Minute Cognitive Protocol (including a daily Logic Crucible puzzle, Mental Model application, and Weak-Concept SRS recall) to **Telegram**, **Email**, and **WhatsApp**.
4. **Updates Your Live Cloud Web App (`docs/`)**: Exports the latest verified state to `docs/api_bootstrap.json` so **GitHub Pages** hosts your interactive Cortex60 dashboard at `https://<your-username>.github.io/<repo-name>/` for free.

---

## 🚀 3-Step Cloud Deployment (0$/month)

### Step 1: Push this folder to a GitHub Repository
```bash
cd /Users/kujo/.gemini/antigravity/scratch/cortex60
git init
git add .
git commit -m "Initial commit: Unified Cortex60 + VeriPulse Cloud Engine"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Step 2: Add Your Notification Secrets in GitHub
In your GitHub repository, go to **Settings → Secrets and variables → Actions → New repository secret** and add whichever channels you want enabled:

| Secret Name | Value / Description |
| :--- | :--- |
| `ENABLE_TELEGRAM` | `true` |
| `TELEGRAM_BOT_TOKEN` | Token from `@BotFather` on Telegram |
| `TELEGRAM_CHAT_ID` | Your numeric Telegram Chat ID |
| `ENABLE_EMAIL` | `true` |
| `SMTP_USER` | Your Gmail address (e.g. `you@gmail.com`) |
| `SMTP_PASSWORD` | Your 16-character Google App Password |
| `EMAIL_TO` | Recipient email address |
| `GEMINI_API_KEY` | *(Optional)* Free API key from Google AI Studio for LLM synthesis |
| `ENABLE_WHATSAPP` | `true` *(Whenever you are ready to turn on WhatsApp)* |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `WHATSAPP_TO` | `whatsapp:+91...` |

### Step 3: Enable Free Cloud Web Dashboard (GitHub Pages) & Trigger First Run
1. In your GitHub repo, go to **Settings → Pages**.
2. Under **Build and deployment**, select **Deploy from a branch**, choose branch `main`, and folder `/docs`, then click **Save**.
3. Go to the **Actions** tab → select **Cortex60 + VeriPulse Serverless Cloud Engine** → click **Run workflow**.
4. Within ~45 seconds, you will receive the verified briefing on Telegram/Email, and your live interactive web app will be online!
