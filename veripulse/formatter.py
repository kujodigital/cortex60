from datetime import datetime, timezone
import html
from veripulse.models import VerifiedStory


def format_chat_message(story: VerifiedStory) -> str:
    """Formats a VerifiedStory for WhatsApp / Plain-text alerts with 4-Layer What/How/Why/Why/Why Q&A."""
    pointers_block = "\n".join(f"• {p}" for p in story.important_pointers)
    layers_block = "\n\n".join(
        f"🔹 *[{l.layer_tag}]*\n*Q:* {l.question}\n*A:* {l.answer}"
        for l in story.interrogation_layers
    )
    sources_block = "\n".join(f"🔗 {s.label}: {s.url}" for s in story.sources)

    return (
        f"{story.badge_emoji} *[{story.category}] {story.headline}*\n"
        f"🛡️ *Status:* {story.verification_status.value}  |  *Trust Score:* {story.trust_score}/100\n\n"
        f"⚡ *QUICK BITE (Zero Fluff)*\n"
        f"{story.quick_bite}\n\n"
        f"📌 *IMPORTANT POINTERS (The Story)*\n"
        f"{pointers_block}\n\n"
        f"🔬 *DEEP INTERROGATION (WHAT • HOW • WHY • WHY • WHY)*\n"
        f"{layers_block}\n\n"
        f"🔍 *COMMUNITY & FACT-CHECK CONTEXT*\n"
        f"{story.community_verification_notes}\n\n"
        f"📚 *VERIFIED SOURCES*\n"
        f"{sources_block}"
    )


def format_telegram_html(story: VerifiedStory) -> str:
    """Formats a VerifiedStory using Telegram HTML parse_mode with full What/How/Why/Why/Why Q&A."""
    e = html.escape
    pointers_block = "\n".join(f"• {e(p)}" for p in story.important_pointers)
    layers_block = "\n\n".join(
        f"🔹 <b>[{e(l.layer_tag)}]</b>\n<b>Q:</b> {e(l.question)}\n<b>A:</b> {e(l.answer)}"
        for l in story.interrogation_layers
    )
    sources_block = "\n".join(
        f'• <a href="{e(s.url)}">{e(s.label)} ↗</a>' for s in story.sources
    )

    return (
        f"{story.badge_emoji} <b>[{e(story.category)}] {e(story.headline)}</b>\n"
        f"🛡️ <b>Status:</b> <code>{e(story.verification_status.value)}</code> | <b>Trust:</b> <code>{story.trust_score}/100</code>\n\n"
        f"⚡ <b>QUICK BITE (Zero Fluff)</b>\n"
        f"{e(story.quick_bite)}\n\n"
        f"📌 <b>IMPORTANT POINTERS (The Story)</b>\n"
        f"{pointers_block}\n\n"
        f"🔬 <b>DEEP INTERROGATION (WHAT • HOW • 3× WHY)</b>\n"
        f"{layers_block}\n\n"
        f"🔍 <b>COMMUNITY &amp; FACT-CHECK</b>\n"
        f"<i>{e(story.community_verification_notes)}</i>\n\n"
        f"🔗 <b>VERIFIED SOURCES</b>\n"
        f"{sources_block}"
    )


def format_email_html(stories: list[VerifiedStory]) -> str:
    """Formats VerifiedStory items into an executive, Gmail-optimized HTML Intelligence Briefing."""
    e = html.escape
    date_str = datetime.now(timezone.utc).strftime("%b %d, %Y • %H:%M UTC")
    cards_html = []

    for idx, s in enumerate(stories, start=1):
        is_protocol = "PROTOCOL" in s.category.upper()
        badge_bg = "#059669" if s.trust_score >= 80 else ("#d97706" if s.trust_score >= 60 else "#dc2626")
        cat_bg = "#4f46e5" if is_protocol else "#0f172a"
        card_border = "#6366f1" if is_protocol else "#cbd5e1"

        pointers_rows = "".join(
            f"""
            <tr>
              <td valign="top" style="padding:0 10px 10px 0; color:#4f46e5; font-weight:800; font-size:15px;">▪</td>
              <td valign="top" style="padding:0 0 10px 0; color:#1e293b; font-size:14.5px; line-height:1.6;">{e(p)}</td>
            </tr>
            """
            for p in s.important_pointers
        )

        # Render the 4-Layer What / How / Why #1 / Why #2 / Why #3 Interrogation Q&A cards
        layers_blocks = []
        for l_idx, layer in enumerate(s.interrogation_layers, start=1):
            accent_bar = ["#2563eb", "#7c3aed", "#0891b2", "#059669"][(l_idx - 1) % 4]
            layers_blocks.append(
                f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid {accent_bar}; border-radius:8px; padding:14px 16px; margin-bottom:10px;">
                  <div style="font-size:10.5px; font-weight:800; color:{accent_bar}; letter-spacing:0.6px; text-transform:uppercase; margin-bottom:5px;">
                    {e(layer.layer_tag)}
                  </div>
                  <div style="font-size:14px; font-weight:700; color:#0f172a; line-height:1.45; margin-bottom:8px;">
                    <span style="color:{accent_bar};">Q:</span> {e(layer.question)}
                  </div>
                  <div style="background:#f8fafc; border-radius:6px; padding:10px 12px; font-size:13.8px; color:#1e293b; line-height:1.6; border:1px solid #e2e8f0;">
                    <strong style="color:#059669;">A:</strong> {e(layer.answer)}
                  </div>
                </div>
                """
            )
        layers_html = "".join(layers_blocks)

        # Render clickable pill buttons for verified sources
        source_pills = "".join(
            f"""
            <a href="{e(src.url)}" target="_blank" rel="noopener"
               style="display:inline-block; background:#f1f5f9; color:#0f172a; border:1px solid #cbd5e1; border-radius:999px; padding:6px 13px; margin:0 6px 8px 0; font-size:12px; font-weight:600; text-decoration:none;">
               🔗 {e(src.label)} <span style="color:#2563eb;">↗</span>
            </a>
            """
            for src in s.sources
        )

        interrogation_heading = (
            "🧠 4×15-MINUTE COGNITIVE BLOCKS — QUESTIONS &amp; COMPLETE ANSWERS"
            if is_protocol
            else "🔬 4-LAYER FIRST-PRINCIPLES INTERROGATION (WHAT • HOW • WHY • WHY • WHY)"
        )

        cards_html.append(
            f"""
            <div style="background:#ffffff; border:1.5px solid {card_border}; border-radius:14px; margin-bottom:26px; overflow:hidden; box-shadow:0 4px 12px rgba(15,23,42,0.05);">
              <!-- Card Top Bar (Email-safe 2-column table) -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f8fafc; border-bottom:1px solid #e2e8f0; padding:12px 22px;">
                <tr>
                  <td align="left" valign="middle">
                    <span style="display:inline-block; background:{cat_bg}; color:#ffffff; font-size:11px; font-weight:800; padding:5px 10px; border-radius:6px; letter-spacing:0.6px; text-transform:uppercase;">
                      #{idx:02d} • {e(s.category)}
                    </span>
                  </td>
                  <td align="right" valign="middle">
                    <span style="display:inline-block; background:{badge_bg}; color:#ffffff; font-size:11px; font-weight:800; padding:5px 10px; border-radius:6px; letter-spacing:0.4px;">
                      {s.badge_emoji} {e(s.verification_status.value)} • {s.trust_score}/100
                    </span>
                  </td>
                </tr>
              </table>

              <div style="padding:22px;">
                <!-- Story Headline -->
                <h2 style="margin:0 0 16px 0; font-size:20px; font-weight:800; color:#0f172a; line-height:1.38; letter-spacing:-0.2px;">
                  {e(s.headline)}
                </h2>

                <!-- Quick Bite Callout -->
                <div style="background:#eef2ff; border-left:4px solid #4f46e5; padding:14px 16px; margin-bottom:20px; border-radius:0 8px 8px 0;">
                  <div style="font-size:11px; font-weight:800; color:#4338ca; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:5px;">
                    ⚡ THE QUICK BITE (ZERO FLUFF)
                  </div>
                  <div style="font-size:15px; font-weight:500; color:#1e1b4b; line-height:1.6;">
                    {e(s.quick_bite)}
                  </div>
                </div>

                <!-- Important Story Pointers -->
                <div style="margin-bottom:20px;">
                  <div style="font-size:11.5px; font-weight:800; color:#334155; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:10px;">
                    📌 IMPORTANT POINTERS (THE VERIFIED STORY)
                  </div>
                  <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    {pointers_rows}
                  </table>
                </div>

                <!-- 4-Layer Deep Interrogation (What / How / Why #1 / Why #2 / Why #3) with Full Answers -->
                <div style="background:#f1f5f9; border:1px solid #cbd5e1; border-radius:10px; padding:16px; margin-bottom:18px;">
                  <div style="font-size:11.5px; font-weight:800; color:#0f172a; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:12px;">
                    {interrogation_heading}
                  </div>
                  {layers_html}
                </div>

                <!-- Community & Fact-Check Verification -->
                <div style="background:#fffbeb; border:1px solid #fde68a; padding:12px 15px; border-radius:8px; margin-bottom:18px;">
                  <div style="font-size:11px; font-weight:800; color:#92400e; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">
                    🔍 COMMUNITY &amp; MULTI-SOURCE VERIFICATION
                  </div>
                  <div style="font-size:13.5px; color:#78350f; line-height:1.55;">
                    {e(s.community_verification_notes)}
                  </div>
                </div>

                <!-- Verified Source Pills -->
                <div>
                  <div style="font-size:11px; font-weight:800; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px;">
                    📚 VERIFIED SOURCES &amp; PRIMARY LINKS
                  </div>
                  <div>
                    {source_pills}
                  </div>
                </div>
              </div>
            </div>
            """
        )

    body_cards = "\n".join(cards_html)
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Kujo Brainiache Intelligence Brief</title>
    </head>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; background-color:#e2e8f0; padding:24px 12px; margin:0; color:#0f172a;">
      <div style="max-width:680px; margin:0 auto;">

        <!-- Executive Dark Masthead -->
        <div style="background:#0f172a; color:#f8fafc; border-radius:14px; padding:24px 26px; margin-bottom:24px; border-bottom:4px solid #38bdf8;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0">
            <tr>
              <td align="left" valign="middle">
                <div style="font-size:11px; font-weight:800; color:#38bdf8; letter-spacing:1.2px; text-transform:uppercase; margin-bottom:6px;">
                  🧠 KUJO BRAINIACHE // CLOUD INTELLIGENCE ENGINE
                </div>
                <h1 style="margin:0 0 6px 0; font-size:24px; font-weight:800; color:#ffffff; letter-spacing:-0.4px;">
                  Kujo Brainiache — Real-Time Verified Brief &amp; Deep-Why Interrogation
                </h1>
                <div style="font-size:13px; color:#94a3b8;">
                  Zero fluff • 4-Layer What/How/Why/Why/Why Analysis • Complete Answer Keys • {e(date_str)}
                </div>
              </td>
            </tr>
          </table>
          <div style="margin-top:16px; padding-top:14px; border-top:1px solid #1e293b;">
            <a href="https://kujodigital.github.io/cortex60/" target="_blank" rel="noopener"
               style="display:inline-block; background:#38bdf8; color:#0f172a; font-size:12.5px; font-weight:800; padding:8px 16px; border-radius:8px; text-decoration:none;">
               🧠 Open Kujo Brainiache Web App ↗
            </a>
          </div>
        </div>

        <!-- Story & Cognitive Cards -->
        {body_cards}

        <!-- Footer -->
        <div style="text-align:center; font-size:12px; color:#475569; padding:12px 0 28px;">
          Generated autonomously by <strong>Kujo Brainiache Serverless Cloud Engine</strong> •
          <a href="https://kujodigital.github.io/cortex60/" style="color:#2563eb; text-decoration:none; font-weight:600;">Kujo Brainiache Web App</a> •
          <a href="https://github.com/kujodigital/cortex60/actions" style="color:#2563eb; text-decoration:none; font-weight:600;">GitHub Cloud Runs</a>
        </div>
      </div>
    </body>
    </html>
    """
