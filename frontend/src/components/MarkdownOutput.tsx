import ReactMarkdown from "react-markdown";

interface Props {
  markdown: string | null;
  isLoading: boolean;
}

export function MarkdownOutput({ markdown, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="output-panel loading">
        <div className="spinner" aria-label="Processing" />
        <p>Running pipeline — this may take a minute while the model thinks…</p>
      </div>
    );
  }

  if (!markdown) {
    return (
      <div className="output-panel empty">
        <p>Upload a transcript and click <strong>Run</strong> to generate your creative canvas.</p>
      </div>
    );
  }

  return (
    <div className="output-panel result">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
}
