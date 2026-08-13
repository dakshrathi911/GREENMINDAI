from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# GREENMIND AI - REAL ELECTRICITY DATA BACKEND
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_FILE = BASE_DIR / "models" / "energy_forecaster.joblib"
DATA_FILE = BASE_DIR / "data" / "processed" / "hourly_energy.csv"


app = FastAPI(
    title="GreenMind AI",
    description="AI-powered electricity demand forecasting and optimization",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODEL FEATURES
# These MUST match train_model.py exactly.
# ============================================================

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


# ============================================================
# LOAD MODEL
# ============================================================

model = None

try:
    model = joblib.load(MODEL_FILE)

    print(
        "GreenMind AI model loaded successfully."
    )

except Exception as e:

    print(
        "WARNING: Could not load model:"
    )

    print(e)


# ============================================================
# LOAD REAL PROCESSED DATA
# ============================================================

df = None

try:

    if DATA_FILE.exists():

        df = pd.read_csv(
            DATA_FILE,
            parse_dates=["timestamp"],
        )

        df = (
            df
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        print(
            f"Energy dataset loaded successfully: "
            f"{len(df)} hourly observations."
        )

    else:

        print(
            f"WARNING: Dataset not found at "
            f"{DATA_FILE}"
        )

except Exception as e:

    print(
        "WARNING: Could not load energy dataset:"
    )

    print(e)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message":
            "GreenMind AI backend is running!",

        "status":
            "online",

        "model_loaded":
            model is not None,

        "dataset_loaded":
            df is not None,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status":
            "healthy",

        "model_loaded":
            model is not None,

        "dataset_loaded":
            df is not None,

        "dataset_rows":
            len(df) if df is not None else 0,
    }


# ============================================================
# BUILD FEATURES FOR NEXT-HOUR PREDICTION
# ============================================================

def build_prediction_features(data):

    if data is None:

        return None

    if len(data) < 169:

        return None

    latest_timestamp = data[
        "timestamp"
    ].iloc[-1]

    features = pd.DataFrame(
        [
            {
                "hour":
                    latest_timestamp.hour,

                "day_of_week":
                    latest_timestamp.dayofweek,

                "day_of_month":
                    latest_timestamp.day,

                "month":
                    latest_timestamp.month,

                "is_weekend":
                    int(
                        latest_timestamp.dayofweek >= 5
                    ),

                "lag_1":
                    data[
                        "total_energy"
                    ].iloc[-1],

                "lag_24":
                    data[
                        "total_energy"
                    ].iloc[-24],

                "lag_168":
                    data[
                        "total_energy"
                    ].iloc[-168],

                "rolling_mean_24":
                    data[
                        "total_energy"
                    ]
                    .iloc[-24:]
                    .mean(),

                "rolling_std_24":
                    data[
                        "total_energy"
                    ]
                    .iloc[-24:]
                    .std(),

                "rolling_mean_168":
                    data[
                        "total_energy"
                    ]
                    .iloc[-168:]
                    .mean(),
            }
        ]
    )

    return features[FEATURES]


# ============================================================
# GENERATE ML PREDICTION
# ============================================================

def generate_prediction(data):

    if model is None:

        return None

    features = build_prediction_features(
        data
    )

    if features is None:

        return None

    # --------------------------------------------------------
    # Main Random Forest prediction
    # --------------------------------------------------------

    prediction = model.predict(
        features
    )[0]

    prediction = float(
        prediction
    )

    # --------------------------------------------------------
    # Individual tree predictions
    #
    # IMPORTANT:
    # Convert to NumPy before sending data to individual
    # DecisionTreeRegressor objects.
    #
    # This removes:
    #
    # "X has feature names, but DecisionTreeRegressor
    # was fitted without feature names"
    # --------------------------------------------------------

    tree_predictions = []

    if hasattr(
        model,
        "estimators_"
    ):

        feature_values = (
            features.to_numpy()
        )

        for tree in model.estimators_:

            tree_prediction = tree.predict(
                feature_values
            )[0]

            tree_predictions.append(
                float(
                    tree_prediction
                )
            )

    # --------------------------------------------------------
    # Current demand
    # --------------------------------------------------------

    current_energy = float(
        data[
            "total_energy"
        ].iloc[-1]
    )

    # --------------------------------------------------------
    # Prediction change
    # --------------------------------------------------------

    if current_energy != 0:

        change = (
            (
                prediction
                - current_energy
            )
            / current_energy
        ) * 100

    else:

        change = 0

    # --------------------------------------------------------
    # Model confidence
    # --------------------------------------------------------

    if len(tree_predictions) > 1:

        prediction_std = (
            pd.Series(
                tree_predictions
            ).std()
        )

        relative_uncertainty = (
            prediction_std
            / max(
                abs(prediction),
                1
            )
        )

        confidence = (
            100
            * (
                1
                - relative_uncertainty
            )
        )

        confidence = max(
            0,
            min(
                100,
                confidence
            )
        )

    else:

        prediction_std = 0

        confidence = 0

    return {

        "value":
            round(
                prediction,
                2
            ),

        "unit":
            "kW",

        "period":
            "Next hour",

        "change":
            round(
                change,
                2
            ),

        "confidence":
            round(
                confidence,
                1
            ),

        "uncertainty":
            round(
                prediction_std,
                2
            ),

        "based_on":
            str(
                data[
                    "timestamp"
                ].iloc[-1]
            ),
    }


# ============================================================
# EFFICIENCY SCORE
# ============================================================

def calculate_efficiency(data):

    if data is None:

        return 0

    if len(data) < 168:

        return 0

    current_energy = float(
        data[
            "total_energy"
        ].iloc[-1]
    )

    current_hour = int(
        data[
            "timestamp"
        ].iloc[-1]
        .hour
    )

    # --------------------------------------------------------
    # Historical demand for the same hour.
    #
    # We exclude the latest observation because that is the
    # current value we are evaluating.
    # --------------------------------------------------------

    historical = data[
        (
            data[
                "timestamp"
            ].dt.hour
            == current_hour
        )
    ].iloc[:-1].tail(28)

    if len(historical) < 7:

        historical = data.iloc[
            -168:-1
        ]

    expected_energy = float(
        historical[
            "total_energy"
        ].median()
    )

    if expected_energy <= 0:

        return 0

    # --------------------------------------------------------
    # Deviation from expected demand
    # --------------------------------------------------------

    deviation = abs(
        (
            current_energy
            - expected_energy
        )
        / expected_energy
    ) * 100

    # --------------------------------------------------------
    # Score
    #
    # 0% deviation -> 100
    # 10% deviation -> 85
    # 20% deviation -> 70
    #
    # Capped between 0 and 100.
    # --------------------------------------------------------

    score = 100 - (
        deviation * 1.5
    )

    score = max(
        0,
        min(
            100,
            score
        )
    )

    return round(
        score,
        1
    )


# ============================================================
# CARBON ESTIMATION
# ============================================================

def calculate_carbon(
    energy_kwh
):
    """
    Approximate carbon footprint.

    The dataset does not contain direct carbon-intensity
    measurements, so this uses a configurable grid factor.
    """

    carbon_factor = 0.000676

    carbon = (
        energy_kwh
        * carbon_factor
    )

    return round(
        carbon,
        2
    )


# ============================================================
# GENERATE AI RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    data,
    prediction
):

    recommendations = []

    if data is None:

        return recommendations

    if prediction is None:

        return recommendations

    current_energy = float(
        data[
            "total_energy"
        ].iloc[-1]
    )

    predicted_energy = float(
        prediction[
            "value"
        ]
    )

    change = float(
        prediction[
            "change"
        ]
    )

    confidence = float(
        prediction[
            "confidence"
        ]
    )

    # ========================================================
    # PREDICTION-BASED RECOMMENDATION
    # ========================================================

    if change <= -10:

        recommendations.append(
            {
                "title":
                    "Use the upcoming low-demand period",

                "description":
                    (
                        "GreenMind AI predicts a significant "
                        "drop in energy demand. This may be "
                        "a favorable period for flexible or "
                        "energy-intensive workloads."
                    ),

                "saving":
                    (
                        "Predicted reduction: "
                        f"{abs(change):.1f}%"
                    ),

                "priority":
                    (
                        "high"
                        if confidence >= 80
                        else "medium"
                    ),
            }
        )

    elif change <= -5:

        recommendations.append(
            {
                "title":
                    "Schedule flexible workloads",

                "description":
                    (
                        "Energy demand is expected to "
                        "decrease during the next hour. "
                        "Consider using this lower-demand "
                        "period for flexible operations."
                    ),

                "saving":
                    (
                        "Predicted reduction: "
                        f"{abs(change):.1f}%"
                    ),

                "priority":
                    "medium",
            }
        )

    elif change >= 10:

        recommendations.append(
            {
                "title":
                    "Prepare for high demand",

                "description":
                    (
                        "GreenMind AI predicts a significant "
                        "increase in energy demand during "
                        "the next hour. Consider shifting "
                        "flexible or non-critical workloads."
                    ),

                "saving":
                    (
                        "Predicted increase: "
                        f"{change:.1f}%"
                    ),

                "priority":
                    (
                        "high"
                        if confidence >= 80
                        else "medium"
                    ),
            }
        )

    elif change >= 5:

        recommendations.append(
            {
                "title":
                    "Shift flexible workloads",

                "description":
                    (
                        "Energy demand is expected to rise "
                        "during the next hour. Move "
                        "non-critical workloads to a "
                        "lower-demand period where possible."
                    ),

                "saving":
                    (
                        "Predicted increase: "
                        f"{change:.1f}%"
                    ),

                "priority":
                    "medium",
            }
        )

    else:

        recommendations.append(
            {
                "title":
                    "Maintain current operating pattern",

                "description":
                    (
                        "GreenMind AI expects relatively "
                        "stable energy demand during the "
                        "next hour. No major load-shifting "
                        "action is currently indicated."
                    ),

                "saving":
                    "Demand expected to remain stable",

                "priority":
                    "low",
            }
        )

    # ========================================================
    # WEEKLY BASELINE ANALYSIS
    # ========================================================

    weekly_average = float(
        data[
            "total_energy"
        ]
        .tail(168)
        .mean()
    )

    if weekly_average > 0:

        baseline_change = (
            (
                current_energy
                - weekly_average
            )
            / weekly_average
        ) * 100

        if baseline_change >= 10:

            recommendations.append(
                {
                    "title":
                        "Optimize current energy load",

                    "description":
                        (
                            "Current demand is significantly "
                            "above the recent weekly baseline. "
                            "Review non-essential energy loads."
                        ),

                    "saving":
                        (
                            f"{baseline_change:.1f}% "
                            "above baseline"
                        ),

                    "priority":
                        "high",
                }
            )

        elif baseline_change >= 5:

            recommendations.append(
                {
                    "title":
                        "Review elevated energy usage",

                    "description":
                        (
                            "Current demand is above the "
                            "recent weekly baseline. Check "
                            "for non-essential or avoidable "
                            "energy consumption."
                        ),

                    "saving":
                        (
                            f"{baseline_change:.1f}% "
                            "above baseline"
                        ),

                    "priority":
                        "medium",
                }
            )

    # ========================================================
    # RENEWABLE RECOMMENDATION
    # ========================================================

    recommendations.append(
        {
            "title":
                "Increase renewable usage",

            "description":
                (
                    "Use available renewable energy during "
                    "higher-demand periods to reduce grid "
                    "dependence and associated emissions."
                ),

            "saving":
                "Potential carbon reduction",

            "priority":
                "low",
        }
    )

    return recommendations


# ============================================================
# ENERGY HISTORY
# ============================================================

def get_energy_history(data):

    if data is None:

        return []

    history = data.tail(24)

    result = []

    for _, row in history.iterrows():

        result.append(
            {
                "time":
                    row[
                        "timestamp"
                    ].strftime(
                        "%H:%M"
                    ),

                "energy":
                    round(
                        float(
                            row[
                                "total_energy"
                            ]
                        ),
                        2
                    ),
            }
        )

    return result


# ============================================================
# DASHBOARD ENDPOINT
# ============================================================

@app.get("/api/dashboard")
def dashboard():

    # --------------------------------------------------------
    # Dataset check
    # --------------------------------------------------------

    if df is None:

        return {
            "energy_usage": {
                "value": 0,
                "unit": "kW",
                "change": 0,
            },

            "carbon_footprint": {
                "value": 0,
                "unit": "kg",
                "change": 0,
            },

            "efficiency_score": {
                "value": 0,
                "unit": "%",
                "change": 0,
            },

            "prediction": {
                "value": 0,
                "unit": "kW",
                "period": "Next hour",
                "change": 0,
                "confidence": 0,
                "uncertainty": 0,
            },

            "energy_history": [],

            "recommendations": [],
        }

    # --------------------------------------------------------
    # Current energy
    # --------------------------------------------------------

    current_energy = round(
        float(
            df[
                "total_energy"
            ].iloc[-1]
        ),
        2
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = generate_prediction(
        df
    )

    if prediction is None:

        prediction = {
            "value":
                current_energy,

            "unit":
                "kW",

            "period":
                "Next hour",

            "change":
                0,

            "confidence":
                0,

            "uncertainty":
                0,

            "based_on":
                str(
                    df[
                        "timestamp"
                    ].iloc[-1]
                ),
        }

    # --------------------------------------------------------
    # Efficiency
    # --------------------------------------------------------

    efficiency = calculate_efficiency(
        df
    )

    # --------------------------------------------------------
    # Carbon
    # --------------------------------------------------------

    carbon = calculate_carbon(
        current_energy
    )

    # --------------------------------------------------------
    # History
    # --------------------------------------------------------

    history = get_energy_history(
        df
    )

    # --------------------------------------------------------
    # Recommendations
    # --------------------------------------------------------

    recommendations = generate_recommendations(
        df,
        prediction
    )

    # --------------------------------------------------------
    # Final dashboard response
    # --------------------------------------------------------

    return {

        "energy_usage": {
            "value":
                current_energy,

            "unit":
                "kW",

            "change":
                0,
        },

        "carbon_footprint": {
            "value":
                carbon,

            "unit":
                "kg",

            "change":
                0,
        },

        "efficiency_score": {
            "value":
                efficiency,

            "unit":
                "%",

            "change":
                0,
        },

        "prediction":
            prediction,

        "energy_history":
            history,

        "recommendations":
            recommendations,
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.get("/api/prediction")
def prediction_endpoint():

    if df is None:

        return {
            "error":
                "Energy dataset is not loaded."
        }

    prediction = generate_prediction(
        df
    )

    return {
        "prediction":
            prediction
    }


# ============================================================
# RECOMMENDATIONS ENDPOINT
# ============================================================

@app.get("/api/recommendations")
def recommendations_endpoint():

    if df is None:

        return {
            "recommendations":
                []
        }

    prediction = generate_prediction(
        df
    )

    recommendations = generate_recommendations(
        df,
        prediction
    )

    return {
        "recommendations":
            recommendations
    }


# ============================================================
# RUN INFORMATION
# ============================================================

@app.get("/api/info")
def info():

    return {

        "project":
            "GreenMind AI",

        "model":
            "Random Forest",

        "model_loaded":
            model is not None,

        "dataset_loaded":
            df is not None,

        "dataset_path":
            str(
                DATA_FILE
            ),

        "model_path":
            str(
                MODEL_FILE
            ),

        "features":
            FEATURES,

        "observations":
            len(df)
            if df is not None
            else 0,
    }