"""Build one tidy, anonymized table of tested beams from the two source workbooks.

Source workbooks contain student names and are not in the repo. Set
BEAM_XLSX_DIR to the folder holding them (default ~/Downloads).
"""

import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

XLSX_DIR = Path(os.environ.get("BEAM_XLSX_DIR", Path.home() / "Downloads"))
VOSS = XLSX_DIR / "VOSS ONLY Beam data (Voss_McDowell_Advanced Engineering) Bayesian Optimization with GP.xlsx"
FALL = XLSX_DIR / "Beam data fall 26 (6).xlsx"

COLS = [
    "source", "shape", "B", "h", "H", "b", "fillet", "width", "height",
    "infill", "wall_loops", "top_layers", "bottom_layers", "layer_height",
    "mass_g", "force_N", "censored", "replicate_group",
]


def _num(s):
    return pd.to_numeric(pd.Series(s).astype(str).str.extract(r"([\d.]+)")[0], errors="coerce").values


def _infill_frac(s):
    x = pd.to_numeric(pd.Series(s), errors="coerce")
    return np.where(x > 1, x / 100, x)


def _parse_print_text(t):
    t = "" if pd.isna(t) else str(t).lower()
    wall = (re.search(r"(\d+)\s*(?:side\s*)?wall", t) or re.search(r"wall layers to be (\d+)", t)
            or re.search(r"(\d+) on the sides", t))
    top = re.search(r"(\d+)\s*(?:top|roof)", t) or re.search(r"(\d+) layers of wall loops on top", t)
    bot = re.search(r"(\d+)\s*(?:bottom|floor)", t) or re.search(r"(\d+) on the bottom", t)
    both = (re.search(r"(\d+)\s*(?:top\s*(?:and|/|to)\s*bottom|floor and roof)", t)
            or re.search(r"top and bottom layers (\d+)", t))
    top_n = int(top.group(1)) if top else None
    bot_n = int(bot.group(1)) if bot else None
    if both:
        top_n = bot_n = int(both.group(1))
    elif top and not bot and re.search(r"top and (\d+) bottom", t):
        bot_n = int(re.search(r"top and (\d+) bottom", t).group(1))
    return (int(wall.group(1)) if wall else None), top_n, bot_n


def _fall_sheet(sheet):
    d = pd.read_excel(FALL, sheet, header=None)
    i = d.index[d.apply(lambda r: r.astype(str).str.contains("Teams").any(), axis=1)][0]
    d.columns = [str(c) for c in d.iloc[i]]
    d = d.iloc[i + 1 :]
    col = lambda key: next(c for c in d.columns if c.startswith(key))
    d = d[pd.to_numeric(d[col("Force")], errors="coerce").notna() & d[col("Teams")].notna()]
    return d, col


def load_fall_ibeams():
    out = []
    for sheet, rnd in [("Copy of Ibeams round 1 fall", 1), ("I beams round 2", 2), ("risk pop quiz beams", 3)]:
        d, col = _fall_sheet(sheet)
        fail = d[col("Failure")].astype(str).str.lower()
        parsed = d[col("Other")].map(_parse_print_text)
        fillet = d[col("Fillet")] if any(c.startswith("Fillet") for c in d.columns) else np.nan
        out.append(pd.DataFrame({
            "source": f"fall26_ibeam_r{rnd}",
            "shape": "I-beam",
            "B": _num(d[col("Flange Width")]),
            "h": _num(d[col("Flange Height")]),
            "H": _num(d[col("Web Height")]),
            "b": _num(d[col("Web Thickness")]),
            "fillet": _num(fillet) if not np.isscalar(fillet) else np.nan,
            "infill": _infill_frac(d[col("Infill")]),
            "wall_loops": [p[0] for p in parsed],
            "top_layers": [p[1] for p in parsed],
            "bottom_layers": [p[2] for p in parsed],
            "mass_g": pd.to_numeric(d[col("Weight")]).values,
            "force_N": pd.to_numeric(d[col("Force")]).values,
            "censored": fail.str.contains("did not fail|didnt fail").values,
        }))
    df = pd.concat(out, ignore_index=True).dropna(subset=["B", "h", "H", "b"])
    df["width"] = df["B"]
    df["height"] = df["H"] + 2 * df["h"]
    return df


def load_fall_rects():
    out = []
    for sheet, rnd in [("fall 26 round 1", 1), ("fall 26 round 2", 2)]:
        d, col = _fall_sheet(sheet)
        parsed = d[col("Other")].map(_parse_print_text)
        out.append(pd.DataFrame({
            "source": f"fall26_rect_r{rnd}",
            "shape": "rectangle",
            "width": _num(d[col("width")]),
            "height": _num(d[col("Height")]),
            "infill": _infill_frac(d[col("Infill")]),
            "wall_loops": [p[0] for p in parsed],
            "top_layers": [p[1] for p in parsed],
            "bottom_layers": [p[2] for p in parsed],
            "mass_g": pd.to_numeric(d[col("Weight")]).values,
            "force_N": pd.to_numeric(d[col("Force")]).values,
            "censored": False,
        }))
    return pd.concat(out, ignore_index=True)


def load_voss_ibeams():
    d = pd.read_excel(VOSS, "USE THIS TAB", header=None).iloc[1:, :10]
    d.columns = ["id", "H", "h", "B", "b", "fillet", "material", "strw", "mass_g", "force_N"]
    # Row 1 header cells were overwritten in the workbook; restore from the archive tab.
    d.iloc[0, 1:4] = [19.447, 2.776, 8.454]
    for c in ["H", "h", "B", "b", "fillet", "mass_g", "force_N"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return pd.DataFrame({
        "source": "voss_ibeam", "shape": "I-beam",
        "B": d["B"].astype(float), "h": d["h"].astype(float), "H": d["H"].astype(float),
        "b": d["b"].astype(float), "fillet": d["fillet"].astype(float),
        "width": d["B"].astype(float), "height": (d["H"] + 2 * d["h"]).astype(float),
        "infill": np.nan,
        "mass_g": d["mass_g"].astype(float).values, "force_N": d["force_N"].astype(float).values,
        "censored": False,
    })


def load_voss_rects():
    d = pd.read_excel(VOSS, "with original Bambu PLA + noise")
    d = d[d["Mass (g)"].notna() & d["peak force N"].notna()].copy()
    d = d[~d["Unnamed: 0"].astype(str).str.contains("avg|repeat")]
    lab = d["Unnamed: 0"].astype(str).str.replace(r"\s+(H2D|X1)$", "", regex=True)
    fill_cols = ["Height(mm)", "Width(mm)", "Wall Loops", "Layer Height(mm)", "Top Layers",
                 "Bottom Layers ", "Infill percent", "Material"]
    d[fill_cols] = d.groupby(lab)[fill_cols].ffill()
    d[fill_cols] = d[fill_cols].fillna(d.groupby(lab.values)[fill_cols].transform("first"))
    d["Height(mm)"] = d["Height(mm)"].fillna(22.0)
    d["Width(mm)"] = d["Width(mm)"].fillna(14.7)
    rep = lab.where(lab.map(lab.value_counts()) > 1)
    return pd.DataFrame({
        "source": "voss_rect", "shape": "rectangle",
        "width": d["Width(mm)"].values, "height": d["Height(mm)"].values,
        "infill": d["Infill percent"].values / 100,
        "wall_loops": d["Wall Loops"].values, "top_layers": d["Top Layers"].values,
        "bottom_layers": d["Bottom Layers "].values, "layer_height": d["Layer Height(mm)"].values,
        "mass_g": d["Mass (g)"].values, "force_N": d["peak force N"].values,
        "censored": False, "replicate_group": rep.values,
        "material": d["Material"].values,
    })


def load_all():
    df = pd.concat([load_voss_ibeams(), load_voss_rects(), load_fall_ibeams(), load_fall_rects()],
                   ignore_index=True)
    df["strw"] = df["force_N"] / df["mass_g"]
    return df


if __name__ == "__main__":
    df = load_all()
    pd.set_option("display.width", 250)
    print(df.drop(columns=["censored"]).round(3).to_string())
    df.to_csv(Path(__file__).with_name("beams_tidy.csv"), index=False)
