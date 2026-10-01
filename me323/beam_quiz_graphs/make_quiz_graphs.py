"""Quiz figures: trends in tested 3D-printed beams (I-beams and rectangles).

Run: python3 make_quiz_graphs.py   (writes fig*.png next to this file)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from load_beams import load_all

OUT = Path(__file__).parent
plt.rcParams.update({
    "font.size": 13, "axes.titlesize": 14, "axes.labelsize": 13,
    "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False,
})
C_IB, C_RECT = "#1f77b4", "#d95f02"
STRW = "Strength-to-weight (N/g)"
FORCE = "Breaking force (N)"

df = load_all()
df.loc[df["source"].eq("voss_rect") & df["material"].isna(), "material"] = "SunLu PLA+ 2.0"


def jitter(x, amt, seed=0):
    return x + np.random.default_rng(seed).uniform(-amt, amt, len(x))


def panel_letters(axes):
    for ax, L in zip(np.ravel(axes), "ABCDEFGH"):
        t = ax.get_title()
        ax.set_title("")
        ax.set_title(f"({L}) {t}", loc="left")


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight")
    plt.close(fig)


# Fig 1: rectangles, fixed 22 x 14.7 mm, one material, only print settings change
r = df[(df.source == "voss_rect") & (df.material.str.startswith("SunLu"))]
r = pd.concat([r[r.replicate_group.isna()], r[r.replicate_group.notna()].groupby("replicate_group").head(1)])
fig, axes = plt.subplots(2, 4, figsize=(16, 7.5), sharey="row")
xs = [("infill", 100, "Infill (%)", 0), ("wall_loops", 1, "Wall loops", 0.12),
      ("top_layers", 1, "Top/bottom layers", 0.12), ("layer_height", 1, "Layer height (mm)", 0)]
for j, (col, scale, lab, jit) in enumerate(xs):
    x = jitter(r[col].values * scale, jit, j)
    for i, y in enumerate(["force_N", "strw"]):
        axes[i, j].scatter(x, r[y], s=55, c=C_RECT, edgecolor="k", lw=0.5)
        axes[i, j].set_xlabel(lab)
        axes[i, j].set_title({"force_N": "Strength", "strw": "Strength-to-weight"}[y])
axes[0, 0].set_ylabel(FORCE)
axes[1, 0].set_ylabel(STRW)
panel_letters(axes)
fig.suptitle("Rectangular beams, all 22 mm tall x 14.7 mm wide, same filament: only print settings changed",
             y=1.0, fontsize=15)
fig.tight_layout()
save(fig, "fig1_rectangle_print_settings.png")


# Fig 2: I-beams, total height fixed at 25 mm (so H = 25 - 2h), same filament
ib = df[df.source == "voss_ibeam"]
fig, axes = plt.subplots(1, 4, figsize=(16, 4.3), sharey=True)
for ax, (col, lab) in zip(axes, [("b", "Web thickness b (mm)"), ("B", "Flange width B (mm)"),
                                 ("h", "Flange thickness h (mm)"), ("fillet", "Fillet radius (mm)")]):
    ax.scatter(ib[col], ib.strw, s=50, c=C_IB, edgecolor="k", lw=0.5)
    ax.set_xlabel(lab)
    ax.set_title("")
axes[0].set_ylabel(STRW)
panel_letters(axes)
fig.suptitle("I-beams, all 25 mm tall in total (web height H = 25 - 2h), same filament", y=1.03, fontsize=15)
fig.tight_layout()
save(fig, "fig2_ibeam_dimensions.png")


# Fig 3: force vs mass for every beam, with constant strength-to-weight guide lines
fig, ax = plt.subplots(figsize=(8.5, 6.5))
m = np.linspace(0, 100, 50)
for k in [10, 20, 30, 40]:
    ax.plot(m, k * m, color="gray", lw=1, ls="--", zorder=0)
    ax.text(min(98, 2900 / k), k * min(98, 2900 / k), f" {k} N/g", color="gray", va="bottom", ha="right")
for shape, c, mk in [("I-beam", C_IB, "o"), ("rectangle", C_RECT, "s")]:
    s = df[(df["shape"] == shape) & ~df.censored]
    ax.scatter(s.mass_g, s.force_N, s=45, c=c, marker=mk, edgecolor="k", lw=0.5, label=shape.capitalize())
cz = df[df.censored]
ax.scatter(cz.mass_g, cz.force_N, s=60, facecolor="none", edgecolor=C_IB, lw=1.8, label="Did not break (true strength is higher)")
ax.set(xlim=(0, 100), ylim=(0, 3000), xlabel="Mass (g)", ylabel=FORCE,
       title="Every beam tested: strength vs. mass")
ax.legend(loc="lower right")
save(fig, "fig3_force_vs_mass.png")


# Fig 4: student rectangles (mixed widths and heights)
fr = df[df.source.str.startswith("fall26_rect")]
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
tall = fr.height >= 30
for ax, (col, scale, lab) in zip(axes, [("infill", 100, "Infill (%)"), ("height", 1, "Height (mm)"),
                                        ("width", 1, "Width (mm)")]):
    for mask, mk, lb in [(tall, "s", "30-31 mm tall"), (~tall, "^", "23-29.5 mm tall")]:
        ax.scatter(fr[col][mask] * scale, fr.strw[mask], s=60, marker=mk, c=C_RECT, edgecolor="k", lw=0.5,
                   alpha=1 if mk == "s" else 0.55, label=lb)
    ax.set_xlabel(lab)
axes[0].set_ylabel(STRW)
axes[0].legend(loc="upper right", fontsize=11)
panel_letters(axes)
fig.suptitle("Class rectangular beams: width, height, and infill all changed at once", y=1.03, fontsize=15)
fig.tight_layout()
save(fig, "fig4_class_rectangles.png")


# Fig 5: repeatability, identical designs printed and tested more than once
groups = []
for g, lab in [("A", "Rectangle\n2 walls, 100%"), ("B", "Rectangle\n2 walls, 25%"),
               ("EI \\#1", "Rectangle\n5 walls, 20%"), ("EI \\#2", "Rectangle\n5 walls, 5%")]:
    groups.append((lab, df[df.replicate_group == g].strw.values, C_RECT))
dims = ["H", "h", "B", "b", "fillet"]
key = ib[dims].round(2).astype(str).agg("|".join, axis=1)
rep = key.value_counts()
groups.append(("I-beam\n(Voss)", ib[key == rep.index[0]].strw.values, C_IB))
fib = df[df.source.str.startswith("fall26_ibeam")]
groups.append(("I-beam\n(class)", fib[(fib.B == 17) & (fib.H == 24)].strw.values, C_IB))
fig, ax = plt.subplots(figsize=(10, 5))
for i, (lab, v, c) in enumerate(groups):
    ax.scatter(jitter(np.full(len(v), i), 0.08, i), v, s=60, c=c, edgecolor="k", lw=0.5)
    ax.text(i, v.max() + 0.6, f"n={len(v)}", ha="center", fontsize=11)
ax.set_xticks(range(len(groups)), [g[0] for g in groups])
ax.set_ylabel(STRW)
ax.set_ylim(10, 40)
ax.set_title("Same design, printed and broken more than once")
save(fig, "fig5_repeatability.png")


# Fig 6: class I-beams by round (later rounds changed many things at once)
fig, axes = plt.subplots(1, 4, figsize=(16, 4.3), sharey=True)
mk = {1: "o", 2: "s", 3: "D"}
for ax, (col, scale, lab) in zip(axes, [("b", 1, "Web thickness b (mm)"), ("height", 1, "Total height (mm)"),
                                        ("top_layers", 1, "Top/bottom layers"), ("infill", 100, "Infill (%)")]):
    for rnd, shade in [(1, 0.35), (2, 0.65), (3, 1.0)]:
        s = fib[fib.source.str.endswith(f"r{rnd}") & ~fib.censored]
        ax.scatter(s[col] * scale, s.strw, s=55, marker=mk[rnd], c=[plt.cm.Blues(shade)], edgecolor="k",
                   lw=0.5, label=f"Round {rnd}")
    s = fib[fib.censored]
    ax.scatter(s[col] * scale, s.strw, s=70, marker="D", facecolor="white", edgecolor="k", lw=1.5,
               label="Round 3, did not break")
    ax.set_xlabel(lab)
axes[0].set_ylabel(STRW)
h_, l_ = axes[0].get_legend_handles_labels()
fig.legend(h_, l_, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.1), fontsize=12)
panel_letters(axes)
fig.suptitle("Class I-beams across three rounds of redesign (blank top-layer entries were not reported)",
             y=1.03, fontsize=15)
fig.tight_layout()
save(fig, "fig6_class_ibeams_by_round.png")

print("Groups in fig 5:", [(g[0].replace("\n", " "), np.round(g[1], 1).tolist()) for g in groups])
