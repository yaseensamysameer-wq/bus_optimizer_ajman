import subprocess
import sys
from pathlib import Path


# ============================================================
# BUS OPTIMIZER AJMAN
# FULL PIPELINE
# ============================================================


# ------------------------------------------------------------
# 1. PROJECT FOLDER
# ------------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent


# ------------------------------------------------------------
# 2. FOLDERS
# ------------------------------------------------------------

DATA_DIR = PROJECT_DIR / "data"
NOTEBOOK_DIR = PROJECT_DIR / "notebooks"
OUTPUT_DIR = PROJECT_DIR / "outputs"


# Create folders if they don't exist
DATA_DIR.mkdir(exist_ok=True)
NOTEBOOK_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# 3. FILES
# ------------------------------------------------------------

# Simulation
SIMULATION = PROJECT_DIR / "bus_optimizer_ajmanv0_1.py"

# Simulation input
PASSENGERS = DATA_DIR / "passengers.csv"

# Simulation output
BUSLOGS = DATA_DIR / "passengers.csv"

# Notebooks
ANALYSIS = NOTEBOOK_DIR / "bus_optimizer_ajmanv0.2.ipynb"
ML_PREDICTION = NOTEBOOK_DIR / "bus_optimizer_ajmanv0.3.ipynb"
OPTIMIZATION = NOTEBOOK_DIR / "bus_optimizer_ajmanv0.4.ipynb"


# ------------------------------------------------------------
# 4. RUN A STAGE
# ------------------------------------------------------------

def run_stage(command, stage_name):

    print("\n")
    print("=" * 70)
    print(f"STARTING: {stage_name}")
    print("=" * 70)

    try:

        result = subprocess.run(
            command,
            cwd=PROJECT_DIR,
            text=True,
            capture_output=True
        )

        # Print normal output
        if result.stdout:
            print(result.stdout)

        # Check for an error
        if result.returncode != 0:

            print("\n")
            print("=" * 70)
            print(f"❌ {stage_name} FAILED")
            print("=" * 70)

            print("\nERROR:\n")

            if result.stderr:
                print(result.stderr)
            else:
                print("No error message was returned.")

            print("\nPIPELINE STOPPED.")

            sys.exit(result.returncode)

        print(f"✅ {stage_name} completed successfully.")

    except Exception as error:

        print("\n")
        print("=" * 70)
        print(f"❌ {stage_name} FAILED")
        print("=" * 70)

        print("\nERROR:\n")
        print(error)

        print("\nPIPELINE STOPPED.")

        sys.exit(1)


# ============================================================
# STAGE 1 — SIMULATION
# ============================================================

# Make sure passengers.csv exists before starting

if not PASSENGERS.exists():

    print("\n❌ ERROR")
    print("The simulation input file could not be found:")
    print(PASSENGERS)
    print("\nPipeline stopped.")

    sys.exit(1)


run_stage(
    [
        sys.executable,
        str(SIMULATION)
    ],
    "1/4 - Simulation"
)


# ------------------------------------------------------------
# Check that simulation actually created buslogs.csv
# ------------------------------------------------------------

if not BUSLOGS.exists():

    print("\n")
    print("=" * 70)
    print("❌ SIMULATION FAILED")
    print("=" * 70)

    print("\nThe simulation finished running, but it did not create:")

    print(BUSLOGS)

    print("\nThe next stages cannot run without the buslogs dataset.")

    print("\nPIPELINE STOPPED.")

    sys.exit(1)


print(f"\n✅ Buslogs dataset found:")
print(BUSLOGS)


# ============================================================
# STAGE 2 — ANALYSIS
# ============================================================

run_stage(
    [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(ANALYSIS),
        "--output",
        str(OUTPUT_DIR / "analysis_executed.ipynb")
    ],
    "2/4 - Data Analysis"
)


# ============================================================
# STAGE 3 — ML PREDICTION
# ============================================================

run_stage(
    [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(ML_PREDICTION),
        "--output",
        str(OUTPUT_DIR / "ml_prediction_executed.ipynb")
    ],
    "3/4 - ML Prediction"
)


# ============================================================
# STAGE 4 — OPTIMIZATION & RECOMMENDATION
# ============================================================

run_stage(
    [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(OPTIMIZATION),
        "--output",
        str(OUTPUT_DIR / "optimization_executed.ipynb")
    ],
    "4/4 - Optimization & Recommendation"
)


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 70)
print("🎉 BUS OPTIMIZER AJMAN PIPELINE COMPLETED")
print("=" * 70)

print("\nPipeline order:")
print("  1. Simulation")
print("  2. Data Analysis")
print("  3. ML Prediction")
print("  4. Optimization & Recommendation")

print("\nInput:")
print(f"  {PASSENGERS}")

print("\nSimulation output:")
print(f"  {BUSLOGS}")

print("\nFinal outputs:")
print(f"  {OUTPUT_DIR}")

print("\n")
