from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from p5r_assistant import __version__


def configure_utf8_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, TypeError, ValueError, OSError):
            continue


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="p5r-assistant")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(dest="command")

    import_guide = subparsers.add_parser("import-guide")
    import_guide.add_argument("--htmls", default="htmls")
    import_guide.add_argument("--out", default="data/guide.json")

    match_text = subparsers.add_parser("match-text")
    match_text.add_argument("choices", nargs="+")
    match_text.add_argument("--guide", default="data/guide.json")

    clean_guide = subparsers.add_parser("clean-guide")
    clean_guide.add_argument("--guide", default="data/guide.json")

    run = subparsers.add_parser("run")
    run.add_argument("--data-dir", default="data")
    run.add_argument("--htmls", default="htmls")
    run.add_argument("--no-keyboard", action="store_true")
    run.add_argument("--no-gamepad", action="store_true")
    run.add_argument("--recognize-once", action="store_true")
    run.add_argument("--startup-check", action="store_true")
    run.add_argument("--debug-capture-dir", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "import-guide":
        from p5r_assistant.guide.importer import import_guide_directory
        from p5r_assistant.guide.repository import save_guide

        guide, report = import_guide_directory(Path(args.htmls))
        save_guide(guide, Path(args.out))
        print(json.dumps({"out": args.out, "warnings": report.warnings}, ensure_ascii=False))
        return 0

    if args.command == "match-text":
        from p5r_assistant.guide.repository import load_guide
        from p5r_assistant.match.aliases import AliasStore
        from p5r_assistant.match.matcher import Matcher

        guide = load_guide(Path(args.guide))
        result = Matcher(guide, AliasStore.empty()).match(args.choices)
        print(json.dumps(result.to_dict(), ensure_ascii=False))
        return 0

    if args.command == "clean-guide":
        from p5r_assistant.guide.importer import clean_guide
        from p5r_assistant.guide.repository import load_guide, save_guide

        path = Path(args.guide)
        guide = load_guide(path)
        before_confidants = len(guide.confidants)
        before_events = sum(len(confidant.events) for confidant in guide.confidants)
        cleaned = clean_guide(guide)
        after_events = sum(len(confidant.events) for confidant in cleaned.confidants)
        save_guide(cleaned, path)
        print(
            json.dumps(
                {
                    "guide": str(path),
                    "confidants_removed": before_confidants - len(cleaned.confidants),
                    "events_removed": before_events - after_events,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if args.command == "run":
        from p5r_assistant.runtime import RuntimePaths, build_recognition_service
        from p5r_assistant.ui.tray import DesktopAppConfig, run_app

        paths = RuntimePaths(
            data_dir=Path(args.data_dir),
            htmls_dir=Path(args.htmls),
            debug_capture_dir=Path(args.debug_capture_dir) if args.debug_capture_dir else None,
        )
        if args.startup_check:
            from p5r_assistant.runtime import ensure_runtime_files

            ensure_runtime_files(paths)
            return 0
        if args.recognize_once:
            build_recognition_service(paths).recognize_once()
            return 0
        return run_app(
            paths,
            DesktopAppConfig(enable_keyboard=not args.no_keyboard, enable_gamepad=not args.no_gamepad),
        )

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
