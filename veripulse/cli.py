import argparse
import uvicorn
from rich.console import Console
from veripulse.watcher import VeriPulseEngine

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="veripulse",
        description="VeriPulse: Zero-Fluff, Multi-Source Fact-Checked News & Discussion Messenger",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. scan: Run one verification cycle immediately
    scan_parser = subparsers.add_parser("scan", help="Fetch, cross-verify, and dispatch high-signal stories once")
    scan_parser.add_argument("--limit", type=int, default=4, help="Maximum stories to verify in this scan")
    scan_parser.add_argument("--ignore-seen", action="store_true", help="Re-verify even if previously seen")

    # 2. watch: Continuous real-time high-signal alert daemon
    subparsers.add_parser("watch", help="Run continuous real-time watcher for breaking high-signal discussions")

    # 3. verify-url: Verify any specific URL on demand
    url_parser = subparsers.add_parser("verify-url", help="Fact-check and extract zero-fluff pointers from a single URL")
    url_parser.add_argument("url", help="URL of a Reddit thread, Medium article, or News story")
    url_parser.add_argument("--notify", action="store_true", help="Also dispatch to enabled Telegram/Email/WhatsApp")

    # 4. serve: Start FastAPI web server & dashboard
    serve_parser = subparsers.add_parser("serve", help="Start FastAPI server and web feed preview")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")

    args = parser.parse_args()
    engine = VeriPulseEngine()

    if args.command == "scan":
        stories, dispatch_info = engine.run_cycle(ignore_seen=args.ignore_seen, max_items=args.limit)
        console.print(f"\n[bold green]✔ Scan finished:[/bold green] {len(stories)} verified high-signal stories processed.")
        for ch, msg in dispatch_info.items():
            console.print(f"  • [cyan]{ch}[/cyan]: {msg}")

    elif args.command == "watch":
        engine.watch_forever()

    elif args.command == "verify-url":
        story = engine.verify_single_url(args.url)
        if args.notify:
            res = engine.dispatcher.dispatch([story])
            console.print(f"[bold green]✔ Dispatched:[/bold green] {res}")

    elif args.command == "serve":
        console.print(f"[bold green]Starting VeriPulse server at http://127.0.0.1:{args.port}[/bold green]")
        uvicorn.run("veripulse.api:app", host="127.0.0.1", port=args.port, reload=False)


if __name__ == "__main__":
    main()
