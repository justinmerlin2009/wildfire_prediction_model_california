#!/usr/bin/env python3
"""
PRISM State-Level Monthly Summary Precomputation Script.

One-time batch process that reads CONUS monthly PRISM rasters and computes
per-state zonal statistics for all 48 CONUS states + DC.

Output: outputs/cache/prism/prism_state_monthly_summaries.parquet (~50 MB)
        outputs/cache/prism/prism_ca_monthly_stats.parquet (~1 MB)

Estimated runtime: ~2-3 hours (external USB drive I/O bound).
Memory: peaks ~250 MB.

Usage:
    conda run -n wildfire python scripts/prism_precompute_state_summaries.py

    # Resume from a specific variable if interrupted:
    conda run -n wildfire python scripts/prism_precompute_state_summaries.py --resume-from vpdmax

    # Only compute CA stats (fast):
    conda run -n wildfire python scripts/prism_precompute_state_summaries.py --ca-only
"""
import argparse
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.constants import (
    PRISM_VARIABLES, PRISM_MONTHLY_START_YEAR, PRISM_MONTHLY_END_YEAR,
    PRISM_CACHE_DIR, PRISM_CA_BOUNDS,
)
from src.utils.prism_data_loader import (
    check_prism_drive, discover_files, load_us_states_boundaries,
    precompute_state_monthly_summaries, load_monthly_stats_ca,
    save_to_cache,
)


def compute_ca_monthly_stats(variables, year_range, output_path):
    """
    Compute California-only monthly spatial statistics for all variables.

    Saves incrementally after each variable to avoid losing progress on crash.
    Skips variables that already exist in partial output file.
    """
    import pandas as pd

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check for existing partial results
    existing_df = None
    completed_vars = set()
    if output_path.exists() and output_path.stat().st_size > 0:
        try:
            existing_df = pd.read_csv(output_path)
            completed_vars = set(existing_df["variable"].unique())
            print(f"  Found existing results for: {sorted(completed_vars)}")
        except Exception:
            existing_df = None

    all_dfs = [existing_df] if existing_df is not None else []

    for var in variables:
        if var in completed_vars:
            print(f"\n  Skipping {var} (already computed)")
            continue

        print(f"\nComputing CA monthly stats for {var}...")
        t0 = time.time()
        df = load_monthly_stats_ca(var, year_range[0], year_range[1])
        df["variable"] = var
        all_dfs.append(df)
        elapsed = time.time() - t0
        print(f"  {len(df)} rows in {elapsed:.0f}s")

        # Save incrementally after each variable (atomic write via temp file)
        combined = pd.concat(all_dfs, ignore_index=True)
        tmp_path = output_path.with_suffix(".csv.tmp")
        combined.to_csv(tmp_path, index=False)
        tmp_path.rename(output_path)
        print(f"  Saved checkpoint ({len(combined):,} rows)")

    combined = pd.concat(all_dfs, ignore_index=True)
    tmp_path = output_path.with_suffix(".csv.tmp")
    combined.to_csv(tmp_path, index=False)
    tmp_path.rename(output_path)
    print(f"\nSaved CA stats: {len(combined):,} rows to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.0f} KB")
    return combined


def main():
    parser = argparse.ArgumentParser(
        description="Precompute PRISM state-level monthly summaries"
    )
    parser.add_argument(
        "--ca-only", action="store_true",
        help="Only compute California monthly stats (fast, ~10 min)"
    )
    parser.add_argument(
        "--resume-from", type=str, default=None,
        help="Resume state stats from this variable (e.g., 'vpdmax')"
    )
    parser.add_argument(
        "--year-start", type=int, default=PRISM_MONTHLY_START_YEAR,
        help=f"Start year (default: {PRISM_MONTHLY_START_YEAR})"
    )
    parser.add_argument(
        "--year-end", type=int, default=PRISM_MONTHLY_END_YEAR,
        help=f"End year (default: {PRISM_MONTHLY_END_YEAR})"
    )
    args = parser.parse_args()

    year_range = (args.year_start, args.year_end)

    # Verify drive
    print("=" * 70)
    print("PRISM State-Level Monthly Summary Precomputation")
    print("=" * 70)

    try:
        drive_info = check_prism_drive()
        print(f"Drive: {drive_info['base_path']}")
        print(f"Variables: {drive_info['n_variables']}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # ── CA monthly stats (always run, fast) ───────────────────────────
    ca_output = PRISM_CACHE_DIR / "prism_ca_monthly_stats.csv"
    print(f"\n{'─' * 70}")
    print("Phase 1: California Monthly Spatial Stats")
    print(f"{'─' * 70}")
    print(f"Year range: {year_range[0]}–{year_range[1]}")
    print(f"Variables: {PRISM_VARIABLES}")

    t_start = time.time()
    compute_ca_monthly_stats(PRISM_VARIABLES, year_range, ca_output)
    t_ca = time.time() - t_start
    print(f"CA stats completed in {t_ca / 60:.1f} minutes")

    if args.ca_only:
        print("\n--ca-only flag set, skipping state-level computation.")
        print("Done!")
        return

    # ── CONUS state-level stats (slow, ~2-3 hours) ────────────────────
    print(f"\n{'─' * 70}")
    print("Phase 2: CONUS State-Level Monthly Statistics")
    print(f"{'─' * 70}")

    # Download/load state boundaries
    states_gdf = load_us_states_boundaries()
    print(f"Loaded {len(states_gdf)} CONUS state boundaries")

    # Handle resume
    variables = list(PRISM_VARIABLES)
    if args.resume_from:
        if args.resume_from in variables:
            idx = variables.index(args.resume_from)
            variables = variables[idx:]
            print(f"Resuming from {args.resume_from} ({len(variables)} variables remaining)")
        else:
            print(f"Warning: {args.resume_from} not in {PRISM_VARIABLES}, starting from beginning")

    state_output = PRISM_CACHE_DIR / "prism_state_monthly_summaries.parquet"

    print(f"Variables: {variables}")
    print(f"Year range: {year_range[0]}–{year_range[1]}")
    print(f"Output: {state_output}")
    print(f"\nEstimated runtime: ~{len(variables) * 20}-{len(variables) * 30} minutes")
    print("Starting in 3 seconds...")
    time.sleep(3)

    t_start = time.time()
    df = precompute_state_monthly_summaries(
        variables=variables,
        year_range=year_range,
        states_gdf=states_gdf,
        output_path=state_output,
    )
    t_states = time.time() - t_start

    print(f"\n{'=' * 70}")
    print(f"COMPLETE")
    print(f"{'=' * 70}")
    print(f"State stats: {len(df):,} rows, {t_states / 3600:.1f} hours")
    print(f"Output: {state_output}")
    print(f"File size: {state_output.stat().st_size / (1024**2):.1f} MB")


if __name__ == "__main__":
    main()
