import { useState } from "react";
import { UploadForm } from "./components/UploadForm";
import { MarkdownOutput } from "./components/MarkdownOutput";
import "./App.css";

function App() {
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Thought Boxes</h1>
        <p className="subtitle">Creative Meeting Canvas</p>
      </header>

      <main className="app-main">
        <section className="input-section">
          <UploadForm
            onResult={setMarkdown}
            onLoading={setIsLoading}
            isLoading={isLoading}
          />
        </section>

        <section className="output-section">
          <MarkdownOutput markdown={markdown} isLoading={isLoading} />
        </section>
      </main>
    </div>
  );
}

export default App;
