from __future__ import annotations

import argparse
import json
from pathlib import Path

from p5r_assistant import __version__


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

    run = subparsers.add_parser("run")
    run.add_argument("--data-dir", default="data")
    run.add_argument("--htmls", default="htmls")
    run.add_argument("--no-keyboard", action="store_true")
    run.add_argument("--no-gamepad", action="store_true")
    run.add_argument("--recognize-once", action="store_true")
    run.add_argument("--startup-check", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
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

    if args.command == "run":
        from p5r_assistant.runtime import RuntimePaths, build_recognition_service
        from p5r_assistant.ui.tray import DesktopAppConfig, run_app

        paths = RuntimePaths(data_dir=Path(args.data_dir), htmls_dir=Path(args.htmls))
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
