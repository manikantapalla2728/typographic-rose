"""
1 ROSE, EVERY LANGUAGE - Typographic Rose Animation
===================================================
A visually satisfying typographic animation that forms a complete,
organic rose flower, stem, and leaves using multilingual words meaning
"I LOVE YOU" across global languages, matching the exact artistic
typographic silhouette poster aesthetic.

Resolution: 1080 x 1920 (Vertical 9:16)
Framerate : 30 FPS
Duration  : 14.0 seconds (420 frames)
Background: Pure Black (#000000)
"""

import sys, os, math, time, subprocess, random
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import cv2
from PIL import Image, ImageFont, ImageDraw

# ----------------- Configuration & Canvas Constants -----------------
WIDTH, HEIGHT = 1080, 1920
FPS = 30
DURATION = 14.0  # seconds
TOTAL_FRAMES = int(DURATION * FPS)  # 420 frames
CX = WIDTH // 2  # 540

FONT_UNI = r'C:\Windows\Fonts\ARIALUNI.TTF'
FONT_TITLE = r'C:\Windows\Fonts\arialbd.ttf'

OUTPUT_FILE = 'typographic_rose.mp4'

# ----------------- Color Palettes -----------------
RED_BRIGHT = (235, 20, 50)    # Bright vibrant crimson
RED_MID    = (195, 15, 40)    # Medium ruby
RED_DARK   = (150, 10, 30)    # Deep velvet crimson

GREEN_BRIGHT = (52, 205, 88)   # Bright vibrant emerald
GREEN_MID    = (34, 155, 66)   # Medium leaf green
GREEN_DARK   = (18, 105, 42)   # Deep forest green

SIZE_MAP = {'L': 23, 'M': 18, 'S': 14}

RED_PALETTE = {1: RED_BRIGHT, 2: RED_MID, 3: RED_DARK}
GREEN_PALETTE = {1: GREEN_BRIGHT, 2: GREEN_MID, 3: GREEN_DARK}

# ----------------- Target Width Profiles -----------------
# Exact silhouette width profile from the rose blossom
HEAD_TARGET_WIDTHS = [
    325, 425, 485, 525, 550, 565, 580, 605, 635, 645,
    660, 670, 675, 675, 665, 650, 640, 620, 590, 555,
    515, 485, 470, 435, 395, 370, 345, 305, 250, 170, 70
]

STEM_TOP_WIDTHS = [60, 45, 65, 45, 65]
LEFT_LEAF_WIDTHS = [160, 220, 260, 250, 210, 150]
RIGHT_LEAF_WIDTHS = [150, 210, 250, 260, 230, 190, 140, 80]
STEM_BOT_WIDTHS = [45, 50, 40, 55, 40, 45, 50, 40, 45, 40, 45, 40, 40, 40, 40, 40]

# Multilingual romantic phrases bank
ALL_PHRASES = [
    ("I LOVE YOU", 'L', 1),
    ("TE AMO", 'L', 1),
    ("AMOUR", 'L', 1),
    ("사랑해", 'M', 2),
    ("愛してる", 'M', 2),
    ("我爱你", 'L', 1),
    ("أحبك", 'S', 3),
    ("TI AMO", 'L', 1),
    ("Nakupenda", 'M', 2),
    ("LIEBE", 'L', 1),
    ("JE T'AIME", 'L', 1),
    ("ICH LIEBE DICH", 'M', 2),
    ("Eu te amo", 'M', 2),
    ("నేను నిన్ను ప్రేమిస్తున్నాను", 'M', 2),
    ("Я ТЕБЯ ЛЮБЛЮ", 'M', 2),
    ("LOVE", 'L', 1),
    ("사랑", 'M', 2),
    ("愛", 'S', 2),
    ("Szeretlek", 'M', 2),
    ("Mahal kita", 'M', 2),
    ("ANH YÊU EM", 'M', 2),
    ("Anh yêu em", 'S', 3),
    ("TE QUIERO", 'L', 1),
    ("LOVE YOU", 'L', 1),
    ("AMORE", 'L', 1),
    ("Ti amo", 'M', 2),
    ("Te amo", 'S', 3),
    ("Kocham cię", 'S', 3),
    ("Jag älskar dig", 'S', 3),
    ("Jeg elsker dig", 'S', 3),
    ("Seni seviyorum", 'S', 3),
    ("Rakastan sinua", 'S', 3),
    ("Aku cinta kamu", 'S', 3),
    ("Ljubim te", 'S', 3),
    ("Te iubesc", 'S', 3),
    ("Miluji tě", 'S', 3),
    ("אני אוהבת אותך", 'S', 3),
    ("รักคุณ", 'S', 3),
    ("Σ' αγαπώ", 'M', 2),
    ("Ik hou van jou", 'S', 3)
]

rng = random.Random(1337)

# Font cache
_font_cache = {}
def get_font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]

# Pre-render stamp cache for fast rendering
_stamp_cache = {}
def get_stamp(text, size, color_rgb):
    key = (text, size, color_rgb)
    if key not in _stamp_cache:
        f = get_font(FONT_UNI, size)
        bbox = f.getbbox(text)
        w = max(1, bbox[2] - bbox[0] + 6)
        h = max(1, bbox[3] - bbox[1] + 6)
        im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.text((3 - bbox[0], 3 - bbox[1]), text, font=f, fill=(*color_rgb, 255))
        _stamp_cache[key] = (im, bbox)
    return _stamp_cache[key]

def fit_words_to_width(target_w, palette):
    pool = list(ALL_PHRASES)
    best_combo = []
    best_diff = 999999
    
    for attempt in range(8):
        rng.shuffle(pool)
        combo = []
        w_sum = 0
        for text, sz_tier, col_tier in pool:
            sz = SIZE_MAP[sz_tier]
            f = get_font(FONT_UNI, sz)
            bbox = f.getbbox(text)
            w = bbox[2] - bbox[0]
            if w_sum + w + (10 if len(combo) > 0 else 0) <= target_w + 14:
                combo.append((text, sz, palette[col_tier], w, bbox))
                w_sum += w + 10
            if abs(w_sum - target_w) < 18:
                break
        diff = abs(w_sum - target_w)
        if diff < best_diff and len(combo) > 0:
            best_diff = diff
            best_combo = combo
            
    return best_combo

# ----------------- Build Rose & Animation Setup -----------------
def build_animation_elements():
    """
    Constructs all word elements and the arched heading, assigning each
    exact target positions, flight paths, and progressive animation timing.
    """
    elements = []
    
    # --- 1. Top Arched Title ("1 Rose, Every Language") ---
    text_heading = "1 Rose, Every Language"
    h_font = get_font(FONT_TITLE, 56)
    R_ARCH = 680
    CY_ARCH = 1040

    char_widths = []
    for ch in text_heading:
        bbox = h_font.getbbox(ch)
        char_widths.append(max(10, bbox[2] - bbox[0] + 5))

    total_w = sum(char_widths)
    total_ang = total_w / R_ARCH
    curr_ang = -total_ang / 2.0

    heading_chars = []
    for idx, ch in enumerate(text_heading):
        w_ch = char_widths[idx]
        mid_ang = curr_ang + (w_ch / 2.0) / R_ARCH
        x = CX + R_ARCH * math.sin(mid_ang)
        y = CY_ARCH - R_ARCH * math.cos(mid_ang)
        rot = math.degrees(mid_ang)
        
        # Pre-render stamp for heading letter
        bbox = h_font.getbbox(ch)
        cw = bbox[2] - bbox[0] + 10
        ch_h = bbox[3] - bbox[1] + 10
        stamp = Image.new('RGBA', (cw, ch_h), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(stamp)
        sdraw.text((5 - bbox[0], 5 - bbox[1]), ch, font=h_font, fill=(235, 20, 50, 255))
        rot_stamp = stamp.rotate(-rot, resample=Image.Resampling.BILINEAR, expand=True)
        
        heading_chars.append({
            'char': ch, 'x': x, 'y': y, 'rot': rot, 'stamp': rot_stamp
        })
        curr_ang += w_ch / R_ARCH

    # --- 2. Flower Head (Red Silhouette) ---
    Y_START_HEAD = 530
    LINE_H_HEAD = 22

    for row_idx, target_w in enumerate(HEAD_TARGET_WIDTHS):
        y = Y_START_HEAD + row_idx * LINE_H_HEAD
        words = fit_words_to_width(target_w, RED_PALETTE)
        total_words_w = sum(w[3] for w in words)
        space_w = max(6, (target_w - total_words_w) / max(1, len(words) - 1)) if len(words) > 1 else 0
        actual_line_w = total_words_w + space_w * (len(words) - 1)
        
        start_x = CX - actual_line_w / 2.0
        cur_x = start_x
        
        # Timing: Center rows (10 to 20) spawn first (1.8s - 5.0s),
        # then outer/top/bottom rows (5.0s - 8.5s)
        dist_from_center_row = abs(row_idx - 15)
        t_spawn = 1.8 + 2.8 * (dist_from_center_row / 15.0) ** 0.85 + rng.uniform(-0.15, 0.15)
        dur = 2.0 + rng.uniform(0.1, 0.4)
        
        for text, sz, col, w, bbox in words:
            tx = cur_x + w / 2.0
            ty = y
            stamp, _ = get_stamp(text, sz, col)
            
            # Spawn trajectory from outside
            ang = rng.uniform(0, 2 * math.pi)
            dist = rng.uniform(480, 780)
            sx = tx + dist * math.cos(ang)
            sy = ty + dist * math.sin(ang)
            
            elements.append({
                'text': text, 'size': sz, 'color': col,
                'tx': tx, 'ty': ty, 'w': w, 'h': bbox[3] - bbox[1],
                'stamp': stamp, 'group': 'head', 'row': row_idx,
                'sx': sx, 'sy': sy, 't_spawn': t_spawn, 'dur': dur
            })
            cur_x += w + space_w

    # --- 3. Stem Top (Green) ---
    Y_START_STEM_TOP = Y_START_HEAD + len(HEAD_TARGET_WIDTHS) * LINE_H_HEAD + 14
    LINE_H_STEM = 20

    for row_idx, target_w in enumerate(STEM_TOP_WIDTHS):
        y = Y_START_STEM_TOP + row_idx * LINE_H_STEM
        words = fit_words_to_width(target_w, GREEN_PALETTE)
        total_words_w = sum(w[3] for w in words)
        space_w = 8
        actual_line_w = total_words_w + space_w * max(0, len(words) - 1)
        start_x = CX - actual_line_w / 2.0
        cur_x = start_x
        
        t_spawn = 8.6 + 0.4 * row_idx + rng.uniform(-0.1, 0.1)
        dur = 1.8
        
        for text, sz, col, w, bbox in words:
            tx = cur_x + w / 2.0
            ty = y
            stamp, _ = get_stamp(text, sz, col)
            sx = CX + rng.uniform(-80, 80)
            sy = y - 180
            elements.append({
                'text': text, 'size': sz, 'color': col,
                'tx': tx, 'ty': ty, 'w': w, 'h': bbox[3] - bbox[1],
                'stamp': stamp, 'group': 'stem_top', 'row': row_idx,
                'sx': sx, 'sy': sy, 't_spawn': t_spawn, 'dur': dur
            })
            cur_x += w + space_w

    # --- 4. Left Leaf (Green, unfolds outward to left) ---
    Y_START_LEAF = Y_START_STEM_TOP + len(STEM_TOP_WIDTHS) * LINE_H_STEM + 8
    for row_idx, target_w in enumerate(LEFT_LEAF_WIDTHS):
        y = Y_START_LEAF + row_idx * LINE_H_STEM
        words = fit_words_to_width(target_w, GREEN_PALETTE)
        total_words_w = sum(w[3] for w in words)
        space_w = 8
        actual_line_w = total_words_w + space_w * max(0, len(words) - 1)
        start_x = CX - 18 - actual_line_w
        cur_x = start_x
        
        t_spawn = 9.2 + 0.35 * row_idx + rng.uniform(-0.1, 0.1)
        dur = 1.9
        
        for text, sz, col, w, bbox in words:
            tx = cur_x + w / 2.0
            ty = y
            stamp, _ = get_stamp(text, sz, col)
            sx = CX - 10
            sy = y + rng.uniform(-20, 20)
            elements.append({
                'text': text, 'size': sz, 'color': col,
                'tx': tx, 'ty': ty, 'w': w, 'h': bbox[3] - bbox[1],
                'stamp': stamp, 'group': 'left_leaf', 'row': row_idx,
                'sx': sx, 'sy': sy, 't_spawn': t_spawn, 'dur': dur
            })
            cur_x += w + space_w

    # --- 5. Right Leaf (Green, unfolds outward to right) ---
    Y_START_R_LEAF = Y_START_LEAF + 35
    for row_idx, target_w in enumerate(RIGHT_LEAF_WIDTHS):
        y = Y_START_R_LEAF + row_idx * LINE_H_STEM
        words = fit_words_to_width(target_w, GREEN_PALETTE)
        total_words_w = sum(w[3] for w in words)
        space_w = 8
        actual_line_w = total_words_w + space_w * max(0, len(words) - 1)
        start_x = CX + 18
        cur_x = start_x
        
        t_spawn = 9.5 + 0.30 * row_idx + rng.uniform(-0.1, 0.1)
        dur = 1.9
        
        for text, sz, col, w, bbox in words:
            tx = cur_x + w / 2.0
            ty = y
            stamp, _ = get_stamp(text, sz, col)
            sx = CX + 10
            sy = y + rng.uniform(-20, 20)
            elements.append({
                'text': text, 'size': sz, 'color': col,
                'tx': tx, 'ty': ty, 'w': w, 'h': bbox[3] - bbox[1],
                'stamp': stamp, 'group': 'right_leaf', 'row': row_idx,
                'sx': sx, 'sy': sy, 't_spawn': t_spawn, 'dur': dur
            })
            cur_x += w + space_w

    # --- 6. Stem Bottom (Green, descends to base) ---
    Y_START_STEM_BOT = Y_START_LEAF + len(LEFT_LEAF_WIDTHS) * LINE_H_STEM + 6
    for row_idx, target_w in enumerate(STEM_BOT_WIDTHS):
        y = Y_START_STEM_BOT + row_idx * LINE_H_STEM
        words = fit_words_to_width(target_w, GREEN_PALETTE)
        total_words_w = sum(w[3] for w in words)
        space_w = 8
        actual_line_w = total_words_w + space_w * max(0, len(words) - 1)
        start_x = CX - actual_line_w / 2.0
        cur_x = start_x
        
        t_spawn = 9.8 + 0.15 * row_idx + rng.uniform(-0.08, 0.08)
        dur = 1.7
        
        for text, sz, col, w, bbox in words:
            tx = cur_x + w / 2.0
            ty = y
            stamp, _ = get_stamp(text, sz, col)
            sx = CX + rng.uniform(-20, 20)
            sy = Y_START_STEM_BOT - 40
            elements.append({
                'text': text, 'size': sz, 'color': col,
                'tx': tx, 'ty': ty, 'w': w, 'h': bbox[3] - bbox[1],
                'stamp': stamp, 'group': 'stem_bot', 'row': row_idx,
                'sx': sx, 'sy': sy, 't_spawn': t_spawn, 'dur': dur
            })
            cur_x += w + space_w

    return heading_chars, elements

# ----------------- Render Single Frame -----------------
def render_frame(t, heading_chars, elements):
    """
    Renders one full frame at timestamp t:
      - Arched heading with glowing fade-in
      - In-flight and settled words
      - Post-assembly breathing shimmer
      - Gaussian bloom glow pass
    """
    im = Image.new('RGB', (WIDTH, HEIGHT), (0, 0, 0))

    # 1. Heading ("1 Rose, Every Language")
    # Fades in between t=0.2s and t=1.6s
    head_alpha = np.clip((t - 0.2) / 1.4, 0.0, 1.0)
    if head_alpha > 0.01:
        for hc in heading_chars:
            stamp = hc['stamp']
            rx = int(hc['x'] - stamp.width / 2)
            ry = int(hc['y'] - stamp.height / 2)
            if head_alpha >= 0.99:
                im.paste(stamp, (rx, ry), stamp)
            else:
                # Fading stamp
                alpha_stamp = stamp.copy()
                arr_s = np.array(alpha_stamp)
                arr_s[:, :, 3] = (arr_s[:, :, 3] * head_alpha).astype(np.uint8)
                fading = Image.fromarray(arr_s)
                im.paste(fading, (rx, ry), fading)

    # 2. Draw Word Elements
    for elem in elements:
        if t < elem['t_spawn']:
            continue
        
        p = np.clip((t - elem['t_spawn']) / elem['dur'], 0.0, 1.0)
        # Quintic smooth easing
        e = p * p * p * (p * (6.0 * p - 15.0) + 10.0)
        
        stamp = elem['stamp']
        if p >= 0.999:
            # Settled in place
            cur_x = elem['tx']
            cur_y = elem['ty']
            rx = int(cur_x - stamp.width / 2)
            ry = int(cur_y - stamp.height / 2)
            im.paste(stamp, (rx, ry), stamp)
        else:
            # Traveling along trajectory
            # Add subtle arc curl during motion
            curl = 40.0 * math.sin(math.pi * p)
            cur_x = elem['sx'] * (1.0 - e) + elem['tx'] * e + curl
            cur_y = elem['sy'] * (1.0 - e) + elem['ty'] * e
            
            rx = int(cur_x - stamp.width / 2)
            ry = int(cur_y - stamp.height / 2)
            
            # Fading opacity during flight
            alpha = min(1.0, p * 2.5)
            if alpha >= 0.98:
                im.paste(stamp, (rx, ry), stamp)
            else:
                alpha_stamp = stamp.copy()
                arr_s = np.array(alpha_stamp)
                arr_s[:, :, 3] = (arr_s[:, :, 3] * alpha).astype(np.uint8)
                fading = Image.fromarray(arr_s)
                im.paste(fading, (rx, ry), fading)

    # 3. Organic Shimmer & Gaussian Bloom Pass
    arr = np.array(im).astype(np.float32)
    
    # Breathing luminescence once rose is fully bloomed (after 11.2s)
    if t > 11.2:
        shimmer_strength = min(1.0, (t - 11.2) / 1.0)
        pulse = 1.0 + 0.08 * math.sin(2.4 * t) * shimmer_strength
        arr = arr * pulse
        
    # Bloom glow
    small = cv2.resize(arr, (WIDTH // 2, HEIGHT // 2))
    glow = cv2.GaussianBlur(small, (0, 0), 4.2)
    glow = cv2.resize(glow, (WIDTH, HEIGHT))
    
    final_arr = np.clip(arr + 0.32 * glow, 0, 255).astype(np.uint8)
    return final_arr

# ----------------- Main Execution Entry Point -----------------
if __name__ == '__main__':
    print("=" * 65)
    print(" 1 ROSE, EVERY LANGUAGE - Typographic Rose Animation")
    print(f" Resolution: {WIDTH}x{HEIGHT} (Vertical 9:16) | {FPS} FPS | {DURATION}s")
    print("=" * 65, flush=True)

    t_start = time.time()
    print("Building typographic silhouette elements...", flush=True)
    heading_chars, elements = build_animation_elements()
    print(f"Total placed romantic phrases: {len(elements)} elements")
    print(f"Build completed in {time.time() - t_start:.2f}s\n", flush=True)

    # Ensure clean output file
    if os.path.exists(OUTPUT_FILE):
        try:
            os.remove(OUTPUT_FILE)
        except OSError:
            pass

    # Launch FFmpeg subprocess with high quality H.264 video encoding
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-loglevel', 'error',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{WIDTH}x{HEIGHT}', '-r', str(FPS),
        '-i', '-',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '15',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        OUTPUT_FILE
    ]

    print(f"Rendering {TOTAL_FRAMES} frames to {OUTPUT_FILE}...", flush=True)
    ff = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    t_render = time.time()
    for frame_idx in range(TOTAL_FRAMES):
        t_sec = frame_idx / float(FPS)
        frame_rgb = render_frame(t_sec, heading_chars, elements)
        ff.stdin.write(frame_rgb.tobytes())

        if (frame_idx + 1) % 30 == 0 or frame_idx == TOTAL_FRAMES - 1:
            elapsed = time.time() - t_render
            speed = (frame_idx + 1) / elapsed
            eta = (TOTAL_FRAMES - (frame_idx + 1)) / speed if speed > 0 else 0
            pct = (frame_idx + 1) / TOTAL_FRAMES * 100
            print(f"Frame {frame_idx + 1:3d}/{TOTAL_FRAMES} ({pct:5.1f}%) | Speed: {speed:4.2f} fps | Elapsed: {int(elapsed):3d}s | ETA: {int(eta):3d}s", flush=True)

    ff.stdin.close()
    ff.wait()
    total_time = time.time() - t_render
    print("\n" + "=" * 65)
    print(f"SUCCESS! Rendered {TOTAL_FRAMES} frames in {total_time:.1f}s.")
    print(f"Output saved to: {os.path.abspath(OUTPUT_FILE)}")
    print("=" * 65, flush=True)
