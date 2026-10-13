"""
Command-line interface for QQ Show 2000 Outfit Saver.
Usage:
    python cli.py https://qqshow2000.com/?id=e9fn6oxd
    python cli.py e9fn6oxd -s 2 -o my_outfit.gif
    python cli.py --ui
"""

import sys
import argparse
import webbrowser
import saver


def main():
    parser = argparse.ArgumentParser(
        description="QQ Show 2000 Outfit Saver - Downloads, composites z-index layers, and saves an animated GIF."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Outfit URL (e.g. https://qqshow2000.com/?id=e9fn6oxd) or ID (e.g. e9fn6oxd)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output GIF file path (default: qqshow_{id}_{name}.gif)",
    )
    parser.add_argument(
        "-s",
        "--scale",
        type=int,
        choices=[1, 2, 3, 4],
        default=2,
        help="Pixel-art scale factor (default: 2, for crisp 280x452)",
    )
    parser.add_argument(
        "--bg",
        "--background",
        dest="bg_mode",
        default="auto",
        help="Background mode: 'auto', 'transparent', 'canvas' (#f8f8f8), or hex color '#ffffff' (default: 'auto')",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Inspect layers and animation metadata without rendering the GIF",
    )
    parser.add_argument(
        "--ui",
        "--web",
        dest="launch_ui",
        action="store_true",
        help="Launch the interactive local web app in your browser",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port for the web app (default: 8080)",
    )

    args = parser.parse_args()

    # If --ui or --web flag is given, or if no target is provided, launch web UI
    if args.launch_ui or not args.target:
        if not args.target and not args.launch_ui:
            print("No outfit URL or ID provided. Launching web UI...")
        import server
        try:
            webbrowser.open(f"http://localhost:{args.port}")
        except Exception:
            pass
        server.run_server(args.port)
        return

    # Extract ID
    try:
        outfit_id = saver.extract_outfit_id(args.target)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"\n[1/3] Fetching outfit '{outfit_id}'...")
    try:
        outfit_data = saver.fetch_outfit_data(outfit_id)
        outfit_name = outfit_data.get("name") or "My Outfit"
        print(f"      Found: \"{outfit_name}\" (ID: {outfit_id})")
    except Exception as e:
        print(f"Error fetching outfit: {e}")
        sys.exit(1)

    layers = saver.resolve_layers(outfit_data)
    print(f"\n[2/3] Resolved {len(layers)} z-index layers:")
    for l in layers:
        cat = l.get("category", "")
        z = saver.LAYER_Z_INDEX.get(cat, 999)
        name = l.get("name", cat)
        is_def = " (default)" if l.get("isDefault") else ""
        print(f"      z={z:02d} [{cat:16s}] {name}{is_def}")

    if args.info:
        print("\n(--info flag active, skipping rendering)")
        return

    print(f"\n[3/3] Downloading assets, aligning timelines, and compositing GIF (scale={args.scale}x)...")
    try:
        res = saver.composite_outfit(
            outfit_id=outfit_id,
            output_path=args.output,
            scale=args.scale,
            bg_mode=args.bg_mode,
        )
        print("\nSUCCESS! Composite animated GIF generated:")
        print(f"  File:       {res['output_path']}")
        print(f"  Dimensions: {res['dimensions'][0]} x {res['dimensions'][1]} px")
        print(f"  Frames:     {res['frame_count']}")
        print(f"  Duration:   {res['total_duration_ms'] / 1000:.2f} seconds")
        print(f"  Size:       {res['file_size_bytes'] / 1024:.1f} KB")
    except Exception as e:
        print(f"Error compositing GIF: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
