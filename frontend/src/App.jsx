import { useState } from "react";

export default function App() {
  const API_BASE = "https://trim-bharath.onrender.com";
  // State hooks
  const [longUrl, setLongUrl] = useState("");
  const [customAlias, setCustomAlias] = useState("");
  const [shortUrl, setShortUrl] = useState("");
  const [shortenerError, setShortenerError] = useState("");
  const [analyticsCode, setAnalyticsCode] = useState("");
  const [analyticsData, setAnalyticsData] = useState(null);
  const [analyticsError, setAnalyticsError] = useState("");

  // Handler 1: Shorten long URL
  const handleShorten = async (e) => {
    e.preventDefault();
    setShortenerError("");
    setShortUrl("");

    if (!longUrl) {
      setShortenerError("Destination URL is required.");
      return;
    }

    const payload = { long_url: longUrl };
    if (customAlias) payload.custom_alias = customAlias;

    try {
      const response = await fetch(`${API_BASE}/shorten`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (response.ok) {
        setShortUrl(data.short_url);
        setLongUrl("");
        setCustomAlias("");
      } else {
        setShortenerError(data.detail || "Failed to shorten URL.");
      }
    } catch (err) {
      setShortenerError("Could not connect to the backend server.");
    }
  };

  // Handler 2: Fetch metric telemetry with URL parsing
  const handleFetchAnalytics = async (e) => {
    e.preventDefault();
    setAnalyticsError("");
    setAnalyticsData(null);

    let code = analyticsCode.trim();

    if (!code) {
      setAnalyticsError("Please enter a short code or full short URL.");
      return;
    }

    // --- SMART PARSING LOGIC ---
    if (code.includes("http://") || code.includes("https://")) {
      try {
        const parsedUrl = new URL(code);
        code = parsedUrl.pathname.slice(1); 
      } catch (err) {
        setAnalyticsError("Invalid URL format parsed.");
        return;
      }
    }

    try {
      const response = await fetch(`${API_BASE}/analytics/${code}`);
      const data = await response.json();

      if (response.ok) {
        setAnalyticsData(data);
      } else {
        setAnalyticsError(data.detail || "Short code not found.");
      }
    } catch (err) {
      setAnalyticsError("Could not retrieve analytics telemetry.");
    }
  };

  // Minimalist style sheet configurations
  const styles = {
    container: { backgroundColor: "#ffffff", color: "#1f2937", minHeight: "100vh", fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', padding: "40px 20px" },
    wrapper: { maxWidth: "800px", margin: "0 auto" },
    header: { marginBottom: "40px" },
    title: { fontSize: "28px", fontWeight: "700", color: "#111827", letterSpacing: "-0.5px", margin: "0 0 4px 0" },
    subtitle: { color: "#6b7280", fontSize: "14px", margin: 0 },
    grid: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: "40px" },
    card: { backgroundColor: "#ffffff", padding: "0px", borderRadius: "0px" },
    sectionTitle: { fontSize: "18px", fontWeight: "600", marginBottom: "20px", color: "#111827", marginTop: 0, borderBottom: "1px solid #e5e7eb", paddingBottom: "8px" },
    formGroup: { marginBottom: "16px" },
    label: { display: "block", fontSize: "13px", fontWeight: "500", color: "#374151", marginBottom: "6px" },
    input: { width: "100%", padding: "8px 12px", borderRadius: "6px", backgroundColor: "#ffffff", border: "1px solid #d1d5db", color: "#111827", fontSize: "14px", boxSizing: "border-box", transition: "border-color 0.15s ease" },
    btnDark: { width: "100%", backgroundColor: "#111827", color: "#ffffff", padding: "10px", border: "none", borderRadius: "6px", fontSize: "14px", fontWeight: "500", cursor: "pointer" },
    error: { marginTop: "12px", color: "#dc2626", fontSize: "13px", margin: "8px 0 0 0" },
    resultBox: { marginTop: "20px", padding: "12px", backgroundColor: "#f9fafb", borderRadius: "6px", border: "1px solid #e5e7eb" },
    link: { color: "#2563eb", fontWeight: "500", textDecoration: "underline", wordBreak: "break-all", fontSize: "14px" },
    analyticsBox: { marginTop: "20px", borderTop: "1px dashed #e5e7eb", paddingTop: "16px" },
    counter: { fontSize: "36px", fontWeight: "700", color: "#111827", margin: "2px 0 16px 0" },
    logItem: { padding: "8px 0", borderBottom: "1px solid #f3f4f6", listStyleType: "none" }
  };

  return (
    <div style={styles.container}>
      <div style={styles.wrapper}>
        
        <header style={styles.header}>
          <h1 style={styles.title}>Trim.</h1>
          <p style={styles.subtitle}>A clean link compressor and analytics dashboard.</p>
        </header>

        <div style={styles.grid}>
          
          {/* COLUMN 1: SHORTENER */}
          <section style={styles.card}>
            <h2 style={styles.sectionTitle}>Shorten URL</h2>
            <form onSubmit={handleShorten}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Target URL</label>
                <input
                  type="text"
                  value={longUrl}
                  onChange={(e) => setLongUrl(e.target.value)}
                  placeholder="Paste long link here..."
                  style={styles.input}
                />
              </div>
              <div style={styles.formGroup}>
                <label style={styles.label}>Custom Alias (optional)</label>
                <input
                  type="text"
                  value={customAlias}
                  onChange={(e) => setCustomAlias(e.target.value)}
                  placeholder="e.g., portfolio"
                  style={styles.input}
                />
              </div>
              <button type="submit" style={styles.btnDark}>Shorten Link</button>
            </form>

            {shortenerError && <p style={styles.error}>{shortenerError}</p>}

            {shortUrl && (
              <div style={styles.resultBox}>
                <p style={{ ...styles.label, color: "#6b7280", margin: "0 0 4px 0" }}>Shortened Link:</p>
                <a href={shortUrl} target="_blank" rel="noreferrer" style={styles.link}>{shortUrl}</a>
              </div>
            )}
          </section>

          {/* COLUMN 2: ANALYTICS */}
          <section style={styles.card}>
            <h2 style={styles.sectionTitle}>Track Performance</h2>
            <form onSubmit={handleFetchAnalytics}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Short Code Identifier</label>
                <input
                  type="text"
                  value={analyticsCode}
                  onChange={(e) => setAnalyticsCode(e.target.value)}
                  placeholder="Enter alias or generated code..."
                  style={styles.input}
                />
              </div>
              <button type="submit" style={styles.btnDark}>Check Metrics</button>
            </form>

            {analyticsError && <p style={styles.error}>{analyticsError}</p>}

            {analyticsData && (
              <div style={styles.analyticsBox}>
                <div>
                  <p style={{ ...styles.label, color: "#6b7280", margin: 0, fontSize: "11px", letterSpacing: "0.5px", textTransform: "uppercase" }}>Total Redirects</p>
                  <p style={styles.counter}>{analyticsData.total_clicks}</p>
                </div>
                <div>
                  <p style={{ ...styles.label, color: "#6b7280", margin: "0 0 8px 0", fontSize: "11px", letterSpacing: "0.5px", textTransform: "uppercase" }}>Activity Logs</p>
                  {analyticsData.click_history.length === 0 ? (
                    <p style={{ fontSize: "13px", color: "#9ca3af", fontStyle: "italic", margin: 0 }}>No dynamic tracking entries found.</p>
                  ) : (
                    <ul style={{ padding: 0, margin: 0 }}>
                      {analyticsData.click_history.map((click, index) => (
                        <li key={index} style={styles.logItem}>
                          <span style={{ color: "#111827", display: "block", fontSize: "13px", fontWeight: "500" }}>
                            {new Date(click.clicked_at).toLocaleString()}
                          </span>
                          <span style={{ color: "#6b7280", fontSize: "12px", wordBreak: "break-all" }}>
                            Agent: {click.device_signature || "Direct Traffic"}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            )}
          </section>

        </div>
      </div>
    </div>
  );
}