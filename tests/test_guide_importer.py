from pathlib import Path

from p5r_assistant.guide.importer import clean_guide, import_guide_directory, import_guide_file
from p5r_assistant.guide.repository import load_guide, save_guide
from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question


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


def test_import_only_keeps_rank_tables_inside_rank_up_section(tmp_path: Path):
    html = """
    <html><head><title>高卷杏 - 女神转生WIKI</title></head>
    <body>
      <table><tr><td>姓名</td><td>高卷杏</td></tr></table>
      <h2>提升事件</h2>
      <h3>Rank 2</h3>
      <table>
        <tr><th>选项</th><th>好感</th></tr>
        <tr><td>什么意思？</td><td>0</td></tr>
        <tr><td>随便他们怎么说吧</td><td>3</td></tr>
      </table>
      <h2>Rank等级提升效果</h2>
      <table><tr><td>RANK</td><td>Max</td><td>解锁</td></tr></table>
      <h2>P5R导航</h2>
      <h3>Rank 5</h3>
      <table><tr><td>角色页面</td><td>链接</td></tr></table>
    </body></html>
    """
    path = tmp_path / "ann.html"
    path.write_text(html, encoding="utf-8")

    confidant, report = import_guide_file(path)

    assert report.warnings == []
    assert len(confidant.events) == 1
    event = confidant.events[0]
    assert event.type == "rank_up"
    assert event.rank_to == 2
    assert [choice.text for choice in event.questions[0].choices] == ["什么意思？", "随便他们怎么说吧"]


def test_import_splits_rank_up_grid_table_into_question_choice_groups(tmp_path: Path):
    html = """
    <html><head><title>三岛由辉 - 女神转生WIKI</title></head>
    <body>
      <h3>提升事件</h3>
      <table>
        <tr><td colspan="4">月亮：提升事件</td></tr>
        <tr><td>等级</td><td>问题</td><td>选择项</td><td>好感度(持有对应P)</td></tr>
        <tr><td>1→2</td><td>触发条件</td><td>无</td></tr>
        <tr><td>1</td><td>情报战略?</td><td>—</td></tr>
        <tr><td>怪频?</td><td>—</td></tr>
        <tr><td>2</td><td>不愧是你</td><td>15(15)</td></tr>
        <tr><td>好像很麻烦</td><td>—</td></tr>
        <tr><td>电话</td><td>不愧是宣传部长</td><td>5(10)</td></tr>
        <tr><td>冷静点</td><td>—</td></tr>
        <tr><td>2→3</td><td>触发条件</td><td>雨天以外</td></tr>
        <tr><td>1</td><td>头一次听说</td><td>—</td></tr>
        <tr><td>做得好</td><td>10(15)</td></tr>
      </table>
    </body></html>
    """
    path = tmp_path / "mishima.html"
    path.write_text(html, encoding="utf-8")

    confidant, report = import_guide_file(path)

    assert report.warnings == []
    assert [event.rank_to for event in confidant.events] == [2, 3]
    assert [[choice.text for choice in question.choices] for question in confidant.events[0].questions] == [
        ["情报战略?", "怪频?"],
        ["不愧是你", "好像很麻烦"],
        ["不愧是宣传部长", "冷静点"],
    ]
    assert [choice.points for choice in confidant.events[0].questions[1].choices] == [15, 0]


def test_clean_guide_removes_non_rank_up_events_and_empty_confidants():
    rank_choice = Choice("ann_rank_2_q1_c1", 1, "什么意思？", "什么意思？", 0)
    metadata_choice = Choice("ann_meta_q1_c1", 1, "姓名", "姓名", 0)
    guide = Guide(
        version=1,
        generated_at="now",
        source_dir="tests",
        confidants=[
            Confidant(
                "ann",
                "高卷杏",
                [
                    Event("ann_meta", "unknown", [Question("ann_meta_q1", [metadata_choice])]),
                    Event("ann_rank_2", "rank_up", [Question("ann_rank_2_q1", [rank_choice])], 1, 2, "Rank 2"),
                ],
            ),
            Confidant("empty", "空数据", [Event("empty_meta", "unknown", [Question("empty_q1", [metadata_choice])])]),
        ],
    )

    cleaned = clean_guide(guide)

    assert [confidant.name for confidant in cleaned.confidants] == ["高卷杏"]
    assert [event.id for event in cleaned.confidants[0].events] == ["ann_rank_2"]
