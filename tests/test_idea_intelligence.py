import json
from yt_agent.idea_intelligence import TrendItem, build_idea_report, dedupe_items, extract_hooks, rank_items
from yt_agent.scenario_prompts import build_prompt, generate_scenario


def test_cross_platform_dedupe_and_hook_extraction(tmp_path):
    items = [
        TrendItem("youtube", "Why quantum batteries could change storage", "https://youtube/a", likes=1000, comments=20),
        TrendItem("tiktok", "Why quantum batteries could change storage", "https://tiktok/a", likes=800, comments=30),
        TrendItem("instagram", "How deep ocean microbes survive", "https://instagram/b", likes=200, comments=5),
    ]
    deduped = dedupe_items(items)
    assert len(deduped) == 2
    ranked = rank_items(deduped, "quantum batteries")
    assert ranked[0]["platform"] == "youtube"
    assert extract_hooks(deduped)[0]["hook_style"] == "why-question"
    report = build_idea_report("quantum batteries", str(tmp_path), items)
    assert json.loads(report.read_text())["schema"] == "yt-agent.idea-intelligence.v1"


def test_prompt_has_rights_and_schema_guardrails():
    prompt = build_prompt({"title": "A test idea"})
    assert "Do not copy wording" in prompt
    assert "valid JSON" in prompt
    fallback = generate_scenario({"title": "A test idea"})
    assert fallback["prompt_version"] == "scenario-v1"
    assert fallback["risk_flags"]
