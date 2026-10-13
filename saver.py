"""
Core compositing engine for QQ Show 2000 outfits.
Downloads layer assets, resolves z-indexes matching the qqshow2000.com engine,
synchronizes frame durations across layers, and renders a composite animated GIF.
"""

import os
import re
import math
import json
import urllib.parse
import urllib.request
from functools import reduce
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageSequence

SUPABASE_URL = "https://iuthwndljsjdwhzlxopz.supabase.co"
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1dGh3bmRsanNqZHdoemx4b3B6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg2MTM2MTUsImV4cCI6MjA3NDE4OTYxNX0."
    "q-0qS8L5lpSB-ttj1HK2wfYTu0wM44KuEJ7FhKbz2oQ"
)

# Canonical z-index layer map from qqshow2000.com
LAYER_Z_INDEX = {
    "backgrounds": 0,
    "background-decor": 1,
    "vehicle": 2,
    "wings": 3,
    "backHair": 4,
    "bottom": 5,
    "hair": 6,
    "top": 7,
    "outfit": 8,
    "makeup": 9,
    "head-set": 10,
    "frontHair": 11,
    "neckwear": 11,
    "earrings": 12,
    "face-decor": 13,
    "glasses": 14,
    "headwear": 15,
    "other-accessories": 16,
    "frame": 17,
    "text": 18,
    "companion": 19,
    "sparkle": 20,
}

# Tie-breaker order for items sharing z-index
TIE_BREAKER_ORDER = {"bottom": 0, "outfit": 1, "top": 2}

# Default body & clothing items used by the game when slots are empty
DEFAULT_ITEMS = {
    "frontHair": {
        "id": "default_frontHair",
        "name": "默认前头发",
        "image": "/assets/front-hair/default.gif",
        "category": "frontHair",
        "layer": 10,
    },
    "backHair": {
        "id": "default_backHair",
        "name": "默认后头发",
        "image": "/assets/back-hair/default.gif",
        "category": "backHair",
        "layer": 5,
    },
    "bottom": {
        "id": "default_bottom",
        "name": "默认下装",
        "image": "/assets/bottom/default.gif",
        "category": "bottom",
        "layer": 5,
    },
    "top": {
        "id": "default_top",
        "name": "默认上装",
        "image": "/assets/top/default.gif",
        "category": "top",
        "layer": 6,
    },
    "makeup": {
        "id": "default_makeup",
        "name": "默认妆容",
        "image": "/assets/makeup/default.png",
        "category": "makeup",
        "layer": 8,
    },
}


def extract_outfit_id(url_or_id: str) -> str:
    """Extracts the outfit ID from a URL or raw ID string."""
    cleaned = url_or_id.strip()
    
    # Check for ?id= or &id= or #id=
    match = re.search(r'[?&#]id=([a-zA-Z0-9_-]+)', cleaned)
    if match:
        return match.group(1)
    
    # Check if user passed just the alphanumeric ID (e.g. e9fn6oxd)
    if re.fullmatch(r'[a-zA-Z0-9_-]{4,40}', cleaned):
        return cleaned
    
    # Try finding last path segment or parameter
    match = re.search(r'([a-zA-Z0-9_-]{6,30})/?$', cleaned)
    if match:
        return match.group(1)
        
    raise ValueError(f"Could not parse a valid QQ Show outfit ID from '{url_or_id}'")


def fetch_outfit_data(outfit_id: str) -> Dict[str, Any]:
    """Fetches outfit JSON from Supabase shares table."""
    endpoint = f"{SUPABASE_URL}/rest/v1/shares?id=eq.{urllib.parse.quote(outfit_id)}&select=*"
    req = urllib.request.Request(
        endpoint,
        headers={
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "User-Agent": "QQShow-Outfit-Saver/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error fetching outfit '{outfit_id}': {e}")
    
    if not data or len(data) == 0:
        raise ValueError(f"Outfit with ID '{outfit_id}' was not found in the database.")
    
    return data[0]


def resolve_layers(outfit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Replicates the exact layer resolution and z-index ordering from qqshow2000.com:
    - Splits 'hair' into 'backHair' and 'frontHair' if present
    - Resolves conflict categories (e.g. head-set suppresses hair and makeup; outfit suppresses top and bottom)
    - Appends default items where needed
    - Sorts by z-index and tie-breakers
    """
    outfit_slots = outfit_data.get("outfit", {})
    layers = []
    present_categories = set()
    suppressed_categories = set()

    # Pass 1: Process user-configured outfit slots
    for category, item in outfit_slots.items():
        if not item:
            continue
        
        # If hair has frontHair (and optional backHair)
        if category == "hair" and isinstance(item, dict) and item.get("frontHair"):
            if item.get("backHair"):
                back = dict(item["backHair"])
                back["category"] = "backHair"
                back["isDefault"] = False
                layers.append(back)
                present_categories.add("backHair")
            
            front = dict(item["frontHair"])
            front["category"] = "frontHair"
            front["isDefault"] = False
            layers.append(front)
            present_categories.add("frontHair")
            
            suppressed_categories.add("frontHair")
            suppressed_categories.add("backHair")
        else:
            layer_item = dict(item)
            layer_item["category"] = category
            layer_item["isDefault"] = False
            layers.append(layer_item)
            present_categories.add(category)

        # Conflict suppression rules from qqshow2000.com:
        if category == "head-set":
            suppressed_categories.update(["hair", "frontHair", "backHair", "makeup"])
        if category in ["frontHair", "backHair"]:
            suppressed_categories.add("hair")
        if category == "outfit":
            suppressed_categories.update(["top", "bottom"])

    # Pass 2: Fill in default items for empty, non-suppressed categories
    for cat_name in LAYER_Z_INDEX.keys():
        if cat_name not in present_categories and cat_name not in suppressed_categories:
            default_item = DEFAULT_ITEMS.get(cat_name)
            if default_item:
                item_copy = dict(default_item)
                item_copy["isDefault"] = True
                layers.append(item_copy)

    # Pass 3: Stable sort by z-index and tie-breaker
    def sort_key(entry):
        cat = entry.get("category", "")
        z = LAYER_Z_INDEX.get(cat, 999)
        tie = TIE_BREAKER_ORDER.get(cat, 0)
        return (z, tie)

    layers.sort(key=sort_key)
    return layers


def download_asset(image_rel_path: str, cache_dir: str = ".cache/assets") -> str:
    """Downloads an asset from qqshow2000.com and caches it locally."""
    os.makedirs(cache_dir, exist_ok=True)
    
    # Normalize path
    clean_path = image_rel_path.lstrip("/")
    # Build safe local cache filename
    safe_name = re.sub(r'[/\\?%*:|"<>]', '_', clean_path)
    local_file = os.path.join(cache_dir, safe_name)
    
    if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
        return local_file
    
    encoded_url = f"https://qqshow2000.com/{urllib.parse.quote(clean_path)}"
    req = urllib.request.Request(
        encoded_url,
        headers={"User-Agent": "QQShow-Outfit-Saver/1.0"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp, open(local_file, "wb") as f:
        f.write(resp.read())
        
    return local_file


def extract_layer_frames(image_path: str) -> Tuple[List[Image.Image], List[int]]:
    """
    Extracts RGBA frames and their durations from a GIF or PNG image.
    Ensures each frame is a complete RGBA image.
    """
    im = Image.open(image_path)
    frames = []
    durations = []
    
    n_frames = getattr(im, "n_frames", 1)
    
    for i in range(n_frames):
        im.seek(i)
        # Convert to RGBA
        frame_rgba = im.convert("RGBA")
        frames.append(frame_rgba)
        
        # Duration handling: GIF standard in hundredths of a second
        dur = im.info.get("duration", 100)
        if not dur or dur <= 10:
            dur = 100
        durations.append(dur)
        
    return frames, durations


def compute_lcm(a: int, b: int) -> int:
    """Least Common Multiple of two integers."""
    return abs(a * b) // math.gcd(a, b) if a and b else 0


def quantize_frame_with_transparency(rgba_img: Image.Image) -> Image.Image:
    """
    Converts an RGBA Image to a 256-color palette (P mode) image with crisp transparency.
    Uses index 255 for full transparency and 255 colors for RGB.
    """
    alpha = rgba_img.getchannel("A")
    # Mask of transparent pixels (< 128 alpha)
    mask = Image.eval(alpha, lambda a: 255 if a < 128 else 0)
    
    # Quantize RGB image to 255 colors
    rgb_img = rgba_img.convert("RGB")
    p_img = rgb_img.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    
    # Set mask area to palette index 255
    p_img.paste(255, mask)
    p_img.info["transparency"] = 255
    return p_img


def composite_outfit(
    outfit_id: str,
    output_path: Optional[str] = None,
    scale: int = 1,
    bg_mode: str = "auto",
    max_duration_ms: int = 12000,
    cache_dir: str = ".cache/assets",
) -> Dict[str, Any]:
    """
    Full pipeline:
    1. Fetches outfit data from Supabase.
    2. Resolves layers & downloads GIFs.
    3. Calculates animation timeline (LCM of frame cycles, with max duration safety).
    4. Composites every frame at native resolution (140x226).
    5. Optionally scales up with crisp nearest-neighbor sampling.
    6. Saves and returns summary info.
    """
    # 1. Fetch
    outfit_data = fetch_outfit_data(outfit_id)
    outfit_name = outfit_data.get("name") or "My Outfit"
    
    # 2. Resolve layers
    layers = resolve_layers(outfit_data)
    
    # 3. Download & extract layer frames
    loaded_layers = []
    has_background_layer = False
    
    for layer in layers:
        img_rel = layer.get("image")
        if not img_rel:
            continue
        
        category = layer.get("category", "")
        if category in ["backgrounds", "background-decor"]:
            has_background_layer = True
            
        local_path = download_asset(img_rel, cache_dir=cache_dir)
        frames, durations = extract_layer_frames(local_path)
        total_cycle = sum(durations)
        
        loaded_layers.append({
            "category": category,
            "name": layer.get("name", category),
            "z_index": LAYER_Z_INDEX.get(category, 999),
            "is_default": layer.get("isDefault", False),
            "frames": frames,
            "durations": durations,
            "total_cycle": total_cycle,
            "image_url": f"https://qqshow2000.com{img_rel}"
        })

    # Determine canvas dimensions from loaded layers
    width = 140
    height = 226
    if loaded_layers and loaded_layers[0]["frames"]:
        width, height = loaded_layers[0]["frames"][0].size

    # Background color configuration
    # bg_mode can be 'auto', 'transparent', 'canvas' (#f8f8f8), or hex '#ffffff'
    bg_color = (0, 0, 0, 0)
    if bg_mode == "canvas" or (bg_mode == "auto" and not has_background_layer):
        bg_color = (248, 248, 248, 255)  # #f8f8f8 website container background
    elif bg_mode.startswith("#"):
        hex_val = bg_mode.lstrip("#")
        if len(hex_val) == 6:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
            bg_color = (r, g, b, 255)

    # 4. Synchronize animation timeline
    animated_cycles = [l["total_cycle"] for l in loaded_layers if len(l["frames"]) > 1]
    
    if animated_cycles:
        total_loop_ms = reduce(compute_lcm, animated_cycles)
        # Guard against absurd LCMs (cap to max_duration_ms)
        if total_loop_ms > max_duration_ms:
            # Find closest multiple or cap
            total_loop_ms = max_duration_ms
    else:
        total_loop_ms = 1000

    # Collect all frame transition timestamps in [0, total_loop_ms)
    timestamps = set([0])
    for l in loaded_layers:
        if len(l["frames"]) <= 1:
            continue
        t = 0
        while t < total_loop_ms:
            for d in l["durations"]:
                t += d
                if t < total_loop_ms:
                    timestamps.add(t)

    sorted_timestamps = sorted(timestamps)

    # Build timeline intervals (start_time, duration)
    intervals = []
    for i in range(len(sorted_timestamps)):
        t_start = sorted_timestamps[i]
        t_end = sorted_timestamps[i + 1] if i + 1 < len(sorted_timestamps) else total_loop_ms
        dur = t_end - t_start
        if dur > 0:
            intervals.append((t_start, dur))

    # 5. Composite frames
    composite_frames: List[Image.Image] = []
    composite_durations: List[int] = []

    for t_start, dur in intervals:
        canvas = Image.new("RGBA", (width, height), bg_color)
        
        for l in loaded_layers:
            frames = l["frames"]
            durations = l["durations"]
            if len(frames) == 1:
                active_frame = frames[0]
            else:
                t_in_cycle = t_start % l["total_cycle"]
                elapsed = 0
                idx = 0
                for i, d in enumerate(durations):
                    if elapsed + d > t_in_cycle:
                        idx = i
                        break
                    elapsed += d
                active_frame = frames[idx]

            canvas = Image.alpha_composite(canvas, active_frame)

        composite_frames.append(canvas)
        composite_durations.append(dur)

    # 6. Optimize: merge consecutive identical frames
    merged_frames: List[Image.Image] = []
    merged_durations: List[int] = []

    for f, d in zip(composite_frames, composite_durations):
        if not merged_frames:
            merged_frames.append(f)
            merged_durations.append(d)
        else:
            # Check if current frame equals previous frame by comparing byte data
            if f.tobytes() == merged_frames[-1].tobytes():
                merged_durations[-1] += d
            else:
                merged_frames.append(f)
                merged_durations.append(d)

    # 7. Scale up if requested (Nearest Neighbor to preserve pixel art crispness)
    final_frames = []
    out_width = width * scale
    out_height = height * scale
    
    for f in merged_frames:
        if scale > 1:
            scaled = f.resize((out_width, out_height), resample=Image.Resampling.NEAREST)
        else:
            scaled = f
        final_frames.append(scaled)

    # Determine default output path if not specified
    if not output_path:
        clean_name = re.sub(r'[\\/*?:"<>| ]', '_', outfit_name)
        output_path = f"qqshow_{outfit_id}_{clean_name}.gif"

    # 8. Quantize & Save GIF
    is_transparent = any(f.getchannel("A").getextrema()[0] < 255 for f in final_frames)
    
    if is_transparent:
        palette_frames = [quantize_frame_with_transparency(f) for f in final_frames]
        palette_frames[0].save(
            output_path,
            save_all=True,
            append_images=palette_frames[1:],
            duration=merged_durations,
            loop=0,
            disposal=2,
        )
    else:
        # Fully opaque: standard median cut quantization
        palette_frames = [
            f.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            for f in final_frames
        ]
        palette_frames[0].save(
            output_path,
            save_all=True,
            append_images=palette_frames[1:],
            duration=merged_durations,
            loop=0,
            disposal=2,
        )

    file_size = os.path.getsize(output_path)

    return {
        "id": outfit_id,
        "name": outfit_name,
        "language": outfit_data.get("language", "zh"),
        "output_path": os.path.abspath(output_path),
        "dimensions": (out_width, out_height),
        "scale": scale,
        "frame_count": len(final_frames),
        "total_duration_ms": sum(merged_durations),
        "file_size_bytes": file_size,
        "is_transparent": is_transparent,
        "layers": [
            {
                "category": l["category"],
                "name": l["name"],
                "z_index": l["z_index"],
                "is_default": l["is_default"],
                "frame_count": len(l["frames"]),
                "cycle_ms": l["total_cycle"],
            }
            for l in loaded_layers
        ],
    }


if __name__ == "__main__":
    import cli
    cli.main()

