"""Phase 3 · Video Analytics Library — EV Bus Market Analysis.

Companion library for the Multimodal AI Strategy project.
Mirrors the structure of Phase 2's pipeline_lib.py but operates on video files.

Pipeline stages:
  METADATA   : duration, fps, resolution, file size
  FRAMES     : extract keyframes at configurable interval
  LOW-LEVEL  : brightness, contrast, saturation, sharpness, edge density,
               warm/cool bias, colourfulness, symmetry, visual balance
  OBJECTS    : DETR object detection  (bus / person / truck / traffic-light counts)
               → graceful fallback if torch/transformers not installed
  CAPTIONS   : BLIP scene descriptions per frame
               → graceful fallback if torch/transformers not installed
  CLIP       : zero-shot classification for EV-bus–relevant themes
               → graceful fallback if torch/transformers not installed
  OCR        : Tesseract text extraction per frame (always available)
  SENTIMENT  : VADER sentiment on in-frame OCR text (narrative framing)
  SHOT CUTS  : pixel-difference–based shot boundary detection
  AGGREGATION: per-video statistics, theme frequencies, pacing metrics
  CHARTS     : automated chart generation (always available)

Usage
-----
  from video_analytics_lib import process_video, aggregate_all, generate_all_charts

  df = process_video("Videos/eka.mp4", frames_dir="outputs/frames/eka")
  summary = aggregate_all([df], brand_names=["EKA"])

Dependencies (core — always required)
--------------------------------------
  opencv-python, numpy, Pillow, pandas, matplotlib,
  vaderSentiment, scipy, scikit-learn, pytesseract

Dependencies (optional — enables BLIP / DETR / CLIP)
------------------------------------------------------
  torch, torchvision, transformers
"""
from __future__ import annotations

import json
import math
import os
import re
import warnings
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import pandas as pd
from PIL import Image

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# OPTIONAL heavy-model flag
# ---------------------------------------------------------------------------
try:
    import torch
    import transformers  # noqa: F401
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

# ---------------------------------------------------------------------------
# EV-BUS CLIP PROMPTS  (adapted from Phase 2 image pipeline)
# ---------------------------------------------------------------------------
CLIP_BINARY_VIDEO = {
    "hl_bus_exterior":         ("an electric bus exterior driving on a city road",
                                "an image with no bus exterior visible"),
    "hl_bus_interior":         ("the interior of an electric bus with seats and passengers",
                                "an exterior shot or non-bus image"),
    "hl_charging_infra":       ("electric bus charging station or charging infrastructure",
                                "a bus with no charging equipment visible"),
    "hl_fleet_scale":          ("a large fleet of many electric buses lined up together",
                                "a single bus or no bus visible"),
    "hl_govt_ceremony":        ("a government or corporate handover ceremony for new buses",
                                "an ordinary bus video with no ceremony"),
    "hl_tech_showcase":        ("advanced technology dashboard screens battery systems in a bus",
                                "a plain bus interior with no technology emphasis"),
    "hl_passenger_comfort":    ("comfortable passengers enjoying a smooth electric bus ride",
                                "an empty bus or non-passenger content"),
    "hl_operational_proof":    ("real-world footage of buses in daily passenger service",
                                "a studio marketing render or product demo with no real service"),
    "hl_safety_feature":       ("bus safety features ADAS cameras emergency systems",
                                "a bus video with no visible safety features"),
    "hl_brand_marketing":      ("a polished brand marketing or advertisement video for a bus",
                                "raw documentary footage with no marketing production"),
}

CLIP_SETTING_VIDEO = [
    "urban city road or highway",
    "rural highway or expressway",
    "bus depot or maintenance yard",
    "studio or product launch event",
    "government or corporate ceremony",
]

CLIP_THEMES_VIDEO = {
    "theme_technology":    ("emphasising advanced technology innovation and electronics",
                            "no emphasis on technology"),
    "theme_comfort":       ("showcasing passenger comfort spacious seats and smooth ride",
                            "not about comfort"),
    "theme_sustainability":("green eco-friendly zero-emission clean energy message",
                            "no sustainability or green theme"),
    "theme_reliability":   ("demonstrating reliability uptime and dependable service",
                            "no reliability or uptime message"),
    "theme_affordability": ("emphasising cost savings affordability or value for money",
                            "no pricing or affordability message"),
    "theme_safety":        ("emphasising safety security and passenger protection",
                            "no safety message"),
}

CLIP_PERCEPTION_VIDEO = {
    "pxy_trust":           ("a trustworthy well-established reliable bus brand",
                            "an untrustworthy or unreliable bus brand"),
    "pxy_modernity":       ("a cutting-edge modern futuristic electric bus",
                            "an outdated conventional diesel bus"),
    "pxy_comfort":         ("a comfortable spacious premium bus experience",
                            "an uncomfortable cramped bus"),
    "pxy_sustainability":  ("a clean zero-emission environmentally friendly electric bus",
                            "a polluting diesel or petrol bus"),
    "pxy_operational_scale":("a proven bus deployed at scale serving many passengers",
                             "a prototype or limited-deployment bus"),
    "pxy_visual_production":("a high-production-quality professional brand video",
                             "a low-quality amateur or raw video"),
}

# ---------------------------------------------------------------------------
# DEVICE / MODEL CACHING
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _device() -> str:
    if _TORCH_AVAILABLE:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    return "cpu"


@lru_cache(maxsize=1)
def _blip():
    if not _TORCH_AVAILABLE:
        return None, None
    from transformers import BlipProcessor, BlipForConditionalGeneration
    proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base")
    return proc, model.to(_device()).eval()


@lru_cache(maxsize=1)
def _detr():
    if not _TORCH_AVAILABLE:
        return None, None
    from transformers import DetrImageProcessor, DetrForObjectDetection
    proc = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
    return proc, model.to(_device()).eval()


@lru_cache(maxsize=1)
def _clip():
    if not _TORCH_AVAILABLE:
        return None, None
    from transformers import CLIPProcessor, CLIPModel
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    return proc, model.to(_device()).eval()


# ---------------------------------------------------------------------------
# VIDEO METADATA
# ---------------------------------------------------------------------------
def get_video_metadata(video_path: Path) -> dict:
    """Return basic video properties without decoding frames."""
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    duration_s = total_frames / fps if fps > 0 else 0
    file_size_mb = round(Path(video_path).stat().st_size / (1024 ** 2), 2)
    return {
        "video_file": Path(video_path).name,
        "brand": Path(video_path).stem.upper(),
        "fps": round(fps, 2),
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "resolution": f"{width}x{height}",
        "duration_seconds": round(duration_s, 2),
        "duration_minutes": round(duration_s / 60, 2),
        "file_size_mb": file_size_mb,
        "aspect_ratio": round(width / height, 3) if height > 0 else None,
    }


# ---------------------------------------------------------------------------
# FRAME EXTRACTION
# ---------------------------------------------------------------------------
def extract_frames(
    video_path: Path,
    output_dir: Path,
    sample_fps: float = 1.0,
    max_frames: int = 300,
) -> list[Path]:
    """
    Extract frames at *sample_fps* frames per second.

    Parameters
    ----------
    video_path  : path to mp4 / avi
    output_dir  : directory to save JPEGs
    sample_fps  : how many frames to sample per second of video (default 1)
    max_frames  : hard cap on total frames extracted

    Returns
    -------
    Sorted list of frame paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps <= 0:
        video_fps = 25.0
    frame_interval = max(1, int(round(video_fps / sample_fps)))

    saved, frame_idx = [], 0
    while cap.isOpened() and len(saved) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0:
            out_path = output_dir / f"frame_{frame_idx:06d}.jpg"
            cv2.imwrite(str(out_path), frame)
            saved.append(out_path)
        frame_idx += 1
    cap.release()
    return sorted(saved)


# ---------------------------------------------------------------------------
# LOW-LEVEL FRAME FEATURES  (pure OpenCV / NumPy)
# ---------------------------------------------------------------------------
def _warm_cool_bias(rgb: np.ndarray) -> float:
    r, g, b = rgb[..., 0].mean(), rgb[..., 1].mean(), rgb[..., 2].mean()
    warm = (r + 0.5 * g) / 255.0
    cool = (b + 0.5 * g) / 255.0
    denom = warm + cool
    return round((warm - cool) / denom, 3) if denom > 0 else 0.0


def _colourfulness(rgb: np.ndarray) -> float:
    R = rgb[..., 0].astype(float); G = rgb[..., 1].astype(float); B = rgb[..., 2].astype(float)
    rg = R - G; yb = 0.5 * (R + G) - B
    return round(math.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * math.sqrt(rg.mean() ** 2 + yb.mean() ** 2), 2)


def _edge_density(gray: np.ndarray) -> float:
    edges = cv2.Canny(gray, 100, 200)
    return round(float((edges > 0).mean()), 4)


def _gradient_energy(gray: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    return np.hypot(gx, gy)


def _visual_balance(gray: np.ndarray) -> float:
    energy = _gradient_energy(gray) + 1e-9
    h, w = gray.shape
    left = energy[:, :w // 2].sum(); right = energy[:, w - w // 2:].sum()
    top = energy[:h // 2, :].sum(); bot = energy[h - h // 2:, :].sum()
    return round(float((1 - abs(left - right) / (left + right) + 1 - abs(top - bot) / (top + bot)) / 2), 3)


def _figure_ground(gray: np.ndarray) -> float:
    energy = _gradient_energy(gray)
    h, w = gray.shape
    cy0, cy1 = int(h * 0.25), int(h * 0.75)
    cx0, cx1 = int(w * 0.25), int(w * 0.75)
    center = energy[cy0:cy1, cx0:cx1].mean()
    mask = np.ones((h, w), bool); mask[cy0:cy1, cx0:cx1] = False
    border = energy[mask].mean()
    return round(float(center / (center + border + 1e-9)), 3)


def _motion_blur_score(gray: np.ndarray) -> float:
    """Laplacian variance — low = blurry/motion-heavy, high = sharp/static."""
    return round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2)


def low_level_features(frame_path: Path) -> Optional[dict]:
    """Extract pixel-level features from a single frame."""
    bgr = cv2.imread(str(frame_path))
    if bgr is None:
        return None
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return {
        "width": w, "height": h,
        "brightness": round(float(gray.mean()), 2),
        "contrast": round(float(gray.std()), 2),
        "saturation": round(float(hsv[..., 1].mean()), 2),
        "sharpness": _motion_blur_score(gray),
        "warm_cool_bias": _warm_cool_bias(rgb),
        "colourfulness": _colourfulness(rgb),
        "edge_density": _edge_density(gray),
        "visual_balance": _visual_balance(gray),
        "figure_ground_sep": _figure_ground(gray),
    }


# ---------------------------------------------------------------------------
# SHOT BOUNDARY DETECTION  (pixel-difference based)
# ---------------------------------------------------------------------------
def detect_shot_boundaries(frame_paths: list[Path], threshold_pct: float = 90.0) -> list[int]:
    """
    Detect shot cuts using mean-absolute-pixel-difference between consecutive frames.

    Returns indices (into frame_paths) where a cut likely occurs.
    """
    diffs = []
    prev_gray = None
    for p in frame_paths:
        bgr = cv2.imread(str(p))
        if bgr is None:
            diffs.append(0.0)
            continue
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (160, 90))  # fast comparison
        if prev_gray is None:
            diffs.append(0.0)
        else:
            diff = float(np.abs(gray.astype(float) - prev_gray.astype(float)).mean())
            diffs.append(diff)
        prev_gray = gray
    diffs_arr = np.array(diffs)
    threshold = np.percentile(diffs_arr[1:], threshold_pct) if len(diffs_arr) > 1 else 0
    boundaries = [i for i, d in enumerate(diffs_arr) if i > 0 and d >= threshold]
    return boundaries, diffs_arr.tolist()


# ---------------------------------------------------------------------------
# OCR + SENTIMENT
# ---------------------------------------------------------------------------
def ocr_frame(pil: Image.Image) -> str:
    """Extract any on-screen text (subtitles, captions, lower-thirds)."""
    try:
        import pytesseract
        return pytesseract.image_to_string(pil.convert("RGB")).strip()
    except Exception:
        return ""


def vader_sentiment(text: str) -> dict:
    """VADER sentiment on OCR-extracted text (narrative framing proxy)."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    if not text or not text.strip():
        return {"nf_neg": None, "nf_neu": None, "nf_pos": None,
                "nf_compound": None, "nf_label": "no_text"}
    s = SentimentIntensityAnalyzer().polarity_scores(text)
    lbl = ("positive" if s["compound"] >= 0.05
           else "negative" if s["compound"] <= -0.05 else "neutral")
    return {"nf_neg": s["neg"], "nf_neu": s["neu"],
            "nf_pos": s["pos"], "nf_compound": s["compound"], "nf_label": lbl}


# ---------------------------------------------------------------------------
# DEEP-LEARNING FEATURES  (optional — requires torch + transformers)
# ---------------------------------------------------------------------------
_DETR_KEEP = {"bus", "person", "truck", "car", "train",
              "traffic light", "bicycle", "motorcycle"}


def detect_objects(pil: Image.Image, threshold: float = 0.7) -> Counter:
    """DETR object detection. Returns empty Counter if torch unavailable."""
    if not _TORCH_AVAILABLE:
        return Counter()
    import torch
    proc, model = _detr()
    if proc is None:
        return Counter()
    inputs = proc(images=pil, return_tensors="pt").to(_device())
    with torch.no_grad():
        out = model(**inputs)
    sizes = torch.tensor([pil.size[::-1]])
    res = proc.post_process_object_detection(out, target_sizes=sizes, threshold=threshold)[0]
    labels = [model.config.id2label[int(l)] for l in res["labels"]]
    return Counter(l for l in labels if l in _DETR_KEEP)


def blip_caption(pil: Image.Image) -> str:
    """BLIP scene caption. Returns empty string if torch unavailable."""
    if not _TORCH_AVAILABLE:
        return ""
    import torch
    proc, model = _blip()
    if proc is None:
        return ""
    inputs = proc(pil, return_tensors="pt").to(_device())
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=40)
    return proc.decode(out[0], skip_special_tokens=True)


def _as_embed(x):
    import torch
    return x if torch.is_tensor(x) else x.pooler_output


@lru_cache(maxsize=1)
def _clip_text_bank():
    """Encode every CLIP prompt once and cache."""
    if not _TORCH_AVAILABLE:
        return None, None, None
    import torch
    proc, model = _clip()
    if proc is None:
        return None, None, None
    prompts, slices = [], {}
    i = 0
    for name, (pos, neg) in {**CLIP_BINARY_VIDEO, **CLIP_THEMES_VIDEO,
                               **CLIP_PERCEPTION_VIDEO}.items():
        slices[name] = ("pair", i); prompts += [pos, neg]; i += 2
    slices["_setting"] = ("multi", i); prompts += CLIP_SETTING_VIDEO; i += len(CLIP_SETTING_VIDEO)
    with torch.no_grad():
        tok = proc(text=prompts, return_tensors="pt", padding=True).to(_device())
        tf = _as_embed(model.get_text_features(**tok))
        tf = tf / tf.norm(dim=-1, keepdim=True)
    scale = float(model.logit_scale.exp())
    return tf, slices, scale


def clip_features(pil: Image.Image) -> dict:
    """CLIP zero-shot features. Returns empty dict if torch unavailable."""
    if not _TORCH_AVAILABLE:
        return {}
    import torch
    proc, model = _clip()
    tf, slices, scale = _clip_text_bank()
    if proc is None or tf is None:
        return {}
    with torch.no_grad():
        img = proc(images=pil, return_tensors="pt").to(_device())
        vf = _as_embed(model.get_image_features(**img))
        vf = vf / vf.norm(dim=-1, keepdim=True)
        sims = (scale * (vf @ tf.T)[0]).cpu()
    out = {}
    for name, (kind, i) in slices.items():
        if kind == "pair":
            p = torch.softmax(sims[i:i + 2], dim=0)[0].item()
            if name.startswith("pxy_"):
                out[name] = round(p * 100, 1)
            else:
                out[name] = round(p, 3)
                out[name + "_flag"] = bool(p >= 0.5)
    kind, i = slices["_setting"]
    seg = torch.softmax(sims[i:i + len(CLIP_SETTING_VIDEO)], dim=0)
    labels = ["urban_road", "rural_highway", "depot_yard", "studio_launch", "govt_ceremony"]
    out["hl_setting"] = labels[int(seg.argmax())]
    out["hl_setting_conf"] = round(float(seg.max()), 3)
    return out


# ---------------------------------------------------------------------------
# STORYBOARD FRAME SELECTION
# ---------------------------------------------------------------------------
def select_keyframes(
    frame_paths: list[Path],
    shot_boundaries: list[int],
    pixel_diffs: list[float],
    n_top: int = 10,
) -> dict:
    """
    Return two sets of notable frames:
      storyboard  — first frame after each shot cut (visual structure)
      peak_motion — top-N frames with highest inter-frame motion
    """
    storyboard = [frame_paths[b] for b in shot_boundaries if b < len(frame_paths)]
    diffs_arr = np.array(pixel_diffs)
    top_idx = np.argsort(diffs_arr)[-n_top:]
    peak_motion = [frame_paths[i] for i in sorted(top_idx) if i < len(frame_paths)]
    return {"storyboard": storyboard, "peak_motion": peak_motion}


# ---------------------------------------------------------------------------
# TEXT THEME EXTRACTION  (from OCR corpus across all frames)
# ---------------------------------------------------------------------------
_STOP_WORDS = {
    "the", "and", "for", "with", "from", "you", "are", "this", "that",
    "they", "their", "has", "have", "been", "not", "but", "all", "any",
    "was", "were", "its", "can", "will", "more", "than", "into", "who",
    "how", "what", "why", "when", "our", "your", "new", "now", "get",
    "www", "http", "https", "com", "also", "just", "one", "two",
}

_EV_BUS_THEME_KEYWORDS = {
    "battery_technology":   {"battery", "kwh", "range", "charge", "charging", "lithium",
                             "energy", "power", "storage", "cell"},
    "safety":               {"safety", "safe", "adas", "brake", "camera", "alert",
                             "emergency", "airbag", "sensor"},
    "passenger_comfort":    {"comfort", "seat", "ac", "interior", "space", "passenger",
                             "legroom", "wifi", "usb", "smooth"},
    "technology":           {"technology", "tech", "ai", "smart", "digital", "connected",
                             "software", "system", "iot", "automation"},
    "sustainability":       {"green", "electric", "emission", "clean", "eco", "zero",
                             "sustainable", "environment", "carbon", "renewable"},
    "reliability":          {"reliable", "reliability", "uptime", "service", "maintain",
                             "warranty", "durable", "performance", "proven", "tested"},
    "cost_economics":       {"cost", "price", "saving", "efficient", "economy", "per",
                             "km", "kilometre", "affordable", "total"},
    "govt_policy":          {"government", "ministry", "scheme", "tender", "subsidy",
                             "policy", "national", "india", "state", "pmgsy"},
    "brand_trust":          {"trust", "quality", "certified", "iso", "partner", "global",
                             "experience", "years", "leader", "best"},
    "fleet_operations":     {"fleet", "depot", "route", "operator", "schedule", "city",
                             "transport", "bus", "buses", "network"},
}


def extract_text_themes(ocr_texts: list[str]) -> dict:
    """Count EV-bus keyword hits across all OCR-extracted frame texts."""
    combined = " ".join(t.lower() for t in ocr_texts if isinstance(t, str))
    tokens = set(re.sub(r"[^a-z\s]", " ", combined).split())
    hits = {}
    for theme, kws in _EV_BUS_THEME_KEYWORDS.items():
        hits[theme] = len(kws & tokens)
    return hits


# ---------------------------------------------------------------------------
# PER-VIDEO ORCHESTRATION
# ---------------------------------------------------------------------------
def process_video(
    video_path: Path,
    frames_dir: Path,
    sample_fps: float = 1.0,
    max_frames: int = 200,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Full per-video pipeline.

    1. Extract frames at `sample_fps` per second of video.
    2. For each frame: low-level features + OCR + VADER.
       If torch available: DETR + BLIP + CLIP.
    3. Detect shot boundaries.
    4. Return one-row-per-frame DataFrame.
    """
    video_path = Path(video_path)
    frames_dir = Path(frames_dir)
    brand = video_path.stem.upper()
    meta = get_video_metadata(video_path)

    if verbose:
        print(f"\n{'='*60}")
        print(f"  Brand : {brand}")
        print(f"  File  : {video_path.name}  ({meta['file_size_mb']} MB)")
        print(f"  Duration: {meta['duration_seconds']}s  |  FPS: {meta['fps']}")
        print(f"  Deep models: {'ON (torch + transformers)' if _TORCH_AVAILABLE else 'OFF — torch not found, OpenCV+OCR only'}")
        print(f"{'='*60}")

    if verbose:
        print(f"\n[1/5] Extracting frames ({sample_fps} fps, max {max_frames})…")
    frame_paths = extract_frames(video_path, frames_dir, sample_fps, max_frames)
    if verbose:
        print(f"      → {len(frame_paths)} frames saved to {frames_dir}")

    if verbose:
        print(f"\n[2/5] Detecting shot boundaries…")
    boundaries, pixel_diffs = detect_shot_boundaries(frame_paths)
    if verbose:
        print(f"      → {len(boundaries)} shot cuts detected")

    if verbose:
        print(f"\n[3/5] Analysing frames…")
    rows = []
    for idx, fp in enumerate(frame_paths):
        ll = low_level_features(fp)
        if ll is None:
            continue

        pil = Image.open(fp).convert("RGB")

        # OCR + sentiment
        ocr_text = ocr_frame(pil)
        sentiment = vader_sentiment(ocr_text)

        # Optional deep models
        obj = detect_objects(pil) if _TORCH_AVAILABLE else Counter()
        caption = blip_caption(pil) if _TORCH_AVAILABLE else ""
        clip_f = clip_features(pil) if _TORCH_AVAILABLE else {}

        # Shot metadata
        is_shot_cut = idx in boundaries
        pixel_diff = pixel_diffs[idx] if idx < len(pixel_diffs) else 0.0

        rec = {
            # identity
            "video_file": video_path.name,
            "brand": brand,
            "frame_path": str(fp),
            "frame_index": idx,
            "timestamp_s": round(idx / sample_fps, 2),
            # shot
            "is_shot_cut": is_shot_cut,
            "pixel_diff": round(pixel_diff, 3),
            # low-level
            **ll,
            # OCR
            "ocr_text": ocr_text,
            "ocr_char_len": len(ocr_text),
            # sentiment
            **sentiment,
            # BLIP caption (empty if no torch)
            "blip_caption": caption,
            # DETR (zeros if no torch)
            "obj_bus": obj.get("bus", 0),
            "obj_person": obj.get("person", 0),
            "obj_truck": obj.get("truck", 0),
            "obj_car": obj.get("car", 0),
            "obj_all": json.dumps(dict(obj)),
        }
        rec.update(clip_f)
        rows.append(rec)

        if verbose and (idx % 20 == 0 or idx == len(frame_paths) - 1):
            txt_preview = ocr_text[:30].replace("\n", " ") if ocr_text else "-"
            print(f"      frame {idx:>4}/{len(frame_paths)-1} | "
                  f"brightness={ll['brightness']:5.1f} | "
                  f"ocr='{txt_preview}'")

    df = pd.DataFrame(rows)

    # Attach video-level metadata as extra columns
    for k, v in meta.items():
        df[f"meta_{k}"] = v

    if verbose:
        print(f"\n[4/5] Done. {len(df)} frame records.")
    return df


# ---------------------------------------------------------------------------
# PER-VIDEO SUMMARY AGGREGATION
# ---------------------------------------------------------------------------
def summarise_video(df: pd.DataFrame) -> dict:
    """Collapse a per-frame DataFrame into a per-video summary dict."""
    if df.empty:
        return {}
    brand = df["brand"].iloc[0]
    meta_cols = [c for c in df.columns if c.startswith("meta_")]
    meta = {c.replace("meta_", ""): df[c].iloc[0] for c in meta_cols}

    # visual averages
    vis_cols = ["brightness", "contrast", "saturation", "sharpness",
                "warm_cool_bias", "colourfulness", "edge_density",
                "visual_balance", "figure_ground_sep"]
    visual_avgs = {f"avg_{c}": round(float(df[c].mean()), 3)
                   for c in vis_cols if c in df.columns}

    # shot pacing
    shot_cuts = int(df["is_shot_cut"].sum())
    duration = meta.get("duration_seconds", 1)
    cuts_per_minute = round(shot_cuts / (duration / 60), 2) if duration > 0 else 0

    # OCR
    ocr_texts = df["ocr_text"].dropna().tolist()
    text_themes = extract_text_themes(ocr_texts)
    dominant_theme = max(text_themes, key=text_themes.get) if text_themes else "none"
    ocr_frames = int((df["ocr_char_len"] > 10).sum())
    ocr_pct = round(ocr_frames / len(df) * 100, 1) if len(df) > 0 else 0

    # VADER over all frames that have text
    vader_df = df[df["nf_compound"].notna()]
    avg_compound = round(float(vader_df["nf_compound"].mean()), 3) if not vader_df.empty else None
    sentiment_dist = (vader_df["nf_label"].value_counts(normalize=True).round(3).to_dict()
                      if not vader_df.empty else {})

    # DETR (if available)
    obj_summary = {}
    for col in ["obj_bus", "obj_person", "obj_truck", "obj_car"]:
        if col in df.columns:
            obj_summary[f"total_{col}"] = int(df[col].sum())
            obj_summary[f"pct_frames_{col}"] = round(float((df[col] > 0).mean() * 100), 1)

    # CLIP perception averages (if available)
    pxy_cols = [c for c in df.columns if c.startswith("pxy_")]
    perception_avgs = {c: round(float(df[c].mean()), 1)
                       for c in pxy_cols if df[c].notna().any()}

    # CLIP binary flag frequencies (if available)
    hl_flag_cols = [c for c in df.columns if c.endswith("_flag")]
    hl_freqs = {c: round(float(df[c].mean() * 100), 1)
                for c in hl_flag_cols if df[c].notna().any()}

    return {
        "brand": brand,
        **meta,
        "total_frames_analysed": len(df),
        "shot_cuts": shot_cuts,
        "cuts_per_minute": cuts_per_minute,
        "avg_pixel_diff": round(float(df["pixel_diff"].mean()), 3),
        **visual_avgs,
        "ocr_text_frames": ocr_frames,
        "ocr_text_pct": ocr_pct,
        "text_themes": text_themes,
        "dominant_text_theme": dominant_theme,
        "avg_vader_compound": avg_compound,
        "sentiment_distribution": sentiment_dist,
        **obj_summary,
        "perception_scores": perception_avgs,
        "hl_flag_frequencies_pct": hl_freqs,
        "deep_models_used": _TORCH_AVAILABLE,
    }


# ---------------------------------------------------------------------------
# CHART GENERATION
# ---------------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


BRAND_COLORS = {
    "EKA":      "#1a73e8",   # blue
    "OLECTRA":  "#34a853",   # green
    "SWITCH":   "#fbbc04",   # amber
    "TATA":     "#ea4335",   # red
}

def _brand_color(brand: str) -> str:
    return BRAND_COLORS.get(brand.upper(), "#888888")


def fig_brightness_timeline(df: pd.DataFrame, output_path: Path) -> None:
    """Brightness over time for a single video — shows pacing and scene transitions."""
    fig, ax = plt.subplots(figsize=(12, 4))
    color = _brand_color(df["brand"].iloc[0])
    ax.fill_between(df["timestamp_s"], df["brightness"], alpha=0.25, color=color)
    ax.plot(df["timestamp_s"], df["brightness"], color=color, linewidth=1.2)
    cuts = df[df["is_shot_cut"]]
    ax.vlines(cuts["timestamp_s"], 0, 255, colors="crimson", linewidth=0.7,
              linestyle="--", alpha=0.6, label="Shot cut")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Frame brightness (0–255)")
    ax.set_title(f"{df['brand'].iloc[0]} — Brightness Timeline + Shot Cuts")
    ax.legend(fontsize=9); ax.set_ylim(0, 255)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_visual_metrics_radar(summaries: list[dict], output_path: Path) -> None:
    """Radar / spider chart comparing key visual metrics across brands."""
    metrics = ["avg_brightness", "avg_saturation", "avg_colourfulness",
               "avg_edge_density", "avg_visual_balance"]
    labels = [m.replace("avg_", "").replace("_", " ").title() for m in metrics]
    N = len(labels)
    angles = [n / N * 2 * math.pi for n in range(N)] + [0]  # close the loop

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for s in summaries:
        brand = s.get("brand", "?")
        vals = []
        for m in metrics:
            v = s.get(m, 0)
            # Normalise to 0..1
            if "brightness" in m:   v /= 255
            elif "saturation" in m: v /= 255
            elif "colourfulness" in m: v = min(v / 80, 1.0)
            elif "edge_density" in m:  v = min(v / 0.15, 1.0)
            elif "visual_balance" in m: pass  # already 0..1
            vals.append(v)
        vals += [vals[0]]
        ax.plot(angles, vals, label=brand, color=_brand_color(brand), linewidth=2)
        ax.fill(angles, vals, alpha=0.1, color=_brand_color(brand))
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=11)
    ax.set_title("Visual Quality Radar — Brand Comparison", size=13, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_text_themes_heatmap(summaries: list[dict], output_path: Path) -> None:
    """Heatmap of keyword-theme hit counts per brand."""
    brands = [s["brand"] for s in summaries]
    themes = list(_EV_BUS_THEME_KEYWORDS.keys())
    matrix = [[s.get("text_themes", {}).get(t, 0) for t in themes] for s in summaries]
    mat = np.array(matrix, dtype=float)

    fig, ax = plt.subplots(figsize=(max(10, len(themes) * 1.2), max(4, len(brands) * 0.9)))
    im = ax.imshow(mat, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(range(len(themes)))
    ax.set_xticklabels([t.replace("_", " ").title() for t in themes], rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(brands))); ax.set_yticklabels(brands, fontsize=11)
    for i in range(len(brands)):
        for j in range(len(themes)):
            ax.text(j, i, int(mat[i, j]), ha="center", va="center", fontsize=9,
                    color="white" if mat[i, j] > mat.max() * 0.6 else "black")
    plt.colorbar(im, ax=ax, label="Keyword hit count")
    ax.set_title("On-Screen Text Themes by Brand (OCR Keyword Count)")
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_sentiment_comparison(summaries: list[dict], output_path: Path) -> None:
    """Stacked bar: positive / neutral / negative OCR-text sentiment per brand."""
    brands = [s["brand"] for s in summaries]
    pos = [s.get("sentiment_distribution", {}).get("positive", 0) for s in summaries]
    neu = [s.get("sentiment_distribution", {}).get("neutral", 0) for s in summaries]
    neg = [s.get("sentiment_distribution", {}).get("negative", 0) for s in summaries]
    no_text = [s.get("sentiment_distribution", {}).get("no_text", 0) for s in summaries]

    x = np.arange(len(brands)); w = 0.5
    fig, ax = plt.subplots(figsize=(9, 5))
    b1 = ax.bar(x, pos, w, label="Positive", color="#34a853")
    b2 = ax.bar(x, neu, w, bottom=pos, label="Neutral", color="#fbbc04")
    b3 = ax.bar(x, [n+ne for n,ne in zip(pos,neu)], w, label="Negative", color="#ea4335",
                bottom=[p+n for p,n in zip(pos,neu)])
    ax.set_xticks(x); ax.set_xticklabels(brands, fontsize=12)
    ax.set_ylabel("Share of text frames"); ax.set_ylim(0, 1.05)
    ax.set_title("OCR Text Sentiment Distribution by Brand\n(VADER on on-screen text / subtitles)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_shot_pacing(summaries: list[dict], output_path: Path) -> None:
    """Bar chart: shot cuts per minute — visual pacing / editing intensity."""
    brands = [s["brand"] for s in summaries]
    cpm = [s.get("cuts_per_minute", 0) for s in summaries]
    colors = [_brand_color(b) for b in brands]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(brands, cpm, color=colors, edgecolor="white", linewidth=0.5)
    for bar, val in zip(bars, cpm):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{val:.1f}", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylabel("Shot cuts per minute")
    ax.set_title("Editing Pacing — Shot Cuts per Minute by Brand\n"
                 "(Higher = faster, more dynamic edit | Lower = slower, more deliberate)")
    ax.set_ylim(0, max(cpm) * 1.3 + 1)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_visual_distribution_boxplots(all_frames_df: pd.DataFrame, output_path: Path) -> None:
    """Box plots of frame-level brightness, saturation, edge density grouped by brand."""
    metrics = ["brightness", "saturation", "colourfulness", "edge_density"]
    titles = ["Brightness", "Saturation", "Colourfulness", "Edge Density (Visual Complexity)"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    axes = axes.ravel()
    brands_ordered = sorted(all_frames_df["brand"].unique())
    for ax, col, title in zip(axes, metrics, titles):
        data = [all_frames_df[all_frames_df["brand"] == b][col].dropna().values
                for b in brands_ordered]
        bp = ax.boxplot(data, labels=brands_ordered, patch_artist=True, notch=False)
        for patch, brand in zip(bp["boxes"], brands_ordered):
            patch.set_facecolor(_brand_color(brand))
            patch.set_alpha(0.6)
        ax.set_title(title, fontsize=11)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Frame-Level Visual Distribution by Brand", fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def fig_ocr_wordcloud(all_frames_df: pd.DataFrame, output_dir: Path) -> None:
    """One word cloud per brand from all OCR-extracted text."""
    from wordcloud import WordCloud
    for brand, grp in all_frames_df.groupby("brand"):
        text = " ".join(grp["ocr_text"].fillna("").tolist()).lower()
        text = re.sub(r"[^a-z\s]", " ", text)
        tokens = [w for w in text.split() if len(w) > 2 and w not in _STOP_WORDS]
        if not tokens:
            continue
        wc = WordCloud(width=900, height=450, background_color="white",
                       colormap="Blues", max_words=80,
                       color_func=lambda *a, **k: _brand_color(brand)
                       ).generate(" ".join(tokens))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
        ax.set_title(f"{brand} — On-Screen Text Word Cloud", fontsize=13)
        fig.tight_layout()
        fig.savefig(str(output_dir / f"wordcloud_{brand.lower()}.png"),
                    dpi=150, bbox_inches="tight")
        plt.close(fig)


def fig_perception_radar(summaries: list[dict], output_path: Path) -> None:
    """Radar chart for CLIP perception scores — only drawn if torch was used."""
    perc_keys = list(CLIP_PERCEPTION_VIDEO.keys())
    has_data = any(s.get("perception_scores") for s in summaries)
    if not has_data:
        # Write a placeholder notice
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.text(0.5, 0.5, "CLIP perception scores not available\n"
                "(requires torch + transformers)",
                ha="center", va="center", fontsize=13, color="grey",
                transform=ax.transAxes)
        ax.axis("off")
        fig.savefig(str(output_path), dpi=120, bbox_inches="tight")
        plt.close(fig)
        return

    labels = [k.replace("pxy_", "").replace("_", " ").title() for k in perc_keys]
    N = len(labels)
    angles = [n / N * 2 * math.pi for n in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    for s in summaries:
        brand = s["brand"]
        perc = s.get("perception_scores", {})
        vals = [perc.get(k, 50) for k in perc_keys] + [perc.get(perc_keys[0], 50)]
        ax.plot(angles, vals, label=brand, color=_brand_color(brand), linewidth=2)
        ax.fill(angles, vals, alpha=0.1, color=_brand_color(brand))
    ax.set_xticks(angles[:-1]); ax.set_xticklabels(labels, size=10)
    ax.set_ylim(0, 100)
    ax.set_title("CLIP Perception Scores — Brand Comparison\n(0=low, 100=high)", size=12, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1))
    fig.tight_layout()
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate_all_charts(
    all_frames_df: pd.DataFrame,
    summaries: list[dict],
    charts_dir: Path,
    per_video_dfs: Optional[dict] = None,
) -> list[Path]:
    """
    Generate all charts and return their paths.

    Parameters
    ----------
    all_frames_df : concatenated per-frame DataFrame (all brands)
    summaries     : list of per-video summary dicts
    charts_dir    : directory to save PNGs
    per_video_dfs : dict brand → per-frame DataFrame (for per-brand charts)
    """
    charts_dir = Path(charts_dir)
    charts_dir.mkdir(parents=True, exist_ok=True)
    saved = []

    # 1. Brightness timeline per brand
    if per_video_dfs:
        for brand, df in per_video_dfs.items():
            p = charts_dir / f"brightness_timeline_{brand.lower()}.png"
            fig_brightness_timeline(df, p)
            saved.append(p)

    # 2. Visual radar
    p = charts_dir / "visual_metrics_radar.png"
    fig_visual_metrics_radar(summaries, p); saved.append(p)

    # 3. Text themes heatmap
    p = charts_dir / "text_themes_heatmap.png"
    fig_text_themes_heatmap(summaries, p); saved.append(p)

    # 4. Sentiment comparison
    p = charts_dir / "sentiment_comparison.png"
    fig_sentiment_comparison(summaries, p); saved.append(p)

    # 5. Shot pacing
    p = charts_dir / "shot_pacing.png"
    fig_shot_pacing(summaries, p); saved.append(p)

    # 6. Visual distribution boxplots
    p = charts_dir / "visual_distribution_boxplots.png"
    fig_visual_distribution_boxplots(all_frames_df, p); saved.append(p)

    # 7. Word clouds
    fig_ocr_wordcloud(all_frames_df, charts_dir)
    saved += list(charts_dir.glob("wordcloud_*.png"))

    # 8. CLIP perception radar
    p = charts_dir / "perception_radar.png"
    fig_perception_radar(summaries, p); saved.append(p)

    return sorted(set(saved))
