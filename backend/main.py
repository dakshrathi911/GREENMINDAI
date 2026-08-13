from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GreenMind AI")


# Allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "GreenMind AI backend is running!",
        "status": "online"
    }


@app.get("/api/dashboard")
def dashboard():
    return {
        "energy_usage": {
            "value": 315,
            "unit": "kW",
            "change": -4.8
        },

        "carbon_footprint": {
            "value": 132,
            "unit": "kg",
            "change": -7.2
        },

        "efficiency_score": {
            "value": 87,
            "unit": "%",
            "change": 3.4
        },

        "prediction": {
            "value": 342,
            "unit": "kW",
            "period": "Next hour",
            "change": 8.6
        },

        "energy_history": [
            {"time": "00:00", "energy": 218},
            {"time": "02:00", "energy": 205},
            {"time": "04:00", "energy": 198},
            {"time": "06:00", "energy": 231},
            {"time": "08:00", "energy": 287},
            {"time": "10:00", "energy": 301},
            {"time": "12:00", "energy": 325},
            {"time": "14:00", "energy": 315},
            {"time": "16:00", "energy": 338},
            {"time": "18:00", "energy": 351},
            {"time": "20:00", "energy": 329},
            {"time": "22:00", "energy": 290}
        ],

        "recommendations": [
            {
                "title": "Shift non-critical workload",
                "description": "Move 12% of non-critical workloads to a lower-energy period.",
                "saving": "Estimated saving: 4.8%"
            },
            {
                "title": "Optimize cooling",
                "description": "Reduce cooling load while maintaining the recommended temperature range.",
                "saving": "Estimated saving: 2.1%"
            },
            {
                "title": "Increase renewable usage",
                "description": "Use available renewable energy during the upcoming high-demand period.",
                "saving": "Estimated carbon reduction: 6.3%"
            }
        ]
    }