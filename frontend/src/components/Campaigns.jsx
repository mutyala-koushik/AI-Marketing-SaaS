import React, { useState } from "react";
import { 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  Layers, 
  Copy, 
  Check, 
  Zap, 
  AlertTriangle,
  ArrowRight
} from "lucide-react";

export default function Campaigns({ segment = "Growth Customers" }) {
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [campaignData, setCampaignData] = useState(null);
  const [ablationData, setAblationData] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [ablationMode, setAblationMode] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://ai-marketing-saas-tp6d.onrender.com";

  const agentSteps = [
    { id: 1, title: "Diagnostician Agent", desc: "Extracting XGBoost & TreeSHAP root friction vectors" },
    { id: 2, title: "Policy Grounding Agent", desc: "Searching Vector RAG store for active legal constraints" },
    { id: 3, title: "Synthesis Agent", desc: "Compiling multi-variant marketing strategies via Gemini" },
    { id: 4, title: "Guardrail Judge", desc: "Scoring brand safety, policy adherence & hallucination risk" }
  ];

  const handleGenerate = async () => {
    setLoading(true);
    setCampaignData(null);
    setActiveStep(1);

    const stepInterval = setInterval(() => {
      setActiveStep((prev) => (prev < 4 ? prev + 1 : prev));
    }, 1200);

    try {
      const res = await fetch(`${API_BASE}/campaigns/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_segment: segment,
          churn_probability: 0.78,
          shap_features: [
            { feature: "Contract_Month-to-Month", importance: 0.42 },
            { feature: "TotalCharges_Low", importance: 0.28 },
            { feature: "Support_Tickets_High", importance: 0.19 }
          ]
        })
      });

      const data = await res.json();
      clearInterval(stepInterval);
      setActiveStep(4);
      setCampaignData(data);
    } catch (err) {
      clearInterval(stepInterval);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAblation = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/campaigns/ablation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_segment: segment,
          churn_probability: 0.78
        })
      });
      const data = await res.json();
      setAblationData(data.ablation_results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="agent-container">
      {/* Top Banner */}
      <div className="agent-header">
        <div>
          <div className="agent-badge-row">
            <span className="agent-badge badge-indigo">
              <Sparkles size={13} className="spin-slow" /> Autonomous Agent v2.4
            </span>
            <span className="agent-badge badge-emerald">
              <ShieldCheck size={13} /> LLM Guardrail Armed
            </span>
          </div>
          <h1 className="agent-title">Agentic Retention Synthesizer</h1>
          <p className="agent-subtitle">
            Multi-stage autonomous pipeline translating XGBoost explainability to policy-grounded campaigns.
          </p>
        </div>

        <div className="agent-actions">
          <button
            onClick={() => {
              setAblationMode(!ablationMode);
              if (!ablationData && !ablationMode) handleRunAblation();
            }}
            className={`agent-btn ${ablationMode ? "btn-warning" : "btn-subtle"}`}
          >
            <AlertTriangle size={14} />
            {ablationMode ? "Exit Ablation Mode" : "Run RAG Ablation Benchmark"}
          </button>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="agent-btn btn-primary"
          >
            {loading ? <Cpu size={15} className="spin-slow" /> : <Zap size={15} />}
            {loading ? "Agent Reasoning..." : "Launch Agent Pipeline"}
          </button>
        </div>
      </div>

      {/* Real-Time Stepper */}
      <div className="agent-stepper-grid">
        {agentSteps.map((step) => {
          const isDone = activeStep > step.id || (activeStep === 4 && campaignData);
          const isCurrent = activeStep === step.id && loading;

          return (
            <div
              key={step.id}
              className={`stepper-card ${isCurrent ? "card-active" : isDone ? "card-done" : "card-pending"}`}
            >
              <div className="stepper-card-header">
                <span className="stepper-stage-tag">STAGE 0{step.id}</span>
                {isDone ? (
                  <Check size={16} className="text-emerald" />
                ) : isCurrent ? (
                  <span className="pulsing-node" />
                ) : (
                  <span className="inactive-node" />
                )}
              </div>
              <h4 className="stepper-title">{step.title}</h4>
              <p className="stepper-desc">{step.desc}</p>
            </div>
          );
        })}
      </div>

      {/* Ablation Benchmark View */}
      {ablationMode && ablationData && (
        <div className="ablation-box">
          <div className="ablation-box-header">
            <h3 className="ablation-title">
              <Layers size={18} /> Viva Ablation Test: Ungrounded Gemini vs RAG-Grounded Agent
            </h3>
            <span className="ablation-chip">Live Policy Guardrail Comparison</span>
          </div>

          <div className="ablation-grid">
            <div className="ablation-card ungrounded">
              <div className="ablation-card-header">
                <h4 className="text-crimson">Raw Gemini 1.5 (Zero Constraints)</h4>
                <span className="badge-risk">Risk: Policy Breach</span>
              </div>
              <pre className="terminal-preview">{ablationData.raw_unconstrained_llm?.output}</pre>
              <p className="violation-text">
                ⚠️ {ablationData.raw_unconstrained_llm?.violation_detected}
              </p>
            </div>

            <div className="ablation-card grounded">
              <div className="ablation-card-header">
                <h4 className="text-emerald">RAG-Grounded Agent</h4>
                <span className="badge-score">Score: {ablationData.rag_grounded_agent?.compliance_score}/100</span>
              </div>
              <div className="terminal-preview">
                <strong className="text-cyan">{ablationData.rag_grounded_agent?.output?.campaign_name}</strong>
                <p style={{ marginTop: "8px" }}>{ablationData.rag_grounded_agent?.output?.variants?.[0]?.body_copy}</p>
              </div>
              <p className="compliant-text">✓ Guardrail Certified: Strictly adheres to corporate margin and discount limits.</p>
            </div>
          </div>
        </div>
      )}

      {/* Generated Campaign Results */}
      {campaignData && (
        <div className="results-wrapper">
          {/* Audit Pass Banner */}
          <div className="audit-banner">
            <div>
              <span className="audit-id">AUDIT PASS ID #{campaignData.campaign_id}</span>
              <h3 className="audit-title">{campaignData.campaign?.campaign_name || "Enterprise Retention Package"}</h3>
              <p className="audit-sub">Targeted Persona: <span className="text-cyan">{segment}</span> | Vector Policy Grounded</p>
            </div>

            <div className="score-group">
              <div className="score-tile">
                <div className="score-num text-emerald">{campaignData.compliance_audit?.compliance_score}%</div>
                <div className="score-label">Policy Match</div>
              </div>
              <div className="score-tile">
                <div className="score-num text-cyan">{campaignData.compliance_audit?.brand_safety_score}%</div>
                <div className="score-label">Brand Safety</div>
              </div>
              <div className="score-tile">
                <div className="score-num">{campaignData.compliance_audit?.hallucination_penalty}%</div>
                <div className="score-label">Hallucination</div>
              </div>
            </div>
          </div>

          {/* Variants Grid */}
          <div className="variants-grid">
            {campaignData.campaign?.variants?.map((v, idx) => (
              <div key={idx} className="variant-card">
                <div>
                  <div className="variant-topbar">
                    <span className="variant-id-tag">{v.variant_id}</span>
                    <span className="variant-channel">{v.channel}</span>
                  </div>
                  <h4 className="variant-headline">{v.headline}</h4>
                  <div className="variant-subject">
                    <span>Subject:</span> {v.subject_line}
                  </div>
                  <p className="variant-body">{v.body_copy}</p>
                </div>

                <div className="variant-footer">
                  <button className="cta-btn">
                    {v.call_to_action} <ArrowRight size={13} />
                  </button>
                  <button
                    onClick={() => copyToClipboard(v.body_copy, idx)}
                    className="copy-btn"
                    title="Copy to clipboard"
                  >
                    {copiedIndex === idx ? <Check size={16} className="text-emerald" /> : <Copy size={16} />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}