from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================
# GreenMind AI - Backend
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = (
    BASE_DIR
    / "models"
    / "energy_forecaster.joblib"
)

DATA_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "hourly_energy.csv"
)


app = FastAPI(
    title="GreenMind AI",
    description="AI-powered sustainability intelligence system",
    version="1.0.0",
)


# ============================================
# CORS
# ============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Load ML model
# ============================================

model = None

if MODEL_FILE.exists():
    model = joblib.load(MODEL_FILE)


# ============================================
# Features expected by the model
# ============================================

FEATURES = [
    "hour",
    "day_of_week",
    "day_of_month",
    "month",
    "is_weekend",
    "lag_1",
    "lag_24",
    "lag_168",
    "rolling_mean_24",
    "rolling_std_24",
    "rolling_mean_168",
]


# ============================================
# Home
# ============================================

@app.get("/")
def home():
    return {
        "message": "GreenMind AI backend is running!",
        "status": "online",
        "model_loaded": model is not None,
    }


# ============================================
# Generate prediction
# ============================================

def generate_prediction():
    """
    Generate the next-hour energy prediction
    using the trained Random Forest model.
    """

    if model is None:
        return None

    if not DATA_FILE.exists():
        return None

    df = pd.read_csv(
        DATA_FILE,
        parse_dates=["timestamp"],
    )

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    # Need enough historical data for
    # 168-hour lag and rolling features.
    if len(df) < 169:
        return None

    # ----------------------------------------
    # Current/latest observation
    # ----------------------------------------

    latest = df.iloc[-1]

    timestamp = latest["timestamp"]

    # ----------------------------------------
    # Build model features
    # ----------------------------------------

    features = pd.DataFrame(
        [
            {
                "hour": timestamp.hour,

                "day_of_week":
                    timestamp.dayofweek,

                "day_of_month":
                    timestamp.day,

                "month":
                    timestamp.month,

                "is_weekend":
                    int(timestamp.dayofweek >= 5),

                "lag_1":
                    df["total_energy"].iloc[-1],

                "lag_24":
                    df["total_energy"].iloc[-24],

                "lag_168":
                    df["total_energy"].iloc[-168],

                "rolling_mean_24":
                    df["total_energy"]
                    .iloc[-24:]
                    .mean(),

                "rolling_std_24":
                    df["total_energy"]
                    .iloc[-24:]
                    .std(),

                "rolling_mean_168":
                    df["total_energy"]
                    .iloc[-168:]
                    .mean(),
            }
        ]
    )

    # ----------------------------------------
    # Predict
    # ----------------------------------------

    prediction = model.predict(
        features[FEATURES]
    )[0]

    current_energy = (
        df["total_energy"].iloc[-1]
    )

    change = (
        (prediction - current_energy)
        / current_energy
    ) * 100

    return {
        "value": round(float(prediction), 2),
        "unit": "kW",
        "period": "Next hour",
        "change": round(float(change), 2),
        "based_on": str(timestamp),
    }


# ============================================
# Dashboard API
# ============================================

@app.get("/api/dashboard")
def dashboard():

    # ----------------------------------------
    # Load hourly history
    # ----------------------------------------

    if DATA_FILE.exists():

        df = pd.read_csv(
            DATA_FILE,
            parse_dates=["timestamp"],
        )

        df = df.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        # Last 24 observations
        history_df = df.tail(24)

        energy_history = [
            {
                "time": row["timestamp"].strftime(
                    "%H:%M"
                ),
                "energy": round(
                    float(row["total_energy"]),
                    2,
                ),
            }
            for _, row in history_df.iterrows()
        ]

        current_energy = round(
            float(df["total_energy"].iloc[-1]),
            2,
        )

        # Simple efficiency calculation
        # for the current demo stage.
        average_energy = float(
            df["total_energy"].tail(168).mean()
        )

        if average_energy > 0:

            efficiency_score = max(
                0,
                min(
                    100,
                    100
                    - (
                        (
                            current_energy
                            - average_energy
                        )
                        / average_energy
                        * 100
                    ),
                ),
            )

        else:
            efficiency_score = 0

    else:

        energy_history = []

        current_energy = 0

        efficiency_score = 0


    # ----------------------------------------
    # Prediction
    # ----------------------------------------

    prediction = generate_prediction()

    if prediction is None:

        prediction = {
            "value": 0,
            "unit": "kW",
            "period": "Next hour",
            "change": 0,
        }


    # ----------------------------------------
    # Carbon estimate
    # ----------------------------------------

    # Temporary emissions factor.
    # This will later be replaced with
    # region/grid-specific carbon intensity.
    carbon_factor = 0.000676

    carbon_footprint = round(
        current_energy * carbon_factor,
        2,
    )


    # ----------------------------------------
    # Recommendations
    # ----------------------------------------

    recommendations = []

    if prediction["change"] > 5:

        recommendations.append(
            {
                "title":
                    "Shift non-critical workload",

                "description":
                    "Move flexible workloads away "
                    "from the upcoming high-demand "
                    "period.",

                "saving":
                    "Potential demand reduction: "
                    "4–8%",
            }
        )

    if current_energy > (
        average_energy * 1.05
        if DATA_FILE.exists()
        else current_energy
    ):

        recommendations.append(
            {
                "title":
                    "Optimize current energy load",

                "description":
                    "Current demand is above the "
                    "recent operating average. "
                    "Review non-essential loads.",

                "saving":
                    "Potential energy reduction: "
                    "2–5%",
            }
        )

    recommendations.append(
        {
            "title":
                "Increase renewable usage",

            "description":
                "Use available renewable energy "
                "during periods of higher demand "
                "to reduce grid dependence.",

            "saving":
                "Potential carbon reduction: "
                "up to 6%",
        }
    )

    return {
        "energy_usage": {
            "value": current_energy,
            "unit": "kW",
            "change": 0,
        },

        "carbon_footprint": {
            "value": carbon_footprint,
            "unit": "kg",
            "change": 0,
        },

        "efficiency_score": {
            "value": round(
                efficiency_score,
                1,
            ),
            "unit": "%",
            "change": 0,
        },

        "prediction": prediction,

        "energy_history": energy_history,

        "recommendations": recommendations,
    }