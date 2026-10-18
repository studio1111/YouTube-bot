import json
from yt_agent.branding import build_brand_kit
from yt_agent.trends import discover_trends, parse_rss_xml, rank_topics


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Science Feed</title>
    <item>
      <title>Why quantum batteries could charge faster than lithium cells</title>
      <link>https://example.com/quantum-batteries</link>
    </item>
    <item>
      <title>How deep ocean microbes survive without sunlight</title>
      <link>https://example.com/ocean-microbes</link>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_and_rank_topics(tmp_path):
    items = parse_rss_xml(SAMPLE_RSS, source_url="https://example.com/rss")
    assert len(items) == 2
    ranked = rank_topics(items, niche_keywords=["quantum"])
    assert ranked[0]["title"].startswith("Why quantum batteries")
    assert ranked[0]["score"] > ranked[1]["score"]

    out = discover_trends(
        "quantum batteries",
        runtime_dir=str(tmp_path),
        offline_seeds=["Why quantum batteries could change grid storage"],
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["top_pick"]["title"] == "Why quantum batteries could change grid storage"


def test_build_brand_kit_creates_svg_assets(tmp_path):
    manifest_path = build_brand_kit("Deep Cosmos", "Space explained clearly", runtime_dir=str(tmp_path))
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    out_dir = manifest_path.parent
    for key, filename in data["assets"].items():
        svg_file = out_dir / filename
        assert svg_file.exists(), f"Missing {key}"
        assert "<svg" in svg_file.read_text(encoding="utf-8")
