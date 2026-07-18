"""Phase 2 · consolidated image-analytics library (end-to-end).

Everything the notebook uses lives here so the notebook stays thin and the
same code is unit-testable from the CLI. Covers:

  LOW-LEVEL  : brightness, saturation, contrast, sharpness, warm/cool hue,
               dominant colours, colourfulness, edge density, symmetry,
               rule-of-thirds, visual balance, figure-ground separation
  HIGH-LEVEL : BLIP caption, DETR object detection (bus/person/truck counts),
               CLIP zero-shot for charger/depot, accessibility, motion,
               fleet-scale, govt-handover, urban/natural, showcase-vs-operational,
               and technology/comfort/trust/sustainability themes
  TEXT       : Tesseract OCR + VADER narrative-framing sentiment
  PERCEPTION : CLIP zero-shot proxy for the 7 perception dimensions
               (+ a blank human-coder template is exported by the notebook)

Models are lazy-loaded and cached so importing this module is cheap.
"""
from __future__ import annotations
import json, math, warnings
from collections import Counter
from functools import lru_cache
from pathlib import Path

import numpy as np
import cv2
from PIL import Image
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# --------------------------------------------------------------------------- #
#  LOW-LEVEL FEATURES  (pure OpenCV / NumPy — no model downloads)
# --------------------------------------------------------------------------- #
def warm_cool_bias(rgb: np.ndarray) -> float:
    r, g, b = rgb[..., 0].mean(), rgb[..., 1].mean(), rgb[..., 2].mean()
    warm = (r + 0.5 * g) / 255.0
    cool = (b + 0.5 * g) / 255.0
    if warm + cool == 0:
        return 0.0
    return round((warm - cool) / (warm + cool), 3)


def colourfulness(rgb: np.ndarray) -> float:
    """Hasler & Süsstrunk (2003) metric of perceived colourfulness."""
    R = rgb[..., 0].astype("float"); G = rgb[..., 1].astype("float"); B = rgb[..., 2].astype("float")
    rg = R - G
    yb = 0.5 * (R + G) - B
    std_root = math.sqrt(rg.std() ** 2 + yb.std() ** 2)
    mean_root = math.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    return round(std_root + 0.3 * mean_root, 2)


def edge_density(gray: np.ndarray) -> float:
    """Fraction of pixels that are Canny edges — visual busyness / complexity."""
    edges = cv2.Canny(gray, 100, 200)
    return round(float((edges > 0).mean()), 4)


def symmetry(gray: np.ndarray) -> tuple[float, float]:
    """(horizontal, vertical) symmetry in [0,1]; 1 = perfectly mirror-symmetric."""
    h, w = gray.shape
    w2 = w // 2
    left = gray[:, :w2].astype("float")
    right = cv2.flip(gray[:, w - w2:], 1).astype("float")
    hs = 1.0 - np.abs(left - right).mean() / 255.0
    h2 = h // 2
    top = gray[:h2, :].astype("float")
    bot = cv2.flip(gray[h - h2:, :], 0).astype("float")
    vs = 1.0 - np.abs(top - bot).mean() / 255.0
    return round(float(hs), 3), round(float(vs), 3)


def _gradient_energy(gray: np.ndarray) -> np.ndarray:
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    return np.hypot(gx, gy)


def rule_of_thirds(gray: np.ndarray) -> float:
    """Share of gradient energy concentrated near the 4 rule-of-thirds points."""
    energy = _gradient_energy(gray)
    s = energy.sum() + 1e-9
    energy = energy / s
    h, w = gray.shape
    pts = [(h / 3, w / 3), (h / 3, 2 * w / 3), (2 * h / 3, w / 3), (2 * h / 3, 2 * w / 3)]
    sigma = min(h, w) / 6.0
    yy, xx = np.mgrid[0:h, 0:w]
    mask = np.zeros((h, w))
    for py, px in pts:
        mask = np.maximum(mask, np.exp(-((yy - py) ** 2 + (xx - px) ** 2) / (2 * sigma ** 2)))
    return round(float((energy * mask).sum()), 4)


def visual_balance(gray: np.ndarray) -> float:
    """Mean of left/right and top/bottom gradient-energy balance in [0,1]."""
    energy = _gradient_energy(gray) + 1e-9
    h, w = gray.shape
    left = energy[:, : w // 2].sum(); right = energy[:, w - w // 2:].sum()
    top = energy[: h // 2, :].sum(); bot = energy[h - h // 2:, :].sum()
    hbal = 1.0 - abs(left - right) / (left + right)
    vbal = 1.0 - abs(top - bot) / (top + bot)
    return round(float((hbal + vbal) / 2), 3)


def figure_ground(gray: np.ndarray) -> float:
    """Proxy for subject/background separation: share of gradient detail in the
    central 50% crop vs the border. ~0.5 = evenly detailed, →1 = strong centred subject."""
    energy = _gradient_energy(gray)
    h, w = gray.shape
    cy0, cy1 = int(h * 0.25), int(h * 0.75)
    cx0, cx1 = int(w * 0.25), int(w * 0.75)
    center = energy[cy0:cy1, cx0:cx1].mean()
    border_mask = np.ones((h, w), bool); border_mask[cy0:cy1, cx0:cx1] = False
    border = energy[border_mask].mean()
    return round(float(center / (center + border + 1e-9)), 3)


def dominant_colours(bgr: np.ndarray, k: int = 3, sample: int = 15000):
    img = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).reshape(-1, 3)
    if img.shape[0] > sample:
        rng = np.random.default_rng(42)
        img = img[rng.choice(img.shape[0], sample, replace=False)]
    km = KMeans(n_clusters=k, n_init=4, random_state=42).fit(img)
    counts = Counter(km.labels_.tolist())
    total = sum(counts.values())
    centers = km.cluster_centers_.astype(int)
    return [(tuple(int(v) for v in centers[i]), round(c / total, 3)) for i, c in counts.most_common()]


def classify_palette(top_rgb) -> str:
    r, g, b = top_rgb
    if max(r, g, b) < 40:      return "dark/black"
    if min(r, g, b) > 220:     return "white"
    if r > g and r > b and r - b > 40:  return "warm (red/orange)"
    if b > r and b > g and b - r > 40:  return "cool (blue)"
    if g > r and g > b:        return "green"
    if abs(r - g) < 20 and abs(g - b) < 20:  return "neutral/gray"
    return "mixed"


def low_level_features(path: Path) -> dict | None:
    bgr = cv2.imread(str(path))
    if bgr is None:
        return None
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    hsym, vsym = symmetry(gray)
    dc = dominant_colours(bgr, k=3)
    return {
        "width": w, "height": h,
        "aspect_ratio": round(w / h, 3),
        "file_size_kb": round(path.stat().st_size / 1024, 1),
        "brightness": round(float(gray.mean()), 2),
        "contrast": round(float(gray.std()), 2),
        "saturation": round(float(hsv[..., 1].mean()), 2),
        "sharpness": round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2),
        "warm_cool_bias": warm_cool_bias(rgb),
        "colourfulness": colourfulness(rgb),
        "edge_density": edge_density(gray),
        "symmetry_h": hsym, "symmetry_v": vsym,
        "rule_of_thirds": rule_of_thirds(gray),
        "visual_balance": visual_balance(gray),
        "figure_ground_sep": figure_ground(gray),
        "top_color_rgb": list(dc[0][0]),
        "top_color_share": dc[0][1],
        "palette_family": classify_palette(dc[0][0]),
        "dominant_colors": json.dumps(dc),
    }


# --------------------------------------------------------------------------- #
#  MODELS  (lazy, cached)
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _device():
    import torch
    return "cuda" if torch.cuda.is_available() else "cpu"


@lru_cache(maxsize=1)
def _blip():
    from transformers import BlipProcessor, BlipForConditionalGeneration
    proc = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    return proc, model.to(_device()).eval()


@lru_cache(maxsize=1)
def _detr():
    from transformers import DetrImageProcessor, DetrForObjectDetection
    proc = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
    return proc, model.to(_device()).eval()


@lru_cache(maxsize=1)
def _clip():
    from transformers import CLIPProcessor, CLIPModel
    proc = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    return proc, model.to(_device()).eval()


def blip_caption(pil: Image.Image) -> str:
    import torch
    proc, model = _blip()
    inputs = proc(pil, return_tensors="pt").to(_device())
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=40)
    return proc.decode(out[0], skip_special_tokens=True)


# COCO classes we care about for the EV-bus brief
_DETR_KEEP = {"bus", "person", "truck", "car", "train", "traffic light", "bicycle", "motorcycle"}


def detect_objects(pil: Image.Image, threshold: float = 0.7) -> Counter:
    import torch
    proc, model = _detr()
    inputs = proc(images=pil, return_tensors="pt").to(_device())
    with torch.no_grad():
        out = model(**inputs)
    sizes = torch.tensor([pil.size[::-1]])
    res = proc.post_process_object_detection(out, target_sizes=sizes, threshold=threshold)[0]
    labels = [model.config.id2label[int(l)] for l in res["labels"]]
    return Counter(l for l in labels if l in _DETR_KEEP)


# ---- CLIP zero-shot prompt groups ---------------------------------------- #
# Each group is (positive_prompt, negative_prompt); we report P(positive).
CLIP_BINARY = {
    "hl_charger_depot":    ("an electric bus at a charging station or bus depot",
                             "a bus with no charging station or depot visible"),
    "hl_accessibility":    ("a low-floor bus with a wheelchair ramp or accessible entrance",
                             "a bus with no visible wheelchair ramp or accessibility feature"),
    "hl_bus_in_motion":    ("a bus driving in motion on a road",
                             "a parked stationary bus that is not moving"),
    "hl_fleet_scale":      ("a large fleet of many buses lined up together",
                             "a single bus on its own"),
    "hl_govt_handover":    ("a government official ceremony or launch event handing over buses",
                             "an ordinary bus photo with no ceremony or officials"),
    "hl_operational_proof":("a real-world photograph of a bus operating in daily service",
                             "a polished studio product render or marketing mock-up of a bus"),
}
# multi-class group -> argmax label
CLIP_SETTING = ["an urban city street setting", "a natural outdoor landscape setting",
                "an indoor studio or showroom setting", "a document infographic or text graphic"]
# theme presence (positive/negative pairs)
CLIP_THEMES = {
    "theme_technology":    ("an image emphasising advanced technology and innovation",
                             "an image with no emphasis on technology"),
    "theme_comfort":       ("a comfortable spacious modern bus interior",
                             "an image not about comfort"),
    "theme_trust":         ("a professional trustworthy reliable brand image",
                             "an amateur unreliable looking image"),
    "theme_sustainability":("a green sustainable eco-friendly clean-energy image",
                             "an image with no sustainability or green theme"),
}
# perception proxy dimensions (positive/negative pairs) -> 0..100
CLIP_PERCEPTION = {
    "pxy_trust":           ("a trustworthy and reliable bus", "an untrustworthy unreliable bus"),
    "pxy_modernity":       ("a modern futuristic bus", "an old outdated bus"),
    "pxy_comfort":         ("a comfortable spacious bus", "an uncomfortable cramped bus"),
    "pxy_accessibility":   ("an accessible bus for elderly and disabled passengers",
                             "an inaccessible bus that is hard to board"),
    "pxy_env_friendliness":("a clean environmentally friendly electric bus",
                             "a polluting dirty diesel bus"),
    "pxy_operational_readiness":("a bus in real operational service ready to deploy at scale",
                             "a concept prototype bus not yet in service"),
    "pxy_visual_appeal":   ("a visually appealing attractive professional image",
                             "a dull unappealing low quality image"),
}


def _as_embed(x):
    """transformers 5.x returns an output object from get_*_features; the
    projected embedding lives in pooler_output. Older versions return a tensor."""
    import torch
    if torch.is_tensor(x):
        return x
    return x.pooler_output


@lru_cache(maxsize=1)
def _clip_text_bank():
    """Encode every prompt once (shared across all images)."""
    import torch
    proc, model = _clip()
    prompts, slices = [], {}
    i = 0
    for name, (pos, neg) in {**CLIP_BINARY, **CLIP_THEMES, **CLIP_PERCEPTION}.items():
        slices[name] = ("pair", i); prompts += [pos, neg]; i += 2
    slices["_setting"] = ("multi", i); prompts += CLIP_SETTING; i += len(CLIP_SETTING)
    with torch.no_grad():
        tok = proc(text=prompts, return_tensors="pt", padding=True).to(_device())
        tf = _as_embed(model.get_text_features(**tok))
        tf = tf / tf.norm(dim=-1, keepdim=True)
    return tf, slices, float(model.logit_scale.exp())


def clip_features(pil: Image.Image) -> dict:
    import torch
    proc, model = _clip()
    tf, slices, scale = _clip_text_bank()
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
                out[name] = round(p * 100, 1)          # perception 0..100
            else:
                out[name] = round(p, 3)                 # probability
                out[name + "_flag"] = bool(p >= 0.5)
    # setting argmax
    kind, i = slices["_setting"]
    seg = torch.softmax(sims[i:i + len(CLIP_SETTING)], dim=0)
    labels = ["urban", "natural", "indoor_studio", "infographic_text"]
    out["hl_setting"] = labels[int(seg.argmax())]
    out["hl_setting_conf"] = round(float(seg.max()), 3)
    return out


def ocr_text(pil: Image.Image) -> str:
    import pytesseract
    return pytesseract.image_to_string(pil.convert("RGB")).strip()


# --------------------------------------------------------------------------- #
#  ORCHESTRATION  (shared by the CLI runner and the notebook)
# --------------------------------------------------------------------------- #
import pandas as pd  # noqa: E402


def iter_images(images_dir: Path):
    return sorted(p for p in Path(images_dir).iterdir() if p.suffix.lower() in IMAGE_EXTS)


def build_dataframe(images_dir: Path, verbose: bool = True) -> pd.DataFrame:
    """Run every per-image stage (low-level + BLIP + DETR + CLIP + OCR)."""
    images_dir = Path(images_dir)
    root = images_dir.parent
    rows = []
    paths = iter_images(images_dir)
    for i, p in enumerate(paths, 1):
        ll = low_level_features(p)
        if ll is None:
            if verbose:
                print(f"  skip unreadable: {p.name}")
            continue
        pil = Image.open(p).convert("RGB")
        obj = detect_objects(pil)
        clip = clip_features(pil)
        rec = {"image_id": p.stem, "file_path": str(p.relative_to(root))}
        rec.update(ll)
        rec["blip_caption"] = blip_caption(pil)
        rec["ocr_text"] = ocr_text(pil)
        rec["obj_bus_count"] = obj.get("bus", 0)
        rec["obj_person_count"] = obj.get("person", 0)
        rec["obj_truck_count"] = obj.get("truck", 0)
        rec["obj_all"] = json.dumps(dict(obj))
        rec.update(clip)
        # derived high-level flags combining DETR + CLIP
        rec["hl_bus_visible"] = bool(obj.get("bus", 0) > 0 or clip.get("hl_fleet_scale", 0) >= 0.5)
        rec["hl_passenger_driver_visible"] = bool(obj.get("person", 0) > 0)
        rec["hl_fleet_scale_deploy"] = bool(obj.get("bus", 0) >= 3 or clip.get("hl_fleet_scale", 0) >= 0.6)
        rows.append(rec)
        if verbose:
            print(f"  [{i:>2}/{len(paths)}] {p.stem[:8]}  bus={rec['obj_bus_count']} "
                  f"person={rec['obj_person_count']} setting={rec['hl_setting']:16s} "
                  f"| {rec['blip_caption'][:42]}")
    return pd.DataFrame(rows)


def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """VADER narrative-framing sentiment on OCR text (proxy for framing, not
    consumer perception)."""
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    vader = SentimentIntensityAnalyzer()
    df = df.copy()
    df["ocr_char_len"] = df["ocr_text"].fillna("").str.len()

    def score(t):
        if not isinstance(t, str) or not t.strip():
            return dict(nf_neg=None, nf_neu=None, nf_pos=None, nf_compound=None, nf_label="no_text")
        s = vader.polarity_scores(t)
        lbl = "positive" if s["compound"] >= 0.05 else ("negative" if s["compound"] <= -0.05 else "neutral")
        return dict(nf_neg=s["neg"], nf_neu=s["neu"], nf_pos=s["pos"], nf_compound=s["compound"], nf_label=lbl)

    nf = pd.DataFrame([score(t) for t in df["ocr_text"]])
    return pd.concat([df.reset_index(drop=True), nf], axis=1)


import re as _re  # noqa: E402
_STOP = {"the","and","for","with","from","you","are","this","that","they","their","has","have","been",
         "not","but","all","any","was","were","its","can","will","more","than","into","who","how",
         "what","why","when"}


def _clean(t):
    if not isinstance(t, str):
        return ""
    t = _re.sub(r"[^A-Za-z\s]", " ", t.lower())
    t = _re.sub(r"\s+", " ", t).strip()
    return " ".join(w for w in t.split() if len(w) > 2 and w not in _STOP)


def lda_topics(df: pd.DataFrame, n_topics: int = 3, n_words: int = 10):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    corpus = [c for c in df["ocr_text"].apply(_clean) if c]
    if len(corpus) < 4:
        return []
    vec = CountVectorizer(max_df=0.9, min_df=1, stop_words="english")
    X = vec.fit_transform(corpus)
    k = min(n_topics, len(corpus))
    lda = LatentDirichletAllocation(n_components=k, random_state=42, learning_method="batch").fit(X)
    vocab = np.array(vec.get_feature_names_out())
    return [(t, list(vocab[np.argsort(comp)[::-1][:n_words]])) for t, comp in enumerate(lda.components_)]


PERCEPTION_DIMS = ["trust", "modernity", "comfort", "accessibility",
                   "env_friendliness", "operational_readiness", "visual_appeal"]


def perception_template(df: pd.DataFrame) -> pd.DataFrame:
    """Blank per-image sheet for human / independent coders to fill (1-7 Likert)."""
    cols = {"image_id": df["image_id"], "file_path": df["file_path"],
            "blip_caption": df["blip_caption"]}
    for d in PERCEPTION_DIMS:
        cols[f"coder_{d}"] = ""            # to be filled 1..7 by human coders
    cols["coder_notes"] = ""
    return pd.DataFrame(cols)


def _spearman(a, b):
    from scipy.stats import spearmanr
    m = a.notna() & b.notna()
    if m.sum() < 5:
        return None, None, int(m.sum())
    rho, p = spearmanr(a[m], b[m])
    return round(float(rho), 3), round(float(p), 4), int(m.sum())


def _group_diff(df, flag_col, score_col):
    """Mean score for flag=True vs flag=False."""
    d = df[[flag_col, score_col]].dropna()
    if d[flag_col].nunique() < 2:
        return None
    g = d.groupby(flag_col)[score_col].agg(["mean", "count"])
    hi = g.loc[True] if True in g.index else None
    lo = g.loc[False] if False in g.index else None
    if hi is None or lo is None:
        return None
    return dict(mean_true=round(float(hi["mean"]), 1), n_true=int(hi["count"]),
                mean_false=round(float(lo["mean"]), 1), n_false=int(lo["count"]),
                delta=round(float(hi["mean"] - lo["mean"]), 1))


def hypothesis_tests(df: pd.DataFrame, perception_prefix: str = "pxy_") -> list:
    """Answer the five spec hypotheses using whichever perception columns exist
    (CLIP proxy by default, or human coder_* columns if present & filled)."""
    P = perception_prefix
    tests = []

    # 1. Does real-operation imagery increase trust?
    tests.append({
        "id": "H1", "question": "Does real-operation imagery increase trust?",
        "test": "trust for operational-proof images vs product-showcase images",
        "result": _group_diff(df.assign(_op=df["hl_operational_proof_flag"]),
                               "_op", f"{P}trust"),
        "reads": f"positive delta => operational imagery scores higher {P}trust",
    })
    # 2. Do bright interiors improve comfort perception?
    rho, p, n = _spearman(df["brightness"], df[f"{P}comfort"])
    tests.append({
        "id": "H2", "question": "Do bright interiors improve comfort perception?",
        "test": "Spearman brightness vs comfort",
        "result": {"rho": rho, "p": p, "n": n},
        "reads": "positive rho => brighter images perceived as more comfortable",
    })
    # 3. Does charging visibility improve technology/modernity perception?
    tests.append({
        "id": "H3", "question": "Does charging visibility improve technology perception?",
        "test": "modernity for charger/depot-visible vs not",
        "result": _group_diff(df.assign(_c=df["hl_charger_depot_flag"]),
                              "_c", f"{P}modernity"),
        "reads": "positive delta => charger visibility raises modernity/technology read",
    })
    # 4. Do passengers make images more relatable (visual appeal)?
    df4 = df.assign(_ppl=df["obj_person_count"] > 0)
    tests.append({
        "id": "H4", "question": "Do passengers make images more relatable?",
        "test": "visual appeal for person-present vs person-absent",
        "result": _group_diff(df4, "_ppl", f"{P}visual_appeal"),
        "reads": "positive delta => images with people score higher appeal/relatability",
    })
    # 5. Does accessibility visibility improve inclusiveness (accessibility perception)?
    tests.append({
        "id": "H5", "question": "Does accessibility visibility improve brand inclusiveness?",
        "test": "accessibility perception for ramp/low-floor-visible vs not",
        "result": _group_diff(df.assign(_a=df["hl_accessibility_flag"]),
                              "_a", f"{P}accessibility"),
        "reads": "positive delta => visible accessibility raises inclusiveness read",
    })
    return tests
