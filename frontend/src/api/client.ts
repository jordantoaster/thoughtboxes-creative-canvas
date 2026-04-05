const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface UploadResponse {
  session_id: string;
}

export interface RunResponse {
  session_id: string;
  markdown: string;
}

export async function uploadTranscript(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/session/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail ?? `Upload failed (${res.status})`);
  }

  return res.json() as Promise<UploadResponse>;
}

export async function runPipeline(
  sessionId: string,
  steeringNotes: string
): Promise<RunResponse> {
  const res = await fetch(`${API_BASE}/session/${sessionId}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ steering_notes: steeringNotes }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail ?? `Run failed (${res.status})`);
  }

  return res.json() as Promise<RunResponse>;
}
