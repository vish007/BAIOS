export type WorkflowRunPayload = {
  workflow_id: string;
  input_payload: Record<string, unknown>;
  provider?: "llama_vision" | "openai" | "claude";
};

const BASE_URL = process.env.NEXT_PUBLIC_BAOS_API_URL ?? "http://localhost:8000/api/v1";

export async function runWorkflow(payload: WorkflowRunPayload) {
  const token = process.env.NEXT_PUBLIC_DEV_JWT ?? "";
  const response = await fetch(`${BASE_URL}/workflow-runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Workflow run failed with status ${response.status}: ${body}`);
  }

  return response.json();
}
