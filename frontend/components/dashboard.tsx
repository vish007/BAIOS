"use client";

import { useState } from "react";
import type { CSSProperties } from "react";

import { runWorkflow } from "../lib/api";

const cardStyle: CSSProperties = {
  background: "white",
  borderRadius: 12,
  padding: 20,
  boxShadow: "0 3px 12px rgba(15,23,42,0.08)",
};

export default function Dashboard() {
  const [provider, setProvider] = useState<"llama_vision" | "openai" | "claude">("llama_vision");
  const [result, setResult] = useState<string>("Run a workflow to view explainable output.");

  const execute = async () => {
    const response = await runWorkflow({
      workflow_id: "trade-finance-lc-scrutiny",
      provider,
      input_payload: {
        trade_documents: ["invoice", "bill_of_lading", "packing_list"],
        contains_pii: true,
        pii_redacted: true,
      },
    });

    setResult(JSON.stringify(response, null, 2));
  };

  return (
    <main style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
      <h1>BAOS Cockpit</h1>
      <p>Enterprise OpenClaw-style orchestration with configurable model providers.</p>

      <section style={{ ...cardStyle, marginBottom: 16 }}>
        <h2>Model Routing</h2>
        <label htmlFor="provider">Inference Provider: </label>
        <select
          id="provider"
          value={provider}
          onChange={(e) => setProvider(e.target.value as "llama_vision" | "openai" | "claude")}
        >
          <option value="llama_vision">Llama Vision (private cloud)</option>
          <option value="openai">OpenAI</option>
          <option value="claude">Claude</option>
        </select>
        <button style={{ marginLeft: 12 }} onClick={execute}>
          Run Trade Workflow
        </button>
      </section>

      <section style={cardStyle}>
        <h2>Explainability Output</h2>
        <pre style={{ whiteSpace: "pre-wrap" }}>{result}</pre>
      </section>
    </main>
  );
}
