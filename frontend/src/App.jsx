import { useEffect, useState } from "react";
import "./App.css";
import greenmindLogo from "./assets/greenmind-logo.png";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/api/dashboard`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch dashboard data");
        }

        return response.json();
      })
      .then((data) => {
        setDashboard(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError("Could not connect to GreenMind AI backend.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-logo">
          <img src={greenmindLogo} alt="GreenMind AI" />
        </div>

        <h2>GreenMind AI</h2>
        <p>Connecting to sustainability intelligence...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-screen">
        <div className="error-icon">!</div>

        <h2>GreenMind AI</h2>

        <p>{error}</p>

        <button
          className="action-button"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  const metrics = [
    {
      title: "Energy Usage",
      value: `${dashboard.energy_usage.value} ${dashboard.energy_usage.unit}`,
      change: `${dashboard.energy_usage.change > 0 ? "↑" : "↓"} ${Math.abs(
        dashboard.energy_usage.change
      )}%`,
      label: "vs. previous period",
    },
    {
      title: "Carbon Footprint",
      value: `${dashboard.carbon_footprint.value} ${dashboard.carbon_footprint.unit}`,
      change: `${dashboard.carbon_footprint.change > 0 ? "↑" : "↓"} ${Math.abs(
        dashboard.carbon_footprint.change
      )}%`,
      label: "CO₂ emissions",
    },
    {
      title: "Efficiency Score",
      value: `${dashboard.efficiency_score.value}${dashboard.efficiency_score.unit}`,
      change: `${dashboard.efficiency_score.change > 0 ? "↑" : "↓"} ${Math.abs(
        dashboard.efficiency_score.change
      )}%`,
      label: "overall efficiency",
    },
  ];

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <div className="brand">

          <div className="brand-mark">
            <img
              src={greenmindLogo}
              alt="GreenMind AI logo"
            />
          </div>

          <div className="brand-text">
            <h1>
              GreenMind <span>AI</span>
            </h1>

            <p>
              Sustainability Intelligence
            </p>
          </div>

        </div>

        <nav className="navigation">

          <button className="nav-item active">
            <span>⌂</span>
            Dashboard
          </button>

          <button className="nav-item">
            <span>◫</span>
            Analytics
          </button>

          <button className="nav-item">
            <span>✦</span>
            AI Insights
          </button>

          <button className="nav-item">
            <span>⚙</span>
            Optimize
          </button>

        </nav>

        <div className="sidebar-bottom">

          <button className="nav-item">
            <span>⚙</span>
            Settings
          </button>

          <div className="system-status">

            <span className="status-dot"></span>

            <div>
              <strong>System Online</strong>
              <small>Backend connected</small>
            </div>

          </div>

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <main className="main-content">

        <header className="topbar">

          <div>

            <p className="eyebrow">
              GREENMIND AI
            </p>

            <h2>
              Dashboard
            </h2>

            <p className="subtitle">
              Intelligent sustainability monitoring and optimization.
            </p>

          </div>

          <div className="topbar-status">

            <span className="status-dot"></span>

            Live monitoring

          </div>

        </header>

        {/* METRICS */}

        <section className="metrics-grid">

          {metrics.map((metric) => (

            <div
              className="metric-card"
              key={metric.title}
            >

              <div className="metric-header">

                <span>
                  {metric.title}
                </span>

                <span className="metric-icon">
                  ◈
                </span>

              </div>

              <h3>
                {metric.value}
              </h3>

              <div className="metric-footer">

                <span className="positive">
                  {metric.change}
                </span>

                <span>
                  {metric.label}
                </span>

              </div>

            </div>

          ))}

        </section>

        {/* CHART + AI PREDICTION */}

        <section className="dashboard-grid">

          <div className="panel energy-panel">

            <div className="panel-header">

              <div>

                <h3>
                  Energy Consumption
                </h3>

                <p>
                  Power usage over the last 24 hours
                </p>

              </div>

              <span className="panel-value">
                {dashboard.energy_usage.value}{" "}
                {dashboard.energy_usage.unit}
              </span>

            </div>

            <div className="chart">

              <div className="chart-grid"></div>

              <div className="chart-line"></div>

              <div className="chart-labels">

                <span>00:00</span>
                <span>06:00</span>
                <span>12:00</span>
                <span>18:00</span>
                <span>Now</span>

              </div>

            </div>

          </div>

          {/* AI PREDICTION */}

          <div className="panel prediction-panel">

            <div className="panel-header">

              <div>

                <h3>
                  AI Prediction
                </h3>

                <p>
                  Expected energy demand
                </p>

              </div>

              <span className="ai-badge">
                AI
              </span>

            </div>

            <div className="prediction-value">

              <strong>
                {dashboard.prediction.value}{" "}
                {dashboard.prediction.unit}
              </strong>

              <span>
                {dashboard.prediction.period}
              </span>

            </div>

            <div className="prediction-bar">
              <div></div>
            </div>

            <div className="prediction-details">

              <span>
                Current: {dashboard.energy_usage.value}{" "}
                {dashboard.energy_usage.unit}
              </span>

              <span>
                +{dashboard.prediction.change}%
              </span>

            </div>

            <p className="prediction-note">

              Demand is expected to increase during
              the upcoming high-load period.

            </p>

          </div>

        </section>

        {/* AI RECOMMENDATIONS */}

        <section className="panel recommendations-panel">

          <div className="panel-header">

            <div>

              <h3>
                AI Recommendations
              </h3>

              <p>
                Optimization opportunities detected by GreenMind AI
              </p>

            </div>

            <span className="recommendation-count">
              {dashboard.recommendations.length} actions
            </span>

          </div>

          <div className="recommendations">

            {dashboard.recommendations.map(
              (recommendation, index) => (

                <div
                  className="recommendation-card"
                  key={recommendation.title}
                >

                  <div className="recommendation-icon">

                    {index === 0
                      ? "⚡"
                      : index === 1
                      ? "🌡️"
                      : "🌱"}

                  </div>

                  <div className="recommendation-content">

                    <h4>
                      {recommendation.title}
                    </h4>

                    <p>
                      {recommendation.description}
                    </p>

                    <span>
                      {recommendation.saving}
                    </span>

                  </div>

                  <button className="action-button">
                    Review
                  </button>

                </div>

              )
            )}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;