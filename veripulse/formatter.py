import html
from veripulse.models import VerifiedStory


def format_chat_message(story: VerifiedStory) -> str:
    """Formats a VerifiedStory for Telegram / WhatsApp / Plain-text alerts."""
    pointers_block = "\n".join(f"• {p}" for p in story.important_pointers)
    sources_block = "\n".join(f"🔗 {s.label}: {s.url}" for s in story.sources)

    return (
        f"{story.badge_emoji} *[{story.category}] {story.headline}*\n"
        f"🛡️ *Status:* {story.verification_status.value}  |  *Trust Score:* {story.trust_score}/100\n\n"
        f"⚡ *QUICK BITE (Zero Fluff)*\n"
        f"{story.quick_bite}\n\n"
        f"📌 *IMPORTANT POINTERS (The Story)*\n"
        f"{pointers_block}\n\n"
        f"🔍 *COMMUNITY & FACT-CHECK CONTEXT*\n"
        f"{story.community_verification_notes}\n\n"
        f"📚 *VERIFIED SOURCES*\n"
        f"{sources_block}"
    )


def format_telegram_html(story: VerifiedStory) -> str:
    """Formats a VerifiedStory using Telegram HTML parse_mode for clean clickable links."""
    e = html.escape
    pointers_block = "\n".join(f"• {e(p)}" for p in story.important_pointers)
    sources_block = "\n".join(
        f'• <a href="{e(s.url)}">{e(s.label)}</a>' for s in story.sources
    )

    return (
        f"{story.badge_emoji} <b>[{e(story.category)}] {e(story.headline)}</b>\n"
        f"🛡️ <b>Status:</b> <code>{e(story.verification_status.value)}</code> | <b>Trust:</b> <code>{story.trust_score}/100</code>\n\n"
        f"⚡ <b>QUICK BITE (Zero Fluff)</b>\n"
        f"{e(story.quick_bite)}\n\n"
        f"📌 <b>IMPORTANT POINTERS (The Story)</b>\n"
        f"{pointers_block}\n\n"
        f"🔍 <b>COMMUNITY &amp; FACT-CHECK</b>\n"
        f"<i>{e(story.community_verification_notes)}</i>\n\n"
        f"🔗 <b>VERIFIED SOURCES</b>\n"
        f"{sources_block}"
    )


def format_email_html(stories: list[VerifiedStory]) -> str:
    """Formats one or more VerifiedStory items into a sleek, zero-fluff HTML Email."""
    e = html.escape
    cards_html = []
    for s in stories:
        badge_color = "#10b981" if s.trust_score >= 80 else ("#f59e0b" if s.trust_score >= 60 else "#ef4444")
        pointers_li = "".join(f"<li style='margin-bottom:6px;'>{e(p)}</li>" for p in s.important_pointers)
        sources_li = "".join(
            f"<li style='margin-bottom:4px;'><a href='{e(src.url)}' style='color:#2563eb;text-decoration:none;font-weight:500;'>{e(src.label)}</a></li>"
            for src in s.sources
        )
        cards_html.append(
            f"""
            <div style="border:1px solid #e2e8f0; border-radius:10px; padding:20px; margin-bottom:20px; background:#ffffff;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="background:#0f172a; color:#f8fafc; font-size:11px; font-weight:700; padding:4px 8px; border-radius:4px; letter-spacing:0.5px;">
                        {e(s.category)}
                    </span>
                    <span style="background:{badge_color}; color:#ffffff; font-size:11px; font-weight:700; padding:4px 8px; border-radius:4px;">
                        {s.badge_emoji} {e(s.verification_status.value)} • {s.trust_score}/100
                    </span>
                </div>
                <h2 style="margin:6px 0 12px 0; font-size:18px; color:#0f172a; line-height:1.35;">{e(s.headline)}</h2>

                <div style="background:#f8fafc; border-left:4px solid #3b82f6; padding:12px; margin-bottom:14px; border-radius:0 6px 6px 0;">
                    <div style="font-size:11px; font-weight:700; color:#1d4ed8; text-transform:uppercase; margin-bottom:4px;">⚡ Quick Bite (Zero Fluff)</div>
                    <div style="font-size:14px; color:#1e293b; line-height:1.5;">{e(s.quick_bite)}</div>
                </div>

                <div style="margin-bottom:14px;">
                    <div style="font-size:12px; font-weight:700; color:#334155; text-transform:uppercase; margin-bottom:6px;">📌 Important Pointers (The Story)</div>
                    <ul style="margin:0; padding-left:20px; font-size:14px; color:#334155; line-height:1.5;">
                        {pointers_li}
                    </ul>
                </div>

                <div style="background:#fefce8; border:1px solid #fef08a; padding:10px 12px; border-radius:6px; margin-bottom:14px;">
                    <div style="font-size:11px; font-weight:700; color:#854d0e; text-transform:uppercase; margin-bottom:3px;">🔍 Community &amp; Fact-Check Verification</div>
                    <div style="font-size:13px; color:#713f12; line-height:1.45;">{e(s.community_verification_notes)}</div>
                </div>

                <div>
                    <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; margin-bottom:4px;">🔗 Verified Sources</div>
                    <ul style="margin:0; padding-left:18px; font-size:13px;">
                        {sources_li}
                    </ul>
                </div>
            </div>
            """
        )

    body_cards = "\n".join(cards_html)
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; background:#f1f5f9; padding:24px; margin:0;">
        <div style="max-width:660px; margin:0 auto;">
            <div style="margin-bottom:18px;">
                <h1 style="margin:0; font-size:22px; color:#0f172a;">📡 VeriPulse Real-Time Verified Brief</h1>
                <p style="margin:4px 0 0 0; font-size:13px; color:#475569;">Zero fluff • Multi-source corroborated • Community fact-checked</p>
            </div>
            {body_cards}
        </div>
    </body>
    </html>
    """
