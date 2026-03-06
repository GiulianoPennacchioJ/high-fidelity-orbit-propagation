"""
Orbit Propagation Analysis Script
Author: Giuliano Pennacchio
Description: Processes GMAT output data to compare Two-Body, J2-only, 
             and High-Fidelity propagation models after full state reset.
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

def load_and_clean_data(filename):
    """Loads GMAT fixed-width files using regex separator for compatibility."""
    path = os.path.join(DATA_DIR, filename)
    # Using raw string regex for whitespace and python engine to avoid warnings
    df = pd.read_csv(path, sep=r'\s+', engine='python')
    # Strip whitespaces from column headers
    df.columns = [c.strip() for c in df.columns]
    return df

# --- Data Loading ---
try:
    df_2b = load_and_clean_data('prop_twobody.csv')
    df_j2 = load_and_clean_data('prop_j2.csv')
    df_hf = load_and_clean_data('prop_highfid.csv')
    print("[-] Data synchronized and loaded successfully.")
except Exception as e:
    print(f"[!] Error loading data: {e}")
    exit()

# --- 1. Data Synchronization ---
# Trim dataframes to the same length to allow direct vector subtraction
min_len = min(len(df_2b), len(df_j2), len(df_hf))
df_2b = df_2b.iloc[:min_len].reset_index(drop=True)
df_j2 = df_j2.iloc[:min_len].reset_index(drop=True)
df_hf = df_hf.iloc[:min_len].reset_index(drop=True)

# Define time axis in days
time_days = df_hf['Sat.A1ModJulian'] - df_hf['Sat.A1ModJulian'].iloc[0]

# --- 2. Propagator Divergence (Position Error Calculation) ---
def get_3d_position_error(df_test, df_ref):
    """Calculates Euclidean distance between synchronized position vectors."""
    dx = df_test['Sat.X'] - df_ref['Sat.X']
    dy = df_test['Sat.Y'] - df_ref['Sat.Y']
    dz = df_test['Sat.Z'] - df_ref['Sat.Z']
    # Adding 1e-9 to allow log-scale plotting of zero/near-zero values
    return np.sqrt(dx**2 + dy**2 + dz**2) + 1e-9

error_2b_vs_hf = get_3d_position_error(df_2b, df_hf)
error_j2_vs_hf = get_3d_position_error(df_j2, df_hf)

plt.figure(figsize=(10, 6))
plt.plot(time_days, error_2b_vs_hf, label='Two-Body vs High-Fid', color='tab:red', linestyle='--', alpha=0.7)
plt.plot(time_days, error_j2_vs_hf, label='J2-only vs High-Fid', color='tab:blue', linewidth=2)
plt.yscale('log')
plt.title('Propagator Divergence: 3D Position Error (30 Days)', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('Position Error [km]', fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'position_error_divergence.png'), dpi=300)

# --- 3. Orbit Decay (SMA Secular Trend) ---
# Rolling mean over 1 orbital period (~95 rows for 60s step) to filter J2 oscillations
df_hf['SMA_Mean'] = df_hf['Sat.SMA'].rolling(window=95, center=True).mean()

plt.figure(figsize=(10, 6))
plt.plot(time_days, df_hf['Sat.SMA'], color='tab:green', alpha=0.2, label='Osculating SMA (High-Fid)')
plt.plot(time_days, df_hf['SMA_Mean'], color='darkgreen', linewidth=2, label='Mean SMA (Atmospheric Drag Effect)')
plt.axhline(y=df_2b['Sat.SMA'].iloc[0], color='tab:gray', linestyle=':', label='Two-Body (Baseline)')
plt.title('Orbit Decay: Semi-Major Axis (SMA) Evolution', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('SMA [km]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'sma_secular_decay.png'), dpi=300)

# --- 4. Nodal Precession (RAAN Drift) ---
plt.figure(figsize=(10, 6))
plt.plot(time_days, df_hf['Sat.RAAN'], label='High-Fidelity (J2 Precession)', color='tab:purple', linewidth=2)
plt.plot(time_days, df_2b['Sat.RAAN'], label='Two-Body (Fixed Plane)', color='tab:gray', linestyle=':')
plt.title('Nodal Precession: RAAN Drift over Time', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('RAAN [deg]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'raan_drift.png'), dpi=300)

# --- 5. Inclination Stability ---
plt.figure(figsize=(10, 6))
plt.plot(time_days, df_hf['Sat.INC'], label='High-Fidelity (Third-Body Perturbations)', color='tab:orange', linewidth=1.5)
plt.axhline(y=98.22, color='tab:gray', linestyle=':', label='Target Inclination')
plt.title('Inclination Stability: Third-Body & J2 Effects', fontsize=14)
plt.xlabel('Time [Days]', fontsize=12)
plt.ylabel('Inclination [deg]', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'inclination_stability.png'), dpi=300)

plt.show()
print(f"[-] Analysis completed. Results saved in {RESULTS_DIR}")