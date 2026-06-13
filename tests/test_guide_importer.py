from pathlib import Path

from p5r_assistant.guide.importer import import_guide_directory, import_guide_file
from p5r_assistant.guide.repository import load_guide, save_guide


def test_imports_rank_table_from_html(tmp_path: Path):
    html = """
    <html><head><title>高卷杏 - 女神转生WIKI</title></head>
    <body>
      <h2>COOP对话攻略</h2>
      <h3>Rank 2</h3>
      <table>
        <tr><th>选项</th><th>好感</th></tr>
        <tr><td>什么意思？</td><td>0</td></tr>
        <tr><td>随便他们怎么说吧</td><td>3</td></tr>
      </table>
    </body></html>
    """
    path = tmp_path / "ann.html"
    path.write_text(html, encoding="utf-8")

    confidant, report = import_guide_file(path)

    assert confidant.name == "高卷杏"
    assert confidant.events[0].rank_to == 2
    assert confidant.events[0].questions[0].choices[1].text == "随便他们怎么说吧"
    assert confidant.events[0].questions[0].choices[1].points == 3
    assert report.warnings == []


def test_import_directory_and_repository_round_trip(tmp_path: Path):
    html_path = tmp_path / "芳泽霞.htm"
    html_path.write_text(
        "<html><head><title>芳泽霞 - 女神转生WIKI</title></head><body>"
        "<h3>Rank 1</h3><table><tr><td>选项A</td><td>1</td></tr></table>"
        "</body></html>",
        encoding="utf-8",
    )

    guide, report = import_guide_directory(tmp_path)
    out = tmp_path / "guide.json"
    save_guide(guide, out)
    loaded = load_guide(out)

    assert report.files_parsed == 1
    assert loaded.confidants[0].name == "芳泽霞"
    assert loaded.confidants[0].events[0].questions[0].choices[0].normalized == "选项A"
