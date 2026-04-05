import { useRef, useState } from "react";
import { uploadTranscript, runPipeline } from "../api/client";

interface Props {
  onResult: (markdown: string) => void;
  onLoading: (loading: boolean) => void;
  isLoading: boolean;
}

export function UploadForm({ onResult, onLoading, isLoading }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [steering, setSteering] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);

  async function resolveFile(): Promise<File> {
    const selected = fileRef.current?.files?.[0];
    if (selected) return selected;

    const res = await fetch("/demo-transcript.txt");
    if (!res.ok) throw new Error("Could not load demo transcript.");
    const blob = await res.blob();
    return new File([blob], "demo-transcript.txt", { type: "text/plain" });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    try {
      onLoading(true);
      const file = await resolveFile();
      if (!fileRef.current?.files?.[0]) {
        setFileName("demo-transcript.txt (demo)");
      }
      const { session_id } = await uploadTranscript(file);
      const { markdown } = await runPipeline(session_id, steering);
      onResult(markdown);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      onLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="upload-form">
      <div className="field">
        <label htmlFor="transcript-file">Transcript (.txt) — optional, uses demo if omitted</label>
        <div className="file-row">
          <input
            id="transcript-file"
            ref={fileRef}
            type="file"
            accept=".txt,text/plain"
            disabled={isLoading}
            onChange={(e) => setFileName(e.target.files?.[0]?.name ?? null)}
          />
          {fileName && <span className="file-name">{fileName}</span>}
        </div>
      </div>

      <div className="field">
        <label htmlFor="steering">Steering notes (optional)</label>
        <textarea
          id="steering"
          value={steering}
          onChange={(e) => setSteering(e.target.value)}
          placeholder="e.g. Focus on the sustainability angle. Avoid anything in the luxury space."
          rows={3}
          disabled={isLoading}
        />
      </div>

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={isLoading}>
        {isLoading ? "Running pipeline…" : "Run"}
      </button>
    </form>
  );
}
