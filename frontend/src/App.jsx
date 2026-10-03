import { useEffect, useState } from 'react';

const defaultTx = {
  account_id: 'acct_1042',
  timestamp: '2024-08-17 03:20:00',
  amount: 1480.0,
  merchant: 'Luxury Retailer',
  merchant_city: 'Paris',
  merchant_country: 'FR',
  channel: 'online',
  currency: 'USD',
};

async function analyzeTransaction(payload) {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'Analysis request failed');
  }

  return response.json();
}

export default function App() {
  const [formData, setFormData] = useState(defaultTx);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const runAnalysis = async (payload = formData) => {
    setLoading(true);
    setError('');

    try {
      const result = await analyzeTransaction(payload);
      setAnalysis(result);
    } catch (err) {
      setError(err.message || 'Something went wrong while analyzing this transaction.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis(defaultTx);
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'amount' ? Number(value) : value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    runAnalysis(formData);
  };

  return (
    <div className="page-shell">
      <header className="topbar">
        <div className="brand">🛡️ Risk Intelligence Console</div>
      </header>

      <main className="dashboard">
        <section className="panel form-panel">
          <h2>Transaction Parameters</h2>

          <form onSubmit={handleSubmit} className="transaction-form">
            <label>
              Account ID
              <input name="account_id" value={formData.account_id} onChange={handleChange} />
            </label>

            <label>
              Timestamp
              <input name="timestamp" value={formData.timestamp} onChange={handleChange} />
            </label>

            <label>
              Amount (USD)
              <input type="number" name="amount" value={formData.amount} onChange={handleChange} step="10" />
            </label>

            <label>
              Merchant
              <input name="merchant" value={formData.merchant} onChange={handleChange} />
            </label>

            <label>
              Merchant City
              <input name="merchant_city" value={formData.merchant_city} onChange={handleChange} />
            </label>

            <label>
              Merchant Country
              <input name="merchant_country" value={formData.merchant_country} onChange={handleChange} />
            </label>

            <label>
              Channel
              <select name="channel" value={formData.channel} onChange={handleChange}>
                <option value="online">online</option>
                <option value="pos">pos</option>
                <option value="atm">atm</option>
              </select>
            </label>

            <label>
              Currency
              <input name="currency" value={formData.currency} onChange={handleChange} />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? 'Running Analysis...' : 'Execute Risk Audit Pipeline'}
            </button>
          </form>
        </section>

        <section className="panel results-panel">
          <h2>Analysis & Intelligence Outputs</h2>

          {error && <div className="error-box">{error}</div>}

          {analysis ? (
            <>
              <div className="result-header">
                <span className="label">Verdict</span>
                <span className={`badge ${analysis.risk_score >= 80 ? 'high' : analysis.risk_score >= 60 ? 'medium' : 'low'}`}>
                  {analysis.verdict}
                </span>
              </div>

              <div className="metrics-grid">
                <div className="metric-card">
                  <span className="metric-label">Risk Score</span>
                  <strong>{analysis.risk_score}/100</strong>
                </div>
                <div className="metric-card">
                  <span className="metric-label">Average Spend</span>
                  <strong>${Number(analysis.average_spend || 0).toFixed(2)}</strong>
                </div>
                <div className="metric-card">
                  <span className="metric-label">Home City</span>
                  <strong>{analysis.home_city}</strong>
                </div>
              </div>

              <div className="section-block">
                <h3>Recommended Action</h3>
                <div className="info-box">{analysis.recommended_action}</div>
              </div>

              <div className="section-block">
                <h3>AI Reasoning</h3>
                <ul>
                  {Array.isArray(analysis.reasoning)
                    ? analysis.reasoning.map((item, index) => <li key={index}>{item}</li>)
                    : <li>{analysis.reasoning}</li>}
                </ul>
              </div>

              <div className="section-block">
                <h3>Anomaly Signals</h3>
                <ul>
                  {analysis.anomalies.map((item, index) => <li key={index}>{item}</li>)}
                </ul>
              </div>

              <div className="section-block">
                <h3>Relevant Context</h3>
                <ul>
                  {analysis.retrieved_context && analysis.retrieved_context.length > 0 ? (
                    analysis.retrieved_context.map((item, index) => <li key={index}>{item}</li>)
                  ) : (
                    <li>No customer context available.</li>
                  )}
                </ul>
              </div>

              <div className="section-block">
                <h3>Transaction Snapshot</h3>
                <pre>{JSON.stringify(analysis.transaction, null, 2)}</pre>
              </div>

              <div className="confidence-row">
                Model confidence: <strong>{Number(analysis.confidence || 0).toFixed(2)}</strong>
              </div>
            </>
          ) : (
            <div className="empty-state">Waiting for analysis...</div>
          )}
        </section>
      </main>
    </div>
  );
}
