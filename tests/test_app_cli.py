import json
from pathlib import Path

from p5r_assistant.app import main


def test_cli_import_guide_writes_json(tmp_path: Path, capsys):
    htmls = tmp_path / "htmls"
    htmls.mkdir()
    (htmls / "高卷杏.htm").write_text(
        "<html><head><title>高卷杏 - 女神转生WIKI</title></head><body>"
        "<h3>Rank 2</h3><table><tr><td>什么意思？</td><td>0</td></tr>"
        "<tr><td>随便他们怎么说吧</td><td>3</td></tr></table></body></html>",
        encoding="utf-8",
    )
    out = tmp_path / "guide.json"

    assert main(["import-guide", "--htmls", str(htmls), "--out", str(out)]) == 0

    assert out.exists()
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["confidants"][0]["name"] == "高卷杏"
    assert json.loads(capsys.readouterr().out)["out"] == str(out)


def test_cli_match_text_outputs_recommendation(tmp_path: Path, capsys):
    htmls = tmp_path / "htmls"
    htmls.mkdir()
    (htmls / "高卷杏.htm").write_text(
        "<html><head><title>高卷杏 - 女神转生WIKI</title></head><body>"
        "<h3>Rank 2</h3><table><tr><td>什么意思？</td><td>0</td></tr>"
        "<tr><td>随便他们怎么说吧</td><td>3</td></tr></table></body></html>",
        encoding="utf-8",
    )
    guide = tmp_path / "guide.json"
    main(["import-guide", "--htmls", str(htmls), "--out", str(guide)])
    capsys.readouterr()

    assert main(["match-text", "什么意思？", "随便他们怎么说吧", "--guide", str(guide)]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["recommendation"]["choice"]["index"] == 2


def test_cli_clean_guide_rewrites_json_with_rank_up_events_only(tmp_path: Path, capsys):
    guide = tmp_path / "guide.json"
    guide.write_text(
        json.dumps(
            {
                "version": 1,
                "generated_at": "now",
                "source_dir": "tests",
                "confidants": [
                    {
                        "id": "ann",
                        "name": "高卷杏",
                        "events": [
                            {
                                "id": "ann_meta",
                                "type": "unknown",
                                "questions": [{"id": "ann_meta_q1", "choices": [{"id": "c1", "index": 1, "text": "姓名", "normalized": "姓名", "points": 0}]}],
                            },
                            {
                                "id": "ann_rank_2",
                                "type": "rank_up",
                                "rank_from": 1,
                                "rank_to": 2,
                                "title": "Rank 2",
                                "questions": [{"id": "ann_rank_2_q1", "choices": [{"id": "c2", "index": 1, "text": "什么意思？", "normalized": "什么意思？", "points": 0}]}],
                            },
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert main(["clean-guide", "--guide", str(guide)]) == 0

    payload = json.loads(guide.read_text(encoding="utf-8"))
    assert [event["id"] for event in payload["confidants"][0]["events"]] == ["ann_rank_2"]
    assert json.loads(capsys.readouterr().out)["events_removed"] == 1


def test_cli_run_startup_check_returns_zero(tmp_path: Path):
    htmls = tmp_path / "htmls"
    htmls.mkdir()
    (htmls / "高卷杏.htm").write_text(
        "<html><head><title>高卷杏 - 女神转生WIKI</title></head><body>"
        "<h3>Rank 2</h3><table><tr><td>什么意思？</td><td>0</td></tr></table></body></html>",
        encoding="utf-8",
    )

    assert main(["run", "--startup-check", "--data-dir", str(tmp_path / "data"), "--htmls", str(htmls)]) == 0
