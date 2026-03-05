"""
Orbit Propagation Analysis Script
Author: Giuliano Pennacchio
Description: This script processes GMAT output data to compare Two-Body, 
             J2-only, and High-Fidelity propagation models for a LEO satellite.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Configuration & Path Setup ---
DATA_DIR = '../data/'
RESULTS_DIR = '../results/'

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

# --- Data Loading ---
# Using sep='\s+' to handle GMAT's fixed-width space-separated format
# --- Data Loading ---
try:
    # Adding 'r' prefix (raw string) to fix the SyntaxWarning for regex
    df_2b = pd.read_csv(os.path.join(DATA_DIR, 'prop_twobody.csv'), sep=r'\s+')
    df_j2 = pd.read_csv(os.path.join(DATA_DIR, 'prop_j2.csv'), sep=r'\s+')
    df_hf = pd.read_csv(os.path.join(DATA_DIR, 'prop_highfid.csv'), sep=r'\s+')
    print("[-] Data loaded successfully.")
except Exception as e:
    print(f"[!] Error loading data: {e}")
    exit()

# Cleanup column names (removing potential whitespaces from GMAT headers)
for df in [df_2b, df_j2, df_hf]:
    df.columns = df.columns.str.strip()

# Calculate relative time in days (assuming MJ2000 or A1ModJulian)
time_days = df_hf['Sat.A1ModJulian'] - df_hf['Sat.A1ModJulian'].iloc[0]

# --- 1. Position Divergence (3D Position Error) ---
def get_3d_error(df_test, df_ref):
    """Calculates the Euclidean distance between two position vectors."""
    return np.sqrt((df_test['Sat.X'] - df_ref['Sat.X'])**2 + 
                   (df_test['Sat.Y'] - df_ref['Sat.Y'])**2 + 
                   (df_test['Sat.Z'] - df_ref['Sat.Z'])**2)

error_2b_vs_hf = get_3d_error(df_2b, df_hf)
error_j2_vs_hf = get_3d_error(df_j2, df_hf)

plt.figure(figsize=(10, 6))
plt.plot(time_days, error_2b_vs_hf, label='Two-Body vs High-Fid', color='tab:red', linestyle='--', alpha=0.8)
plt.plot(time_days, error_j2_vs_hf, label='J2-only vs High-Fid', color='tab:blue', linewidth=2)
plt.yscale('log')
plt.title('Propagator Divergence: 3D Position Error (30 Days)', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('Position Error [km]', fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.4)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'position_error_log.png'), dpi=300)

# --- 2. Orbital Decay (Semi-Major Axis) ---
plt.figure(figsize=(10, 6))
plt.plot(time_days, df_hf['Sat.SMA'], label='High-Fid (Drag Included)', color='tab:green', linewidth=2)
plt.plot(time_days, df_2b['Sat.SMA'], label='Two-Body (No Drag)', color='tab:gray', linestyle=':')
plt.title('Orbit Decay: Semi-Major Axis (SMA) Evolution', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('SMA [km]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'sma_decay.png'), dpi=300)

# --- 3. RAAN Precession (J2 Effect) ---
plt.figure(figsize=(10, 6))
plt.plot(time_days, df_hf['Sat.RAAN'], label='High-Fid Precession', color='tab:purple', linewidth=2)
plt.plot(time_days, df_2b['Sat.RAAN'], label='Two-Body (Fixed Plane)', color='tab:gray', linestyle=':')
plt.title('Nodal Precession: RAAN Drift over Time', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('RAAN [deg]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'raan_drift.png'), dpi=300)

# --- 4. Inclination Stability (Third-Body Effects) ---
plt.figure(figsize=(10, 6))
plt.plot(time_days, df_hf['Sat.INC'], label='High-Fid (Sun/Moon/J2)', color='tab:orange', linewidth=2)
plt.axhline(y=98.22, color='tab:gray', linestyle=':', label='Initial Inclination')
plt.title('Inclination Stability & Perturbations', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('Inclination [deg]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'inclination_stability.png'), dpi=300)

plt.show()
print(f"[-] Analysis completed. Plots saved in {RESULTS_DIR}")