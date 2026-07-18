#!/usr/bin/env python3
"""Phase 3 · EV Bus Video Analytics — CLI Runner.

Processes every .mp4 / .avi in the Videos/ directory through the full
video analytics pipeline and writes all outputs to Video_Analytics/outputs/.

Directory layout expected
-------------------------
  Phase_3_Video_Analytics/
  ├── Videos/
  │   ├── eka.mp4
  │   ├── olectra.mp4
  │   ├── switch.mp4
  │   └── tata.mp4
  └── Video_Analytics/
      ├── scripts/
      │   ├── video_analytics_lib.py   ← library
      │   └── run_video_pipeline.py    ← this file
      └── outputs/
          ├── frames/       per-brand keyframe JPEG sets
          ├── per_frame/    per-frame CSV (one file per video)
          ├── summaries/    per-video JSON summary
          ├── charts/       PNG charts
          └── master_video_analysis.csv

Run
---
  cd Phase_3_Video_Analytics/Video_Analytics
  python scripts/run_video_pipeline.py

  # override defaults:
  python scripts/run_video_pipeline.py \\
      --videos_dir ../../Videos \\
      --output_dir ./outputs \\
      --sample_fps 2 \\
      --max_frames 300
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap:  make sure the script can import the lib regardless of cwd
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from video_analytics_lib import (   # noqa: E402
    _TORCH_AVAILABLE,
    process_video,
    summarise_video,
    generate_all_charts,
)

import pandas as pd  # noqa: E402


VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv"}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="EV Bus Video Analytics Pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--videos_dir",
        default=str(_HERE.parent.parent / "Videos"),
        help="Directory containing input video files",
    )
    parser.add_argument(
        "--output_dir",
        default=str(_HERE.parent / "outputs"),
        help="Root output directory",
    )
    parser.add_argument(
        "--sample_fps", type=float, default=1.0,
        help="Frames to sample per second of video (higher = more frames, slower)",
    )
    parser.add_argument(
        "--max_frames", type=int, default=200,
        help="Hard cap on frames extracted per video",
    )
    parser.add_argument(
        "--verbose", action="store_true", default=True,
        help="Print per-frame progress",
    )
    args = parser.parse_args()

    videos_dir = Path(args.videos_dir)
    output_dir = Path(args.output_dir)

    # Verify videos directory
    if not videos_dir.exists():
        print(f"ERROR: Videos directory not found: {videos_dir}")
        sys.exit(1)

    video_files = sorted(
        p for p in videos_dir.iterdir() if p.suffix.lower() in VIDEO_EXTS
    )
    if not video_files:
        print(f"ERROR: No video files found in {videos_dir}")
        sys.exit(1)

    # Create output directories
    frames_root = output_dir / "frames"
    perframe_dir = output_dir / "per_frame"
    summaries_dir = output_dir / "summaries"
    charts_dir = output_dir / "charts"
    for d in [frames_root, perframe_dir, summaries_dir, charts_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  EV BUS VIDEO ANALYTICS PIPELINE")
    print(f"  Run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Videos      : {len(video_files)} files in {videos_dir}")
    print(f"  Sample FPS  : {args.sample_fps}")
    print(f"  Max frames  : {args.max_frames}")
    print(f"  Deep models : {'YES (torch + transformers)' if _TORCH_AVAILABLE else 'NO  (OpenCV + OCR only)'}")
    print("=" * 60)

    all_frames: list[pd.DataFrame] = []
    summaries: list[dict] = []
    per_video_dfs: dict[str, pd.DataFrame] = {}
    timings: dict[str, float] = {}

    # ---------------------------------------------------------------------------
    # PROCESS EACH VIDEO
    # ---------------------------------------------------------------------------
    for vf in video_files:
        brand = vf.stem.upper()
        t0 = time.time()

        frames_dir = frames_root / brand.lower()
        df = process_video(
            vf, frames_dir,
            sample_fps=args.sample_fps,
            max_frames=args.max_frames,
            verbose=args.verbose,
        )

        # Save per-frame CSV
        csv_path = perframe_dir / f"{brand.lower()}_frames.csv"
        df.to_csv(csv_path, index=False)
        print(f"\n      ✔ Per-frame CSV saved: {csv_path.name}")

        # Build per-video summary
        summary = summarise_video(df)
        summaries.append(summary)
        per_video_dfs[brand] = df
        all_frames.append(df)

        # Save per-video JSON
        json_path = summaries_dir / f"{brand.lower()}_summary.json"
        with open(json_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"      ✔ Summary JSON saved:  {json_path.name}")

        elapsed = time.time() - t0
        timings[brand] = round(elapsed, 1)
        print(f"      ✔ {brand} done in {elapsed:.1f}s\n")

    # ---------------------------------------------------------------------------
    # MASTER CSV  (all videos combined)
    # ---------------------------------------------------------------------------
    if all_frames:
        master_df = pd.concat(all_frames, ignore_index=True)
        master_path = output_dir / "master_video_analysis.csv"
        master_df.to_csv(master_path, index=False)
        print(f"\n✔ Master CSV saved: {master_path}  ({len(master_df)} frame rows)")
    else:
        master_df = pd.DataFrame()

    # ---------------------------------------------------------------------------
    # COMPARATIVE SUMMARY CSV
    # ---------------------------------------------------------------------------
    compare_rows = []
    for s in summaries:
        row = {k: v for k, v in s.items()
               if not isinstance(v, (dict, list))}
        # Flatten text_themes
        for theme, cnt in s.get("text_themes", {}).items():
            row[f"theme_{theme}"] = cnt
        compare_rows.append(row)
    compare_df = pd.DataFrame(compare_rows)
    compare_path = summaries_dir / "brand_comparison.csv"
    compare_df.to_csv(compare_path, index=False)
    print(f"✔ Brand comparison CSV saved: {compare_path.name}")

    # ---------------------------------------------------------------------------
    # CHARTS
    # ---------------------------------------------------------------------------
    print("\n[Generating charts…]")
    chart_paths = generate_all_charts(
        master_df, summaries, charts_dir, per_video_dfs=per_video_dfs
    )
    print(f"✔ {len(chart_paths)} charts saved to {charts_dir}")

    # ---------------------------------------------------------------------------
    # MASTER JSON SUMMARY
    # ---------------------------------------------------------------------------
    run_meta = {
        "run_timestamp": datetime.now().isoformat(),
        "videos_dir": str(videos_dir),
        "output_dir": str(output_dir),
        "sample_fps": args.sample_fps,
        "max_frames": args.max_frames,
        "deep_models_used": _TORCH_AVAILABLE,
        "videos_processed": [s["brand"] for s in summaries],
        "timings_seconds": timings,
        "total_frames_analysed": int(master_df.shape[0]) if not master_df.empty else 0,
        "summaries": summaries,
    }
    run_json_path = output_dir / "pipeline_run_summary.json"
    with open(run_json_path, "w") as f:
        json.dump(run_meta, f, indent=2, default=str)

    # ---------------------------------------------------------------------------
    # FINAL REPORT  (console)
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("  PIPELINE COMPLETE — KEY FINDINGS")
    print("=" * 60)
    print(f"\n{'Brand':<12} {'Dur(s)':>7} {'Frames':>7} {'Cuts/min':>9} "
          f"{'Avg Bright':>11} {'OCR%':>6} {'DomTheme':<22}")
    print("-" * 80)
    for s in summaries:
        print(
            f"{s['brand']:<12} "
            f"{s.get('duration_seconds', 0):>7.1f} "
            f"{s.get('total_frames_analysed', 0):>7} "
            f"{s.get('cuts_per_minute', 0):>9.2f} "
            f"{s.get('avg_brightness', 0):>11.1f} "
            f"{s.get('ocr_text_pct', 0):>6.1f}% "
            f"{s.get('dominant_text_theme', 'n/a'):<22}"
        )
    print("-" * 80)
    print("\nOutputs written to:")
    print(f"  Frames       : {frames_root}")
    print(f"  Per-frame CSV: {perframe_dir}")
    print(f"  Summaries    : {summaries_dir}")
    print(f"  Charts       : {charts_dir}")
    print(f"  Master CSV   : {output_dir / 'master_video_analysis.csv'}")
    print(f"  Run JSON     : {run_json_path}")
    if not _TORCH_AVAILABLE:
        print("\n  ⚠  Deep models (BLIP / DETR / CLIP) were NOT used.")
        print("     Install torch + transformers for richer feature extraction:")
        print("     pip install torch torchvision transformers")
    print("\nDone.")


if __name__ == "__main__":
    main()
