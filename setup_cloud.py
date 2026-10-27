#!/usr/bin/env python3
"""
Interactive Terminal Wizard for Steps 1, 2 & 3 of Cortex60 + VeriPulse Cloud Setup.
Uses your authenticated `gh` CLI (`kujodigital`) to:
1. Create & push the GitHub repository (`kujodigital/cortex60`) if no remote exists yet.
2. Auto-fetch your TELEGRAM_CHAT_ID from your TELEGRAM_BOT_TOKEN and upload Secrets to GitHub.
3. Enable GitHub Pages (`main` -> `/docs`) and trigger the first live cloud workflow run.
"""

import getpass
import json
import subprocess
import urllib.request


def run_cmd(cmd: list[str], input_text: str | None = None, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=check,
    )


def set_gh_secret(name: str, value: str) -> None:
    if not value:
        return
    res = run_cmd(["gh", "secret", "set", name], input_text=value)
    if res.returncode == 0:
        print(f"  ✔ GitHub Secret '{name}' saved.")
    else:
        print(f"  ⚠ Could not save secret '{name}': {res.stderr.strip()}")


def fetch_telegram_chat_id(bot_token: str) -> str:
    url = f"https://api.telegram.org/bot{bot_token.strip()}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("result", [])
            for item in reversed(results):
                msg = item.get("message") or item.get("channel_post") or {}
                chat = msg.get("chat", {})
                if chat.get("id"):
                    return str(chat["id"])
    except Exception as exc:
        print(f"  ⚠ Could not auto-fetch chat ID ({exc}).")
    return ""


def main() -> None:
    print("=" * 68)
    print("☁️  CORTEX60 + VERIPULSE CLOUD SETUP WIZARD (Steps 1, 2 & 3)")
    print("=" * 68)

    # --- STEP 1: Ensure GitHub Remote Repo Exists & Push ---
    rem = run_cmd(["git", "remote", "get-url", "origin"])
    if rem.returncode != 0 or "<your-username>" in rem.stdout:
        print("\n[Step 1] Creating GitHub repository 'cortex60' under your logged-in GitHub account...")
        run_cmd(["git", "remote", "remove", "origin"])
        visibility = input("  Make repository public (required for free GitHub Pages on free tier)? [Y/n]: ").strip().lower()
        vis_flag = "--private" if visibility == "n" else "--public"
        create_res = run_cmd(["gh", "repo", "create", "cortex60", vis_flag, "--source=.", "--remote=origin", "--push"])
        if create_res.returncode == 0:
            print("  ✔ Created and pushed to GitHub repository!")
        else:
            print(f"  ℹ Repo note: {create_res.stderr.strip() or create_res.stdout.strip()}")
            run_cmd(["git", "push", "-u", "origin", "main"])
    else:
        print(f"\n[Step 1] Remote already configured: {rem.stdout.strip()}")
        run_cmd(["git", "push", "-u", "origin", "main"])

    # --- STEP 2: Fetch & Upload Secrets (Telegram / Email / Gemini) ---
    print("\n" + "-" * 68)
    print("[Step 2] Configure Cloud Push Channels (Press Enter to skip any channel)")
    print("-" * 68)

    # 2A. Telegram
    print("\n📱 TELEGRAM SETUP:")
    print("  1. Open Telegram and message @BotFather -> send /newbot -> copy the Bot Token.")
    print("  2. Open a chat with your new bot and send it 'hi' (so we can auto-fetch your Chat ID).")
    bot_token = input("  Paste TELEGRAM_BOT_TOKEN (or press Enter to skip Telegram): ").strip()
    if bot_token:
        chat_id = fetch_telegram_chat_id(bot_token)
        if chat_id:
            print(f"  🎉 Auto-detected your TELEGRAM_CHAT_ID: {chat_id}")
        else:
            input("  👉 Send a message ('hello') to your bot on Telegram now, then press Enter to retry...")
            chat_id = fetch_telegram_chat_id(bot_token)
            if not chat_id:
                chat_id = input("  Enter your numeric TELEGRAM_CHAT_ID manually: ").strip()

        set_gh_secret("ENABLE_TELEGRAM", "true")
        set_gh_secret("TELEGRAM_BOT_TOKEN", bot_token)
        set_gh_secret("TELEGRAM_CHAT_ID", chat_id)

    # 2B. Email (Gmail SMTP)
    print("\n📧 EMAIL (GMAIL SMTP) SETUP:")
    print("  1. Go to https://myaccount.google.com/apppasswords (requires 2FA on your Google account).")
    print("  2. Create an App Password named 'Cortex60' and copy the 16-letter password.")
    smtp_user = input("  Enter your Gmail address (or press Enter to skip Email): ").strip()
    if smtp_user:
        smtp_pass = getpass.getpass("  Paste your 16-char Gmail App Password (hidden): ").strip().replace(" ", "")
        email_to = input(f"  Recipient email address [default: {smtp_user}]: ").strip() or smtp_user
        set_gh_secret("ENABLE_EMAIL", "true")
        set_gh_secret("SMTP_HOST", "smtp.gmail.com")
        set_gh_secret("SMTP_PORT", "587")
        set_gh_secret("SMTP_USER", smtp_user)
        set_gh_secret("SMTP_PASSWORD", smtp_pass)
        set_gh_secret("EMAIL_FROM", smtp_user)
        set_gh_secret("EMAIL_TO", email_to)

    # 2C. Optional Gemini API Key
    print("\n🤖 OPTIONAL AI SYNTHESIS (GEMINI):")
    gemini_key = input("  Paste GEMINI_API_KEY from https://aistudio.google.com/ (or press Enter to skip): ").strip()
    if gemini_key:
        set_gh_secret("GEMINI_API_KEY", gemini_key)

    # --- STEP 3: Enable GitHub Pages & Trigger Cloud Workflow ---
    print("\n" + "-" * 68)
    print("[Step 3] Enabling GitHub Pages (/docs) & Triggering Cloud Workflow...")
    print("-" * 68)

    repo_view = run_cmd(["gh", "repo", "view", "--json", "nameWithOwner"])
    if repo_view.returncode == 0:
        full_name = json.loads(repo_view.stdout)["nameWithOwner"]
        pages_res = run_cmd(
            [
                "gh",
                "api",
                "-X",
                "POST",
                f"repos/{full_name}/pages",
                "-f",
                "source[branch]=main",
                "-f",
                "source[path]=/docs",
            ]
        )
        if pages_res.returncode == 0 or "already" in pages_res.stderr.lower():
            owner, repo_name = full_name.split("/")
            print(f"  ✔ GitHub Pages enabled! Live Web App URL: https://{owner}.github.io/{repo_name}/")
        else:
            print(f"  ℹ GitHub Pages note: {pages_res.stderr.strip()}")

        wf_res = run_cmd(["gh", "workflow", "run", "cloud_cognitive_pulse.yml"])
        if wf_res.returncode == 0:
            print("  🚀 Triggered 'Cortex60 + VeriPulse Serverless Cloud Engine' workflow on GitHub!")
            print(f"  🔗 View live cloud run: https://github.com/{full_name}/actions")
        else:
            print(f"  ℹ Workflow trigger note: {wf_res.stderr.strip()}")

    print("\n✅ Setup complete!")


if __name__ == "__main__":
    main()
