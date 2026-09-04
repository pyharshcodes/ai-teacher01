"""
video_generator.py
--------------------
Turns (narration audio + caption text + a visual hint) into an actual .mp4
teaching video with an animated AI-avatar, synced captions, and a visual
panel - fully local, fully free (PIL + moviepy), no GPU or paid API needed.

Want a photorealistic avatar instead? Set HEYGEN_API_KEY or DID_API_KEY in
.env and replace the body of `render_lesson_video()` with a call to
`_render_with_heygen()` / `_render_with_did()` (stubs included below) -
the rest of the app (routes, frontend) does not need to change.
"""

import os
import math
import uuid
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# moviepy 2.x dropped the `moviepy.editor` submodule (import directly from
# `moviepy` instead); moviepy 1.x still needs the `.editor` import. This
# supports whichever version pip installed on your machine.
try:
    from moviepy import VideoClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoClip, AudioFileClip

W, H = 960, 540

# Theme colours - matches the app's UI (see static/css/style.css)
BG_TOP = (18, 23, 43)      # deep navy
BG_BOTTOM = (27, 33, 64)   # lighter navy
ACCENT = (242, 169, 59)    # marigold
TEXT_MAIN = (245, 243, 237)
TEXT_MUTED = (169, 175, 200)
AVATAR_SKIN = (235, 194, 150)
AVATAR_HAIR = (40, 32, 28)
AVATAR_SHIRT = (79, 209, 174)  # teal


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT_HEADING = _font(28, bold=True)
FONT_CAPTION = _font(22)
FONT_BADGE = _font(16, bold=True)


def _gradient_bg():
    img = Image.new("RGB", (W, H), BG_TOP)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    return img


_BG = _gradient_bg()


def _draw_avatar(draw, cx, cy, talk_phase, blink_phase):
    """Draws a simple, friendly programmatic avatar with a lip-sync-style
    mouth animation driven by talk_phase (0..1) and an eye blink."""
    # soft presenter ring behind the avatar (gives a "live video call" feel)
    draw.ellipse([cx - 150, cy - 150, cx + 150, cy + 230], outline=(50, 58, 92), width=2)
    draw.ellipse([cx - 150, cy - 150, cx + 150, cy + 230], outline=ACCENT, width=1)

    # soft shadow under the avatar
    draw.ellipse([cx - 90, cy + 205, cx + 90, cy + 225], fill=(8, 10, 20))

    # shoulders / shirt (with a small collar)
    draw.ellipse([cx - 100, cy + 70, cx + 100, cy + 230], fill=AVATAR_SHIRT)
    draw.polygon(
        [(cx - 16, cy + 78), (cx, cy + 100), (cx + 16, cy + 78)],
        fill=(60, 170, 145),
    )

    # neck
    draw.rectangle([cx - 16, cy + 50, cx + 16, cy + 85], fill=AVATAR_SKIN)

    # head (slightly taller oval reads more natural than a perfect circle)
    draw.ellipse([cx - 68, cy - 95, cx + 68, cy + 65], fill=AVATAR_SKIN)
    # ear hints
    draw.ellipse([cx - 74, cy - 15, cx - 60, cy + 15], fill=AVATAR_SKIN)
    draw.ellipse([cx + 60, cy - 15, cx + 74, cy + 15], fill=AVATAR_SKIN)

    # hair - rounded cap sitting on top of the head, not overlapping the face
    draw.pieslice([cx - 72, cy - 110, cx + 72, cy + 10], 180, 360, fill=AVATAR_HAIR)
    draw.rectangle([cx - 72, cy - 60, cx + 72, cy - 30], fill=AVATAR_HAIR)
    # soft hair highlight for a little dimensionality
    draw.arc([cx - 55, cy - 100, cx + 10, cy - 40], 200, 300, fill=(70, 58, 50), width=4)

    # eyes (blink = thin line, open = ellipse with a tiny highlight)
    eye_y = cy - 12
    if blink_phase:
        draw.line([(cx - 34, eye_y), (cx - 12, eye_y)], fill=(40, 30, 30), width=3)
        draw.line([(cx + 12, eye_y), (cx + 34, eye_y)], fill=(40, 30, 30), width=3)
    else:
        draw.ellipse([cx - 34, eye_y - 7, cx - 12, eye_y + 7], fill=(255, 255, 255))
        draw.ellipse([cx + 12, eye_y - 7, cx + 34, eye_y + 7], fill=(255, 255, 255))
        draw.ellipse([cx - 27, eye_y - 5, cx - 17, eye_y + 5], fill=(45, 32, 28))
        draw.ellipse([cx + 17, eye_y - 5, cx + 27, eye_y + 5], fill=(45, 32, 28))

    # eyebrows - positioned clear of the hairline
    draw.line([(cx - 36, eye_y - 16), (cx - 10, eye_y - 19)], fill=AVATAR_HAIR, width=3)
    draw.line([(cx + 10, eye_y - 19), (cx + 36, eye_y - 16)], fill=AVATAR_HAIR, width=3)

    # nose
    draw.line([(cx, eye_y + 6), (cx - 5, eye_y + 26)], fill=(205, 165, 125), width=2)

    # mouth - open amount oscillates with talk_phase to simulate speech
    mouth_open = 4 + int(11 * abs(math.sin(talk_phase * math.pi)))
    draw.ellipse(
        [cx - 20, cy + 40 - mouth_open // 2, cx + 20, cy + 40 + mouth_open // 2],
        fill=(130, 55, 55),
    )
    if mouth_open > 8:
        draw.ellipse(
            [cx - 14, cy + 40 - mouth_open // 3, cx + 14, cy + 40 + mouth_open // 3],
            fill=(200, 90, 85),
        )

    # small "speaking" indicator dot pulsing with talk_phase, top-right of the ring
    pulse = 5 + int(3 * abs(math.sin(talk_phase * math.pi)))
    draw.ellipse([cx + 110, cy - 130, cx + 110 + pulse * 2, cy - 130 + pulse * 2], fill=ACCENT)


def _wrap(text, width=42):
    return "\n".join(textwrap.wrap(text, width=width)) if text else ""


def render_lesson_video(audio_path, caption_segments, heading, visual_hint, out_dir):
    """
    audio_path: path to narration mp3/wav for this segment
    caption_segments: list of {"text": str, "start": float, "end": float}
    heading: segment heading shown as a title bar
    visual_hint: short text describing the on-screen visual concept
    Returns path to rendered .mp4
    """
    os.makedirs(out_dir, exist_ok=True)
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration

    def caption_at(t):
        for seg in caption_segments:
            if seg["start"] <= t <= seg["end"]:
                return seg["text"]
        return caption_segments[-1]["text"] if caption_segments else ""

    def make_frame(t):
        frame = _BG.copy()
        draw = ImageDraw.Draw(frame)

        # top badge + heading bar
        draw.rectangle([0, 0, W, 64], fill=(15, 19, 36))
        draw.rectangle([24, 20, 24 + 10, 30], fill=ACCENT)
        draw.text((44, 16), "AI TEACHER", font=FONT_BADGE, fill=ACCENT)
        draw.text((44, 34), _wrap(heading, 60).split("\n")[0], font=FONT_HEADING, fill=TEXT_MAIN)

        # right visual panel
        panel_x = 560
        draw.rounded_rectangle([panel_x, 84, W - 24, H - 130], radius=14, fill=(15, 19, 36), outline=(50, 58, 92))
        draw.text((panel_x + 18, 100), "ON-SCREEN VISUAL", font=FONT_BADGE, fill=TEXT_MUTED)
        hint = _wrap(visual_hint or "Concept illustration", 26)
        draw.multiline_text((panel_x + 18, 140), hint, font=FONT_CAPTION, fill=TEXT_MAIN, spacing=8)

        # avatar (talking + blinking animation)
        talk_phase = (t * 6) % 2  # mouth cycles ~3x/sec
        blink_phase = int(t * 1.2) % 6 == 0  # brief periodic blink
        _draw_avatar(draw, cx=230, cy=270, talk_phase=talk_phase, blink_phase=blink_phase)

        # caption bar
        draw.rectangle([0, H - 110, W, H], fill=(12, 15, 30))
        cap = _wrap(caption_at(t), 70)
        draw.multiline_text((24, H - 96), cap, font=FONT_CAPTION, fill=TEXT_MAIN, spacing=6)

        return np.array(frame)

    video = VideoClip(make_frame, duration=max(duration, 0.5))
    # moviepy 2.x renamed set_audio() -> with_audio(); support both.
    video = video.with_audio(audio_clip) if hasattr(video, "with_audio") else video.set_audio(audio_clip)

    out_path = os.path.join(out_dir, f"{uuid.uuid4().hex}.mp4")
    video.write_videofile(
        out_path, fps=12, codec="libx264", audio_codec="aac", logger=None,
    )
    return out_path


def get_audio_duration(audio_path: str) -> float:
    """Returns the duration (seconds) of an audio file. Centralized here so
    app.py doesn't need its own moviepy import / version-compat handling."""
    clip = AudioFileClip(audio_path)
    try:
        return clip.duration
    finally:
        clip.close()


def build_caption_segments(text, total_duration):
    """Splits text into sentence-level captions timed proportionally across
    the audio duration (rough but effective lip-sync-free captioning)."""
    import re
    sentences = [s.strip() for s in re.split(r"(?<=[.!?।])\s+", text) if s.strip()]
    if not sentences:
        return [{"text": text, "start": 0, "end": total_duration}]

    total_chars = sum(len(s) for s in sentences) or 1
    segments = []
    cursor = 0.0
    for s in sentences:
        share = len(s) / total_chars
        dur = max(total_duration * share, 0.8)
        segments.append({"text": s, "start": cursor, "end": cursor + dur})
        cursor += dur
    segments[-1]["end"] = max(segments[-1]["end"], total_duration)
    return segments


# ---------------------------------------------------------------------------
# OPTIONAL: premium avatar hooks (disabled unless you add a key + wire it in)
# ---------------------------------------------------------------------------
def _render_with_heygen(text, language, api_key):
    """Stub - see https://docs.heygen.com for the video-generation endpoint.
    Call it, poll for completion, download the resulting mp4, and return its
    local path so it can replace render_lesson_video()'s output."""
    raise NotImplementedError("Plug in your HeyGen API call here once you have a key.")


def _render_with_did(text, language, api_key):
    """Stub - see https://docs.d-id.com for the talks endpoint."""
    raise NotImplementedError("Plug in your D-ID API call here once you have a key.")
