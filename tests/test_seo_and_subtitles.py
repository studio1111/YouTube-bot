import json
from yt_agent.seo import write_seo_package
from yt_agent.subtitles import write_subtitles


def test_seo_and_subtitles_generation(tmp_path):
    script = (
        "The sky is not blue because of the ocean.\n\n"
        "Earth's atmosphere scatters short blue wavelengths strongly.\n\n"
        "At sunset, light travels through thicker air, leaving warm reds."
    )
    srt_path, vtt_path = write_subtitles(tmp_path, script, seconds_per_segment=5.0)
    assert "00:00:00,000 --> 00:00:05,000" in srt_path.read_text(encoding="utf-8")
    assert "WEBVTT" in vtt_path.read_text(encoding="utf-8")

    seo_path = write_seo_package(tmp_path, "Why the sky changes color", script, sources=["https://example.com/sky"])
    seo = json.loads(seo_path.read_text(encoding="utf-8"))
    assert "Why the sky changes color" in seo["primary_title"]
    assert len(seo["chapters"]) == 3
    assert "00:00 Intro:" in seo["description"]
    assert "https://example.com/sky" in seo["description"]
