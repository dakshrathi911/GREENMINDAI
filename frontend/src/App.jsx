import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/dashboard";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchDashboard = async () => {
    try {
      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data = await response.json();

      setDashboard(data);
      setError("");
    } catch (err) {
      console.error(err);
      setError(
        "Could not connect to GreenMind AI backend."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();

    // Refresh dashboard every 30 seconds.
    const interval = setInterval(
      fetchDashboard,
      30000
    );

    return () => clearInterval(interval);
  }, []);

  const formatNumber = (value) => {
    if (value === undefined || value === null) {
      return "--";
    }

    return Number(value).toLocaleString(
      "en-IN",
      {
        maximumFractionDigits: 0,
      }
    );
  };

  const getPriorityClass = (priority) => {
    switch (priority) {
      case "high":
        return "priority-high";

      case "medium":
        return "priority-medium";

      default:
        return "priority-low";
    }
  };

  const getPriorityLabel = (priority) => {
    switch (priority) {
      case "high":
        return "HIGH PRIORITY";

      case "medium":
        return "MEDIUM PRIORITY";

      default:
        return "LOW PRIORITY";
    }
  };

  const getTrendClass = (change) => {
    if (change > 0) {
      return "trend-up";
    }

    if (change < 0) {
      return "trend-down";
    }

    return "trend-neutral";
  };

  if (loading) {
    return (
      <div className="app loading-screen">
        <div className="loading-card">
          <div className="loading-spinner"></div>

          <h2>GreenMind AI</h2>

          <p>
            Loading energy intelligence...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">

      {/* ================================== */}
      {/* HEADER */}
      {/* ================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-logo">
            🌱
          </div>

          <div>
            <h1>GreenMind AI</h1>

            <span>
              Energy Intelligence Platform
            </span>
          </div>

        </div>

        <div className="system-status">

          <span className="status-dot"></span>

          AI SYSTEM ONLINE

        </div>

      </header>


      {/* ================================== */}
      {/* ERROR */}
      {/* ================================== */}

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}


      {dashboard && (
        <main className="dashboard">

          {/* ================================== */}
          {/* OVERVIEW CARDS */}
          {/* ================================== */}

          <section className="metrics-grid">

            <div className="metric-card">

              <div className="metric-header">
                <span>ENERGY USAGE</span>
                <span className="metric-icon">
                  ⚡
                </span>
              </div>

              <div className="metric-value">
                {formatNumber(
                  dashboard.energy_usage.value
                )}

                <small>
                  {" "}
                  {dashboard.energy_usage.unit}
                </small>
              </div>

              <div className="metric-description">
                Current aggregate demand
              </div>

            </div>


            <div className="metric-card">

              <div className="metric-header">
                <span>CARBON FOOTPRINT</span>
                <span className="metric-icon">
                  ◉
                </span>
              </div>

              <div className="metric-value">
                {formatNumber(
                  dashboard.carbon_footprint.value
                )}

                <small>
                  {" "}
                  {dashboard.carbon_footprint.unit}
                </small>
              </div>

              <div className="metric-description">
                Estimated current emissions
              </div>

            </div>


            <div className="metric-card">

              <div className="metric-header">
                <span>EFFICIENCY SCORE</span>
                <span className="metric-icon">
                  ✦
                </span>
              </div>

              <div className="metric-value">
                {dashboard.efficiency_score.value}

                <small>
                  {" "}
                  {dashboard.efficiency_score.unit}
                </small>
              </div>

              <div className="efficiency-bar">

                <div
                  className="efficiency-fill"
                  style={{
                    width: `${dashboard.efficiency_score.value}%`,
                  }}
                />

              </div>

            </div>

          </section>


          {/* ================================== */}
          {/* MAIN GRID */}
          {/* ================================== */}

          <section className="main-grid">


            {/* ================================== */}
            {/* ENERGY HISTORY */}
            {/* ================================== */}

            <div className="panel history-panel">

              <div className="panel-header">

                <div>
                  <h2>Energy Demand</h2>

                  <p>
                    Last 24 hours
                  </p>
                </div>

                <span className="live-label">
                  ● LIVE DATA
                </span>

              </div>


              <div className="chart-container">

                {dashboard.energy_history?.map(
                  (point, index) => {

                    const values =
                      dashboard.energy_history.map(
                        (item) =>
                          item.energy
                      );

                    const max =
                      Math.max(...values);

                    const height =
                      max > 0
                        ? (point.energy / max) * 100
                        : 0;

                    return (
                      <div
                        className="chart-column"
                        key={`${point.time}-${index}`}
                      >

                        <div
                          className="chart-bar"
                          style={{
                            height: `${Math.max(
                              height,
                              2
                            )}%`,
                          }}
                          title={`${point.time}: ${formatNumber(
                            point.energy
                          )} kW`}
                        />

                        <span>
                          {point.time}
                        </span>

                      </div>
                    );
                  }
                )}

              </div>

            </div>


            {/* ================================== */}
            {/* AI PREDICTION */}
            {/* ================================== */}

            <div className="panel prediction-panel">

              <div className="panel-header">

                <div>
                  <h2>AI Forecast</h2>

                  <p>
                    {dashboard.prediction.period}
                  </p>
                </div>

                <div className="ai-badge">
                  AI
                </div>

              </div>


              <div className="prediction-value">

                {formatNumber(
                  dashboard.prediction.value
                )}

                <span>
                  {dashboard.prediction.unit}
                </span>

              </div>


              <div
                className={`prediction-change ${getTrendClass(
                  dashboard.prediction.change
                )}`}
              >

                {dashboard.prediction.change > 0
                  ? "↑"
                  : dashboard.prediction.change < 0
                  ? "↓"
                  : "→"}

                {" "}

                {Math.abs(
                  dashboard.prediction.change
                ).toFixed(2)}
                %

                <span>
                  {" "}
                  predicted change
                </span>

              </div>


              {/* Confidence */}

              <div className="confidence-section">

                <div className="confidence-header">

                  <span>
                    Model confidence
                  </span>

                  <strong>
                    {dashboard.prediction.confidence?.toFixed(
                      1
                    )}
                    %
                  </strong>

                </div>


                <div className="confidence-bar">

                  <div
                    className="confidence-fill"
                    style={{
                      width: `${dashboard.prediction.confidence || 0}%`,
                    }}
                  />

                </div>


                <p>
                  Based on Random Forest
                  prediction consistency
                </p>

              </div>


              <div className="prediction-source">

                Based on historical data through{" "}
                <strong>
                  {dashboard.prediction.based_on}
                </strong>

              </div>

            </div>

          </section>


          {/* ================================== */}
          {/* AI RECOMMENDATIONS */}
          {/* ================================== */}

          <section className="panel recommendations-panel">

            <div className="panel-header">

              <div>

                <h2>
                  AI Recommendations
                </h2>

                <p>
                  Actions generated from
                  current energy patterns
                </p>

              </div>

              <div className="recommendation-icon">
                ✦
              </div>

            </div>


            <div className="recommendations-list">

              {dashboard.recommendations?.map(
                (recommendation, index) => (

                  <div
                    className={`recommendation-card ${getPriorityClass(
                      recommendation.priority
                    )}`}
                    key={index}
                  >

                    <div className="recommendation-top">

                      <span
                        className={`priority-badge ${getPriorityClass(
                          recommendation.priority
                        )}`}
                      >
                        {getPriorityLabel(
                          recommendation.priority
                        )}
                      </span>

                    </div>


                    <h3>
                      {recommendation.title}
                    </h3>


                    <p>
                      {recommendation.description}
                    </p>


                    <div className="recommendation-saving">

                      <span>
                        Potential impact
                      </span>

                      <strong>
                        {recommendation.saving}
                      </strong>

                    </div>

                  </div>

                )
              )}

            </div>

          </section>


          {/* ================================== */}
          {/* FOOTER */}
          {/* ================================== */}

          <footer>

            <span>
              GreenMind AI
            </span>

            <span>
              AI-powered energy intelligence
            </span>

            <span>
              ● System operational
            </span>

          </footer>

        </main>
      )}

    </div>
  );
}

export default App;