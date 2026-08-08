import "./App.css";
import greenmindLogo from "./assets/greenmind-logo.png";

function App() {
  const metrics = [
    {
      title: "Energy Usage",
      value: "315 kW",
      change: "↓ 4.8%",
      label: "vs. previous period",
    },
    {
      title: "Carbon Footprint",
      value: "132 kg",
      change: "↓ 7.2%",
      label: "CO₂ emissions",
    },
    {
      title: "Efficiency Score",
      value: "87%",
      change: "↑ 3.4%",
      label: "overall efficiency",
    },
  ];

  const recommendations = [
    {
      icon: "⚡",
      title: "Shift non-critical workload",
      description:
        "Move 12% of non-critical workloads to a lower-energy period.",
      saving: "Estimated saving: 4.8%",
    },
    {
      icon: "🌡️",
      title: "Optimize cooling",
      description:
        "Reduce cooling load while maintaining the recommended temperature range.",
      saving: "Estimated saving: 2.1%",
    },
    {
      icon: "🌱",
      title: "Increase renewable usage",
      description:
        "Use available renewable energy during the upcoming high-demand period.",
      saving: "Estimated carbon reduction: 6.3%",
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
              <small>All systems operational</small>
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

        {/* CHART + PREDICTION */}
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
                315 kW
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
                342 kW
              </strong>

              <span>
                Next hour
              </span>

            </div>

            <div className="prediction-bar">
              <div></div>
            </div>

            <div className="prediction-details">

              <span>
                Current: 315 kW
              </span>

              <span>
                +8.6%
              </span>

            </div>

            <p className="prediction-note">
              Demand is expected to increase during
              the upcoming high-load period.
            </p>

          </div>

        </section>

        {/* RECOMMENDATIONS */}
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
              3 actions
            </span>

          </div>

          <div className="recommendations">

            {recommendations.map((recommendation) => (

              <div
                className="recommendation-card"
                key={recommendation.title}
              >

                <div className="recommendation-icon">
                  {recommendation.icon}
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

            ))}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;