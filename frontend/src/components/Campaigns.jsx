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

export default function Campaigns({ segment = "High-Value Churn Risk" }) {
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [campaignData, setCampaignData] = useState(null);
  const [ablationData, setAblationData] = useState(null);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [ablationMode, setAblationMode] = useState(false);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://ai-marketing-saas-tp6d.onrender.com";

  // Simulated live agent thinking steps
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
    <div className="min-h-screen bg-[#080B11] text-slate-100 p-8 space-y-8 font-sans">
      {/* Top Banner / Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/[0.08]">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 animate-pulse" /> Autonomous Agent v2.4
            </span>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
              <ShieldCheck className="w-3 h-3" /> LLM Guardrail Armed
            </span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Agentic Retention Synthesizer
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Multi-stage autonomous pipeline translating XGBoost explainability to policy-grounded campaigns.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              setAblationMode(!ablationMode);
              if (!ablationData && !ablationMode) handleRunAblation();
            }}
            className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all border flex items-center gap-2 ${
              ablationMode 
                ? "bg-amber-500/20 text-amber-300 border-amber-500/30" 
                : "bg-white/[0.04] hover:bg-white/[0.08] text-slate-300 border-white/[0.08]"
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            {ablationMode ? "Exit Ablation Mode" : "Run RAG Ablation Benchmark"}
          </button>

          <button
            onClick={handleGenerate}
            disabled={loading}
            className="px-5 py-2.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-indigo-500 to-violet-600 hover:from-indigo-600 hover:to-violet-700 text-white shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <Cpu className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            {loading ? "Agent Reasoning..." : "Launch Agent Pipeline"}
          </button>
        </div>
      </div>

      {/* Real-Time Agent Execution Stepper */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {agentSteps.map((step) => {
          const isDone = activeStep > step.id || (activeStep === 4 && campaignData);
          const isCurrent = activeStep === step.id && loading;

          return (
            <div
              key={step.id}
              className={`p-4 rounded-xl border backdrop-blur-md transition-all duration-300 ${
                isCurrent
                  ? "bg-indigo-950/30 border-indigo-500/40 shadow-lg shadow-indigo-500/10"
                  : isDone
                  ? "bg-white/[0.03] border-emerald-500/30"
                  : "bg-white/[0.01] border-white/[0.05] opacity-50"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                  STAGE 0{step.id}
                </span>
                {isDone ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : isCurrent ? (
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-slate-600" />
                )}
              </div>
              <h4 className="text-sm font-semibold text-slate-200">{step.title}</h4>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">{step.desc}</p>
            </div>
          );
        })}
      </div>

      {/* Ablation Benchmark View */}
      {ablationMode && ablationData && (
        <div className="p-6 rounded-2xl bg-amber-950/20 border border-amber-500/30 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-amber-300 flex items-center gap-2">
              <Layers className="w-5 h-5" /> Viva Ablation Test: Ungrounded Gemini vs RAG-Grounded Agent
            </h3>
            <span className="text-xs bg-amber-500/10 text-amber-400 px-3 py-1 rounded-full border border-amber-500/20">
              Live Policy Guardrail Comparison
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Raw LLM */}
            <div className="p-5 rounded-xl bg-black/40 border border-red-500/20 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-red-400">Raw Gemini 1.5 (Zero Constraints)</h4>
                <span className="text-xs text-red-400 bg-red-950/40 px-2 py-0.5 rounded">Risk: Policy Breach</span>
              </div>
              <p className="text-xs text-slate-300 whitespace-pre-wrap font-mono leading-relaxed bg-black/30 p-3 rounded border border-white/[0.04]">
                {ablationData.raw_unconstrained_llm?.output}
              </p>
              <p className="text-xs text-red-300/80 italic">
                ⚠️ {ablationData.raw_unconstrained_llm?.violation_detected}
              </p>
            </div>

            {/* RAG Grounded */}
            <div className="p-5 rounded-xl bg-black/40 border border-emerald-500/20 space-y-2">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-emerald-400">RAG-Grounded Agent</h4>
                <span className="text-xs text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded">
                  Score: {ablationData.rag_grounded_agent?.compliance_score}/100
                </span>
              </div>
              <div className="text-xs text-slate-300 font-mono bg-black/30 p-3 rounded border border-white/[0.04] space-y-2">
                <div className="font-semibold text-indigo-300">
                  {ablationData.rag_grounded_agent?.output?.campaign_name}
                </div>
                <div>{ablationData.rag_grounded_agent?.output?.variants?.[0]?.body_copy}</div>
              </div>
              <p className="text-xs text-emerald-300/80">
                ✓ Guardrail Certified: Strictly adheres to corporate margin and discount limits.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Campaign Results */}
      {campaignData && (
        <div className="space-y-6">
          {/* Telemetry / Guardrail Certificate */}
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.08] backdrop-blur-xl flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="space-y-1">
              <span className="text-xs font-mono text-indigo-400 uppercase tracking-wider">
                Audit Pass ID #{campaignData.campaign_id}
              </span>
              <h3 className="text-xl font-bold text-white">
                {campaignData.campaign?.campaign_name || "Enterprise Retention Package"}
              </h3>
              <p className="text-xs text-slate-400">
                Targeted Audience: <span className="text-indigo-300 font-medium">{segment}</span> | Grounded in Vector Policy Base
              </p>
            </div>

            {/* Compliance Scores */}
            <div className="flex items-center gap-4">
              <div className="text-center px-4 py-2 rounded-xl bg-black/40 border border-emerald-500/20">
                <div className="text-2xl font-black text-emerald-400">
                  {campaignData.compliance_audit?.compliance_score}%
                </div>
                <div className="text-[10px] uppercase font-mono text-slate-400">Policy Match</div>
              </div>
              <div className="text-center px-4 py-2 rounded-xl bg-black/40 border border-indigo-500/20">
                <div className="text-2xl font-black text-indigo-400">
                  {campaignData.compliance_audit?.brand_safety_score}%
                </div>
                <div className="text-[10px] uppercase font-mono text-slate-400">Brand Safety</div>
              </div>
              <div className="text-center px-4 py-2 rounded-xl bg-black/40 border border-white/[0.08]">
                <div className="text-2xl font-black text-slate-200">
                  {campaignData.compliance_audit?.hallucination_penalty}%
                </div>
                <div className="text-[10px] uppercase font-mono text-slate-400">Hallucination</div>
              </div>
            </div>
          </div>

          {/* Generated Variants Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {campaignData.campaign?.variants?.map((v, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-white/[0.02] border border-white/[0.08] hover:border-white/[0.15] transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {v.variant_id}
                    </span>
                    <span className="text-xs font-mono text-slate-400">{v.channel}</span>
                  </div>

                  <h4 className="text-base font-bold text-white">{v.headline}</h4>
                  <div className="text-xs font-medium text-slate-300 bg-black/30 p-2.5 rounded border border-white/[0.04]">
                    <span className="text-slate-500">Subject:</span> {v.subject_line}
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">{v.body_copy}</p>
                </div>

                <div className="pt-4 border-t border-white/[0.06] flex items-center justify-between">
                  <button className="px-4 py-2 rounded-lg bg-indigo-600/20 text-indigo-300 text-xs font-semibold border border-indigo-500/30 flex items-center gap-1.5 hover:bg-indigo-600/30">
                    {v.call_to_action} <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => copyToClipboard(v.body_copy, idx)}
                    className="p-2 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-white transition-colors"
                  >
                    {copiedIndex === idx ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
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