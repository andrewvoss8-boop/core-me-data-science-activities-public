"""
Visualize GP recommendations from the 13-beam subset in (b,H) and (Pltb_m, Pbend_m) space.

Background shading: ground-truth GP (b_dH_Pltb_Pbend, Matern, all 34 beams, alpha=3e-5).
Contours shown in BOTH spaces (mapped via the physics transforms).

Two training parameterizations:
  - b_H       : raw design variables
  - Pltb_Pbend: normalized LTB + bending strength per mass

Each trained on the 13-beam even-spaced subset, Matern, alpha=1e-4.

Acquisition values shown:
  - EI (no kappa)
  - UCB kappa = 1, 2, 3

Output: viz_gp_recs_n13.png
"""

import pathlib
import warnings

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern

warnings.filterwarnings("ignore")

REPO = pathlib.Path(__file__).resolve().parents[1]
SUBSET_CSV = REPO / "data" / "lhs16_subset_bH_even_n13.csv"
FULL_CSV = REPO / "data" / "I_beam_data_2var.csv"

# ── physics ──────────────────────────────────────────────────────────
TOTAL_HEIGHT = 25.0; B_FIXED = 16.0; LENGTH_M = 0.2023
SIGMA_Y = 81.8e6; E_MOD = 2.74e9; G_MOD = E_MOD / 2.6
C1 = 1.35; DENSITY = 1210; Y_MAX = TOTAL_HEIGHT / 2e3

def _beta(t, a):
    if a <= 0 or t <= 0: return 1/3
    r = min(t,a)/max(t,a); return (1/3)*(1 - 0.63*r + 0.052*r**5)

def calc_Ix(H,b): 
    H_m,b_m,B_m=H/1e3,b/1e3,B_FIXED/1e3; h=(TOTAL_HEIGHT/1e3-H_m)/2
    if h<=0: return 0
    return (b_m*H_m**3)/12+2*(B_m*h**3/12+B_m*h*((H_m+h)/2)**2)
def calc_Iy(H,b):
    H_m,b_m,B_m=H/1e3,b/1e3,B_FIXED/1e3; h=(TOTAL_HEIGHT/1e3-H_m)/2
    if h<=0: return 0
    return (H_m*b_m**3)/12+2*(h*B_m**3)/12
def calc_J(H,b):
    H_m,b_m,B_m=H/1e3,b/1e3,B_FIXED/1e3; h=(TOTAL_HEIGHT/1e3-H_m)/2
    if h<=0: return 0
    J_web=_beta(b_m,H_m)*H_m*b_m**3; J_fl=_beta(h,B_m)*B_m*h**3
    return J_web+2*J_fl
def calc_mass(H,b):
    H_m,b_m,B_m=H/1e3,b/1e3,B_FIXED/1e3; h=(TOTAL_HEIGHT/1e3-H_m)/2
    if h<=0: return 0
    return DENSITY*LENGTH_M*(H_m*b_m+2*h*B_m)*1000
def calc_P_bend(H,b):
    return 4*SIGMA_Y*calc_Ix(H,b)/Y_MAX/LENGTH_M
def calc_P_ltb(H,b):
    Iy,J=calc_Iy(H,b),calc_J(H,b)
    if Iy<=0 or J<=0: return 0
    return 4*(C1*np.pi/LENGTH_M)*np.sqrt(E_MOD*Iy*G_MOD*J)/LENGTH_M
def find_H_opt(b):
    def obj(H):
        h=(TOTAL_HEIGHT-H)/2
        if h<0 or h>6.5: return 1e10
        m=calc_mass(H,b); return -calc_P_bend(H,b)/m if m>0 else 1e10
    return minimize_scalar(obj, bounds=(12,23.4), method='bounded').x

def pltb_m(b,H): m=calc_mass(H,b); return calc_P_ltb(H,b)/m if m>0 else 0
def pbend_m(b,H): m=calc_mass(H,b); return calc_P_bend(H,b)/m if m>0 else 0
def dH_feat(b,H): return H-find_H_opt(b)

def to_bH(b,H):   return np.column_stack([b,H])
def to_PP(b,H):   return np.column_stack([[pltb_m(bi,Hi) for bi,Hi in zip(b,H)],
                                           [pbend_m(bi,Hi) for bi,Hi in zip(b,H)]])
def to_bdHPP(b,H):
    n=len(b); X=np.zeros((n,4))
    for i in range(n):
        X[i]=[b[i],dH_feat(b[i],H[i]),pltb_m(b[i],H[i]),pbend_m(b[i],H[i])]
    return X

# ── GP helpers ────────────────────────────────────────────────────────
def normalize(X, bounds):
    X_n=np.copy(X).astype(float)
    for i,k in enumerate(bounds):
        lo,hi=bounds[k]; X_n[:,i]=(X[:,i]-lo)/(hi-lo)
    return X_n

def _bounds_from_data(X, names, margin=0.15):
    bds={}
    for i,nm in enumerate(names):
        lo,hi=X[:,i].min(),X[:,i].max()
        span=max(hi-lo,abs(lo)*0.1+1e-6)
        bds[nm]=(lo-margin*span,hi+margin*span)
    return bds

def train_gp(X, y, bounds, alpha=1e-4):
    X_n=normalize(X,bounds); y_log=np.log(y)
    ym=y_log.mean(); yc=y_log-ym
    nd=X.shape[1]
    k=ConstantKernel(1.)*Matern(length_scale=[0.5]*nd,
                                 length_scale_bounds=(0.15,3.),nu=2.5)
    gp=GaussianProcessRegressor(kernel=k,n_restarts_optimizer=15,alpha=alpha,normalize_y=False)
    gp.fit(X_n,yc)
    return gp,ym

def predict_at(gp, ym, bounds, X_raw):
    X_n=normalize(X_raw,bounds)
    mu,sig=gp.predict(X_n,return_std=True)
    return np.exp(mu+ym), sig

def ei_acq(mu,sig,best_yc):
    Z=np.where(sig>1e-9,(mu-best_yc)/sig,0.)
    return np.where(sig>1e-9,(mu-best_yc)*norm.cdf(Z)+sig*norm.pdf(Z),0.)

def recommend(gp, yc, ym, bounds, transform_fn, b_lo=1., acq='ei', kappa=2., n=8000, seed=0):
    np.random.seed(seed)
    b_c=np.random.uniform(b_lo,8.,n); H_c=np.random.uniform(12.,23.,n)
    X_c=transform_fn(b_c,H_c); X_n=normalize(X_c,bounds)
    mu,sig=gp.predict(X_n,return_std=True)
    if acq=='ei':
        score=ei_acq(mu,sig,yc.max())
    else:
        score=mu+kappa*sig
    idx=np.argmax(score)
    return b_c[idx], H_c[idx]

# ── ground truth ──────────────────────────────────────────────────────
STRONG = 31.75

def build_gt(b_all,H_all,y_all):
    X=to_bdHPP(b_all,H_all)
    bds=_bounds_from_data(X,['b','dH','Pltb_m','Pbend_m']); bds['b']=(1.,8.)
    gp,ym=train_gp(X,y_all,bds,alpha=3e-5)
    return gp,bds,ym

def gt_predict_bH_grid(gp_gt,bds_gt,ym_gt,b_grid_2d,H_grid_2d):
    """Predict GT Str/w on a 2D grid of (b,H) values."""
    b_flat=b_grid_2d.ravel(); H_flat=H_grid_2d.ravel()
    X=to_bdHPP(b_flat,H_flat)
    mu,_=predict_at(gp_gt,ym_gt,bds_gt,X)
    return mu.reshape(b_grid_2d.shape)

def gt_predict_PP_grid(gp_gt,bds_gt,ym_gt,Pl_grid_2d,Pb_grid_2d,res=60):
    """
    Predict GT Str/w on a 2D grid of (Pltb_m, Pbend_m) values.
    For each grid point, invert to (b,H) numerically.
    Expensive: we use a coarse lookup instead -- build the GT surface
    on a fine (b,H) grid and then scatter-interpolate into PP space.
    """
    from scipy.interpolate import griddata
    b_s=np.linspace(1,8,res); H_s=np.linspace(12,23,res)
    BG,HG=np.meshgrid(b_s,H_s)
    gt_bH=gt_predict_bH_grid(gp_gt,bds_gt,ym_gt,BG,HG)
    # compute PP coords for every (b,H) sample
    b_f,H_f=BG.ravel(),HG.ravel()
    Pl_f=np.array([pltb_m(bi,Hi) for bi,Hi in zip(b_f,H_f)])
    Pb_f=np.array([pbend_m(bi,Hi) for bi,Hi in zip(b_f,H_f)])
    gt_f=gt_bH.ravel()
    # interpolate onto requested grid
    pts=np.column_stack([Pl_f,Pb_f])
    xi=np.column_stack([Pl_grid_2d.ravel(),Pb_grid_2d.ravel()])
    interp=griddata(pts,gt_f,xi,method='linear')
    return interp.reshape(Pl_grid_2d.shape)

# ── main ──────────────────────────────────────────────────────────────
def main():
    df_sub=pd.read_csv(SUBSET_CSV); df_full=pd.read_csv(FULL_CSV)
    b_sub=df_sub['b_web_mm'].values.astype(float)
    H_sub=df_sub['H_web_mm'].values.astype(float)
    y_sub=df_sub['Str/w N/g'].values.astype(float)
    b_all=df_full['b_web_mm'].values.astype(float)
    H_all=df_full['H_web_mm'].values.astype(float)
    y_all=df_full['Str/w N/g'].values.astype(float)

    print("Building GT GP (all 34 beams)...")
    gp_gt,bds_gt,ym_gt=build_gt(b_all,H_all,y_all)

    # compute PP coords for training beams
    Pl_sub=np.array([pltb_m(bi,Hi) for bi,Hi in zip(b_sub,H_sub)])
    Pb_sub=np.array([pbend_m(bi,Hi) for bi,Hi in zip(b_sub,H_sub)])
    Pl_all=np.array([pltb_m(bi,Hi) for bi,Hi in zip(b_all,H_all)])
    Pb_all=np.array([pbend_m(bi,Hi) for bi,Hi in zip(b_all,H_all)])

    # ── build GT background grids ──────────────────────────────────────
    res=80
    b_vec=np.linspace(1,8,res); H_vec=np.linspace(12,23,res)
    BG,HG=np.meshgrid(b_vec,H_vec)
    print("Computing GT surface on (b,H) grid...")
    gt_bH=gt_predict_bH_grid(gp_gt,bds_gt,ym_gt,BG,HG)

    # PP space grid -- cover data range with margin
    pl_lo,pl_hi=Pl_all.min()*.85,Pl_all.max()*1.1
    pb_lo,pb_hi=Pb_all.min()*.85,Pb_all.max()*1.1
    Pl_vec=np.linspace(pl_lo,pl_hi,res); Pb_vec=np.linspace(pb_lo,pb_hi,res)
    PLG,PBG=np.meshgrid(Pl_vec,Pb_vec)
    print("Computing GT surface on (Pltb_m, Pbend_m) grid...")
    gt_PP=gt_predict_PP_grid(gp_gt,bds_gt,ym_gt,PLG,PBG)

    # ── train student GPs on 13-beam subset ───────────────────────────
    ALPHA=1e-4
    bds_bH={'b':(1.,8.),'H':(12.,23.)}
    X_PP_tr=to_PP(b_sub,H_sub)
    bds_PP=_bounds_from_data(X_PP_tr,['Pltb_m','Pbend_m'])
    gp_bH, ym_bH=train_gp(to_bH(b_sub,H_sub),y_sub,bds_bH,alpha=ALPHA)
    gp_PP, ym_PP=train_gp(X_PP_tr,             y_sub,bds_PP,alpha=ALPHA)
    yc_bH=np.log(y_sub)-ym_bH
    yc_PP=np.log(y_sub)-ym_PP
    print("Student GPs trained.")

    # ── get recommendations ────────────────────────────────────────────
    acqs=[('EI','ei',None),
          ('UCB κ=1','ucb',1.),
          ('UCB κ=2','ucb',2.),
          ('UCB κ=3','ucb',3.)]

    recs={}
    for label,atype,kap in acqs:
        b_bH,H_bH=recommend(gp_bH,yc_bH,ym_bH,bds_bH,to_bH,
                              acq=atype,kappa=kap if kap else 2.)
        b_PP,H_PP=recommend(gp_PP,yc_PP,ym_PP,bds_PP,to_PP,
                              acq=atype,kappa=kap if kap else 2.)
        recs[label]={
            'bH':(b_bH,H_bH),
            'PP':(b_PP,H_PP),
            'PP_feat':(pltb_m(b_PP,H_PP),pbend_m(b_PP,H_PP)),
            'bH_as_PP':(pltb_m(b_bH,H_bH),pbend_m(b_bH,H_bH)),
        }
        print(f"{label:12s}  (b,H): ({b_bH:.2f}, {H_bH:.2f})   PP-param: ({b_PP:.2f}, {H_PP:.2f})")

    # ── plot ──────────────────────────────────────────────────────────
    colors=['#e41a1c','#ff7f00','#4daf4a','#984ea3']  # EI, UCB1, UCB2, UCB3
    markers_bH=['o','^','s','D']
    markers_PP=['o','^','s','D']

    vmin,vmax=20.,33.
    cmap='viridis'
    levels=np.linspace(vmin,vmax,30)

    fig,axes=plt.subplots(1,2,figsize=(14,5.5))
    fig.suptitle('GP recommendations (13-beam training, Matern, α=1e-4)\n'
                 'Background: ground-truth GP (all 34 beams)', fontsize=12)

    # ── LEFT: (b, H) space ────────────────────────────────────────────
    ax=axes[0]
    cf=ax.contourf(BG,HG,gt_bH,levels=levels,cmap=cmap,vmin=vmin,vmax=vmax)
    ax.contour(BG,HG,gt_bH,levels=[STRONG],colors='white',linewidths=1.5,linestyles='--')
    ax.text(1.3,12.4,f'GT = {STRONG} N/g',color='white',fontsize=8)
    plt.colorbar(cf,ax=ax,label='GT Str/w (N/g)')

    # training data
    ax.scatter(b_sub,H_sub,c=y_sub,cmap=cmap,vmin=vmin,vmax=vmax,
               s=80,edgecolors='k',linewidths=1.2,zorder=5,label='13-beam training')

    # all full-data points (faint outline)
    ax.scatter(b_all,H_all,s=25,facecolors='none',edgecolors='white',
               linewidths=0.6,alpha=0.5,zorder=4,label='all 34 beams')

    for (label,_,_),col,mk in zip(acqs,colors,markers_bH):
        b_r,H_r=recs[label]['bH']
        ax.scatter(b_r,H_r,color=col,marker=mk,s=160,edgecolors='k',
                   linewidths=1.2,zorder=10,label=f'{label} rec (b,H param)')

    ax.set_xlabel('b (mm)'); ax.set_ylabel('H (mm)')
    ax.set_title('(b, H) space')
    ax.legend(fontsize=7,loc='upper right')

    # ── RIGHT: (Pltb_m, Pbend_m) space ───────────────────────────────
    ax=axes[1]
    cf2=ax.contourf(PLG,PBG,gt_PP,levels=levels,cmap=cmap,vmin=vmin,vmax=vmax)
    ax.contour(PLG,PBG,gt_PP,levels=[STRONG],colors='white',linewidths=1.5,linestyles='--')
    ax.text(PLG.min()+0.01*(PLG.max()-PLG.min()),
            PBG.min()+0.02*(PBG.max()-PBG.min()),
            f'GT = {STRONG} N/g',color='white',fontsize=8)
    plt.colorbar(cf2,ax=ax,label='GT Str/w (N/g)')

    ax.scatter(Pl_sub,Pb_sub,c=y_sub,cmap=cmap,vmin=vmin,vmax=vmax,
               s=80,edgecolors='k',linewidths=1.2,zorder=5,label='13-beam training')
    ax.scatter(Pl_all,Pb_all,s=25,facecolors='none',edgecolors='white',
               linewidths=0.6,alpha=0.5,zorder=4,label='all 34 beams')

    for (label,_,_),col,mk in zip(acqs,colors,markers_PP):
        # PP-parameterized recommendation
        pl_r,pb_r=recs[label]['PP_feat']
        ax.scatter(pl_r,pb_r,color=col,marker=mk,s=160,edgecolors='k',
                   linewidths=1.2,zorder=10,label=f'{label} (PP param)')
        # bH-parameterized recommendation mapped into PP space
        pl_bH,pb_bH=recs[label]['bH_as_PP']
        ax.scatter(pl_bH,pb_bH,color=col,marker=mk,s=80,
                   edgecolors='k',linewidths=1.,zorder=9,alpha=0.5,
                   label=f'{label} (b,H param, mapped)')

    ax.set_xlabel('P_ltb / mass (N/g)'); ax.set_ylabel('P_bend / mass (N/g)')
    ax.set_title('(Pltb_m, Pbend_m) space')
    ax.legend(fontsize=6,loc='upper left')

    plt.tight_layout()
    out=REPO/'me323'/'viz_gp_recs_n13.png'
    plt.savefig(out,dpi=150,bbox_inches='tight')
    print(f'\nSaved: {out}')

    # ── text summary ──────────────────────────────────────────────────
    print(f'\n{"Acq":12s}  {"(b,H) param":>22s}  {"PP param":>20s}  {"same region?"}')
    print('-'*75)
    for label,_,_ in acqs:
        b_bH,H_bH=recs[label]['bH']
        b_PP,H_PP=recs[label]['PP']
        gt_bH_val,_=predict_at(gp_gt,ym_gt,bds_gt,to_bdHPP(np.array([b_bH]),np.array([H_bH])))
        gt_PP_val,_=predict_at(gp_gt,ym_gt,bds_gt,to_bdHPP(np.array([b_PP]),np.array([H_PP])))
        print(f"{label:12s}  b={b_bH:.2f} H={H_bH:.2f} GT={gt_bH_val[0]:.1f}  "
              f"b={b_PP:.2f} H={H_PP:.2f} GT={gt_PP_val[0]:.1f}  "
              f"{'STRONG' if gt_bH_val[0]>=STRONG and gt_PP_val[0]>=STRONG else 'partial' if max(gt_bH_val[0],gt_PP_val[0])>=STRONG else 'MISS'}")


if __name__=='__main__':
    main()
