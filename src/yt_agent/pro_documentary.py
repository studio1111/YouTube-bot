import json
import math
import random
import shutil
import struct
import subprocess
import wave
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def fa(text: str) -> str:
        return get_display(arabic_reshaper.reshape(text))
except Exception:
    def fa(text: str) -> str:
        return text

work = Path("/tmp/pro_yt_episode")
shutil.rmtree(work, ignore_errors=True)
frames_dir = work / "frames"
frames_dir.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
FPS = 20
DURATION = 24
TOTAL_FRAMES = DURATION * FPS

fa_reg_path = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"
fa_bold_path = "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf"
en_reg_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
en_bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

if not Path(fa_reg_path).exists():
    fa_reg_path = en_reg_path
if not Path(fa_bold_path).exists():
    fa_bold_path = en_bold_path

F_FA_TITLE = ImageFont.truetype(fa_bold_path, 46)
F_FA_SUB = ImageFont.truetype(fa_bold_path, 30)
F_FA_BODY = ImageFont.truetype(fa_reg_path, 24)
F_EN_HUD = ImageFont.truetype(en_bold_path, 16)
F_EN_BIG = ImageFont.truetype(en_bold_path, 26)
F_EN_SM = ImageFont.truetype(en_reg_path, 14)

random.seed(7)
STARS = [(random.randint(0, W), random.randint(0, H), random.uniform(0.4, 1.0), random.choice([1, 2, 3])) for _ in range(140)]
MOLECULES = [(random.uniform(0.18, 0.85), random.uniform(0.22, 0.72), random.uniform(0, 6.28)) for _ in range(26)]

SCENES = [
    {
        "id": "01 / ORBITAL HOOK",
        "tag": "ATMOSPHERIC OPTICS · 380–750 nm",
        "title": "چرا آسمان زمین آبی دیده می‌شود؟",
        "caption": "آسمان به خاطر اقیانوس‌ها آبی نیست؛ راز اصلی در برخورد نور خورشید با مولکول‌های هواست.",
    },
    {
        "id": "02 / SOLAR SPECTRUM",
        "tag": "WHITE LIGHT DISPERSION · PRISM MODEL",
        "title": "نور سفید خورشید، ترکیبی از تمام رنگ‌هاست",
        "caption": "نور آبی موج‌های کوتاه و پرانرژی (۴۰۰ نانومتر) دارد، اما نور قرمز موج‌های بلند (۷۰۰ نانومتر) دارد.",
    },
    {
        "id": "03 / RAYLEIGH SCATTERING",
        "tag": "N2 & O2 MOLECULAR SCATTERING",
        "title": "پراکندگی رایلی در برخورد با نیتروژن و اکسیژن",
        "caption": "مولکول‌های ریز هوا نور آبی را تا ۱۰ برابر بیشتر از نور قرمز به تمام جهت‌هاپخش می‌کنند.",
    },
    {
        "id": "04 / SUNSET GEOMETRY",
        "tag": "LOW-ANGLE SOLAR PATH · 10X AIR MASS",
        "title": "چرا هنگام غروب، آسمان سرخ و طلایی می‌شود؟",
        "caption": "در افق، نور خورشید مسیر بسیار طولانی‌تری در جو طی می‌کند؛ آبی حذف می‌شود و سرخ می‌ماند.",
    },
]


def draw_starfield(draw: ImageDraw.ImageDraw, t: float, alpha_scale: float = 1.0) -> None:
    for sx, sy, phase, r in STARS:
        twinkle = 0.55 + 0.45 * math.sin(t * 2.5 + phase * 6.28)
        v = int(210 * twinkle * alpha_scale)
        draw.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(v, min(255, int(v * 1.1)), min(255, int(v * 1.25))))


def scene_orbital_earth(img: Image.Image, draw: ImageDraw.ImageDraw, t: float, local_t: float) -> None:
    for y in range(H):
        k = y / H
        draw.line((0, y, W, y), fill=(int(4 + 10 * k), int(9 + 24 * k), int(24 + 54 * k)))
    draw_starfield(draw, t, 0.9)

    sun_x, sun_y = int(250 + 25 * math.sin(t * 0.6)), int(180 + 10 * math.cos(t * 0.5))
    for r in range(220, 10, -18):
        c = int(255 * (1 - r / 230) ** 1.6)
        draw.ellipse((sun_x - r, sun_y - r, sun_x + r, sun_y + r), fill=(min(255, c + 40), min(255, int(c * 0.85)), int(c * 0.45)))

    earth_cx, earth_cy, earth_r = W // 2 + 120, H + 420, 680
    for idx in range(7):
        ang = -0.35 + idx * 0.08 + 0.02 * math.sin(t + idx)
        x2 = sun_x + int(900 * math.cos(ang))
        y2 = sun_y + int(900 * math.sin(ang))
        draw.line((sun_x, sun_y, x2, y2), fill=(110, 200, 255), width=2)

    for glow in range(65, 0, -5):
        rr = earth_r + glow
        intensity = int(220 * (1 - glow / 70))
        draw.ellipse(
            (earth_cx - rr, earth_cy - rr, earth_cx + rr, earth_cy + rr),
            outline=(35, min(255, int(intensity * 0.78)), min(255, intensity + 30)),
            width=5,
        )
    draw.ellipse(
        (earth_cx - earth_r, earth_cy - earth_r, earth_cx + earth_r, earth_cy + earth_r),
        fill=(10, 32, 68),
        outline=(95, 210, 255),
        width=4,
    )
    draw.rounded_rectangle((780, 145, 1190, 255), radius=12, fill=(12, 26, 52), outline=(70, 185, 255), width=2)
    draw.text((800, 162), "EARTH ATMOSPHERE LIMB", font=F_EN_HUD, fill=(130, 225, 255))
    draw.text((800, 190), "78% N2  ·  21% O2  ·  1% Ar", font=F_EN_BIG, fill=(255, 255, 255))
    draw.text((800, 224), f"SCATTERING INDEX: {1.0 + 0.24 * math.sin(t*2):.2f}x", font=F_EN_SM, fill=(195, 240, 110))


def scene_prism_spectrum(img: Image.Image, draw: ImageDraw.ImageDraw, t: float, local_t: float) -> None:
    for y in range(H):
        k = y / H
        draw.line((0, y, W, y), fill=(int(8 + 12 * k), int(12 + 16 * k), int(28 + 30 * k)))
    draw_starfield(draw, t, 0.35)

    beam_end_x, beam_end_y = 520, 360
    draw.line((80, 390, beam_end_x, beam_end_y), fill=(255, 255, 255), width=12)
    draw.text((110, 345), "SUNLIGHT (WHITE LIGHT)", font=F_EN_HUD, fill=(235, 240, 255))

    spectrum = [
        ("700 nm  RED (Long Wave)", (255, 68, 68), -65, 0.035),
        ("620 nm  ORANGE", (255, 145, 50), -40, 0.045),
        ("580 nm  YELLOW", (255, 225, 70), -15, 0.055),
        ("530 nm  GREEN", (75, 230, 125), 12, 0.070),
        ("470 nm  BLUE (Short Wave)", (55, 175, 255), 42, 0.115),
        ("400 nm  VIOLET", (165, 95, 255), 72, 0.145),
    ]
    for label, color, y_offset, freq in spectrum:
        pts = []
        for step in range(0, 560, 8):
            x = 610 + step
            y_base = 355 + (y_offset * step / 520)
            amp = 8 + (12 if "BLUE" in label or "VIOLET" in label else 5)
            y = y_base + amp * math.sin(step * freq - t * 9.0)
            pts.append((x, y))
        draw.line(pts, fill=color, width=6)
        lx, ly = pts[-1]
        draw.text((int(lx) - 210, int(ly) - 10), label, font=F_EN_SM, fill=color)

    prism = [(470, 445), (565, 235), (660, 445)]
    draw.polygon(prism, fill=(28, 52, 88), outline=(160, 230, 255))
    draw.line([prism[0], prism[1], prism[2], prism[0]], fill=(180, 240, 255), width=4)


def scene_rayleigh_molecules(img: Image.Image, draw: ImageDraw.ImageDraw, t: float, local_t: float) -> None:
    for y in range(H):
        k = y / H
        draw.line((0, y, W, y), fill=(int(10 + 25 * (1 - k)), int(38 + 65 * (1 - k)), int(92 + 115 * (1 - k))))

    for r_idx in range(4):
        ry = 210 + r_idx * 95
        draw.line((60, ry, W - 60, ry), fill=(255, 110, 90), width=3)
    draw.text((85, 172), "700nm RED PASSES STRAIGHT THROUGH", font=F_EN_HUD, fill=(255, 155, 135))

    for m_idx, (mx, my, ph) in enumerate(MOLECULES):
        cx = int(mx * W + 14 * math.sin(t * 1.8 + ph))
        cy = int(my * (H - 180) + 12 * math.cos(t * 1.5 + ph))
        pulse = int(16 + 26 * ((t * 2.2 + ph) % 1.0))
        draw.ellipse((cx - pulse, cy - pulse, cx + pulse, cy + pulse), outline=(120, 225, 255), width=2)
        if m_idx % 2 == 0:
            for a in range(6):
                ang = a * math.pi / 3 + t * 1.6
                px = cx + int(pulse * 1.35 * math.cos(ang))
                py = cy + int(pulse * 1.35 * math.sin(ang))
                draw.line((cx, cy, px, py), fill=(95, 215, 255), width=2)
        draw.ellipse((cx - 9, cy - 9, cx + 9, cy + 9), fill=(235, 250, 255), outline=(35, 120, 215), width=2)

    draw.rounded_rectangle((820, 140, 1200, 230), radius=12, fill=(9, 25, 54), outline=(120, 225, 255), width=2)
    draw.text((840, 158), "RAYLEIGH LAW: I ∝ 1 / λ⁴", font=F_EN_BIG, fill=(195, 255, 110))
    draw.text((840, 194), "Blue scatters ~10x stronger than Red", font=F_EN_SM, fill=(225, 240, 255))


def scene_sunset_geometry(img: Image.Image, draw: ImageDraw.ImageDraw, t: float, local_t: float) -> None:
    for y in range(H):
        k = y / H
        r = int(28 + 215 * (k ** 1.15))
        g = int(18 + 115 * (k ** 1.5))
        b = int(68 * (1 - k) + 32)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b)))

    sun_x = int(290 + 35 * math.sin(t * 0.4))
    sun_y = int(430 + 25 * local_t)
    for rr in range(160, 10, -16):
        draw.ellipse(
            (sun_x - rr, sun_y - rr, sun_x + rr, sun_y + rr),
            fill=(255, min(255, 130 + (160 - rr) // 2), max(40, 110 - rr // 2)),
        )

    draw.line((sun_x, sun_y, 980, 445), fill=(255, 220, 120), width=5)
    draw.text((480, 395), "10x LONGER ATMOSPHERIC PATH AT HORIZON", font=F_EN_HUD, fill=(255, 245, 190))

    horizon = [(0, 520), (240, 485), (520, 505), (840, 470), (1120, 495), (W, 480), (W, H), (0, H)]
    draw.polygon(horizon, fill=(16, 12, 24))


def draw_hud_and_captions(img: Image.Image, draw: ImageDraw.ImageDraw, t: float) -> None:
    scene_len = DURATION / len(SCENES)
    idx = min(len(SCENES) - 1, int(t / scene_len))
    sc = SCENES[idx]

    draw.rounded_rectangle((48, 32, W - 48, 92), radius=14, fill=(8, 14, 28), outline=(55, 95, 155), width=2)
    draw.text((74, 46), "DEEP COSMOS  //  SCIENCE DOCUMENTARY", font=F_EN_HUD, fill=(195, 255, 100))
    draw.text((74, 68), f"{sc['id']}   ·   {sc['tag']}", font=F_EN_SM, fill=(175, 205, 235))

    title_s = fa(sc["title"])
    tb = draw.textbbox((0, 0), title_s, font=F_FA_SUB)
    draw.text((W - 76 - (tb[2] - tb[0]), 44), title_s, font=F_FA_SUB, fill=(255, 255, 255))

    draw.rounded_rectangle((68, H - 138, W - 68, H - 36), radius=16, fill=(7, 12, 24), outline=(95, 195, 255), width=2)
    cap_s = fa(sc["caption"])
    cb = draw.textbbox((0, 0), cap_s, font=F_FA_BODY)
    draw.text(((W - (cb[2] - cb[0])) // 2, H - 108), cap_s, font=F_FA_BODY, fill=(242, 247, 255))

    prog_w = int((W - 160) * (t / DURATION))
    draw.rounded_rectangle((80, H - 52, W - 80, H - 44), radius=4, fill=(32, 46, 72))
    draw.rounded_rectangle((80, H - 52, 80 + max(8, prog_w), H - 44), radius=4, fill=(195, 255, 100))


for frame_idx in range(TOTAL_FRAMES):
    t = frame_idx / FPS
    scene_len = DURATION / len(SCENES)
    s_idx = min(len(SCENES) - 1, int(t / scene_len))
    local_t = (t % scene_len) / scene_len

    img = Image.new("RGB", (W, H), (8, 14, 28))
    draw = ImageDraw.Draw(img)

    if s_idx == 0:
        scene_orbital_earth(img, draw, t, local_t)
    elif s_idx == 1:
        scene_prism_spectrum(img, draw, t, local_t)
    elif s_idx == 2:
        scene_rayleigh_molecules(img, draw, t, local_t)
    else:
        scene_sunset_geometry(img, draw, t, local_t)

    draw_hud_and_captions(img, draw, t)
    img.save(frames_dir / f"frame-{frame_idx:04d}.jpg", quality=90)

script_lines = [sc["caption"] for sc in SCENES]
script_text = "\n".join(script_lines)
(work / "script-fa.txt").write_text(script_text + "\n", encoding="utf-8")

voice_raw = work / "voice_raw.wav"
espeak = shutil.which("espeak-ng") or shutil.which("espeak")
if espeak:
    subprocess.run(
        [espeak, "-v", "fa", "-s", "138", "-w", str(voice_raw), " ... ".join(script_lines)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

sr = 22050
t_arr = np.linspace(0, DURATION, int(sr * DURATION), endpoint=False)
pad = (
    0.12 * np.sin(2 * np.pi * 110.0 * t_arr)
    + 0.09 * np.sin(2 * np.pi * 164.81 * t_arr)
    + 0.07 * np.sin(2 * np.pi * 220.0 * t_arr)
    + 0.04 * np.sin(2 * np.pi * 277.18 * t_arr) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t_arr))
)
pulse = 0.06 * np.sin(2 * np.pi * 55.0 * t_arr) * (np.sin(np.pi * t_arr / 2.0) ** 4)
bed = np.clip(pad + pulse, -0.8, 0.8)
bed_pcm = (bed * 32767).astype(np.int16)

bed_wav = work / "ambient_bed.wav"
with wave.open(str(bed_wav), "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(sr)
    wf.writeframes(bed_pcm.tobytes())

mixed_audio = work / "narration.wav"
if voice_raw.exists() and voice_raw.stat().st_size > 100:
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(voice_raw),
            "-i", str(bed_wav),
            "-filter_complex", "[0:a]volume=1.35,apad=whole_dur=24[v];[1:a]volume=0.38[b];[v][b]amix=inputs=2:duration=shortest",
            "-t", str(DURATION),
            str(mixed_audio),
        ],
        check=True,
    )
else:
    shutil.copy2(bed_wav, mixed_audio)

video_mp4 = work / "deep-cosmos-documentary.mp4"
subprocess.run(
    [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame-%04d.jpg"),
        "-i", str(mixed_audio),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "160k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        str(video_mp4),
    ],
    check=True,
)

shutil.copy2(frames_dir / "frame-0015.jpg", work / "thumbnail.jpg")

srt_blocks = []
seg = DURATION / len(SCENES)
for idx, sc in enumerate(SCENES, 1):
    s0 = int((idx - 1) * seg)
    s1 = int(idx * seg)
    srt_blocks.append(f"{idx}\n00:00:{s0:02d},000 --> 00:00:{s1:02d},000\n{sc['caption']}\n")
(work / "captions-fa.srt").write_text("\n".join(srt_blocks), encoding="utf-8")

manifest = {
    "title": "چرا آسمان زمین آبی دیده می‌شود؟ (مستند علمی کوتاه)",
    "channel": "Deep Cosmos",
    "duration_seconds": DURATION,
    "resolution": f"{W}x{H}",
    "fps": FPS,
    "scenes": len(SCENES),
    "audio": "Persian narration + ambient documentary synth bed",
}
(work / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

zip_out = work / "deep-cosmos-youtube-package.zip"
with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for fname in ["deep-cosmos-documentary.mp4", "thumbnail.jpg", "narration.wav", "script-fa.txt", "captions-fa.srt", "manifest.json"]:
        zf.write(work / fname, arcname=fname)

print("MP4 size:", video_mp4.stat().st_size, "ZIP size:", zip_out.stat().st_size)
