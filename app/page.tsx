"use client";

import { useState } from "react";

type Result = {
  repository: string; branch: string; description: string; stars: number;
  files: number; languages: Record<string, number>; sizeKb: number; demoMode: boolean;
};

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/kamran-nizamani/RepoPilot");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    setLoading(true); setError("");
    try {
      const res = await fetch("/api/analyze", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({repoUrl}) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Analysis failed");
      setResult(data);
    } catch (e) { setError(e instanceof Error ? e.message : "Something went wrong"); }
    finally { setLoading(false); }
  }

  return (
    <main className="shell">
      <nav><div className="brand"><span className="mark">R</span> RepoPilot</div><span className="badge">Hosted Demo</span></nav>
      <section className="hero">
        <p className="eyebrow">OPEN-SOURCE AI CODING AGENT</p>
        <h1>Understand your repository<br/><span>before you change it.</span></h1>
        <p className="sub">Analyze a public GitHub repository and turn its structure into actionable engineering context.</p>
        <div className="search">
          <input value={repoUrl} onChange={e=>setRepoUrl(e.target.value)} onKeyDown={e=>e.key==="Enter"&&analyze()} placeholder="https://github.com/owner/repository" />
          <button onClick={analyze} disabled={loading}>{loading ? "Analyzing…" : "Analyze repo →"}</button>
        </div>
        {error && <div className="error">{error}</div>}
      </section>

      {result && <section className="workspace">
        <div className="repohead"><div><div className="muted">REPOSITORY</div><h2>{result.repository}</h2><p>{result.description}</p></div><span className="branch">⎇ {result.branch}</span></div>
        <div className="cards">
          <Card label="Files" value={result.files.toString()} />
          <Card label="GitHub stars" value={result.stars.toString()} />
          <Card label="Repository size" value={result.sizeKb + " KB"} />
          <Card label="Mode" value="Read-only" />
        </div>
        <div className="panel"><div className="paneltitle">Language distribution</div>
          {Object.entries(result.languages).sort((a,b)=>b[1]-a[1]).map(([name,count])=><div className="lang" key={name}><span>{name}</span><b>{count}</b><div className="bar"><i style={{width: `${Math.min(100, Math.max(4, count/result.files*100))}%`}} /></div></div>)}
        </div>
        <div className="notice">Hosted demo is intentionally read-only. File writes, shell commands, commits and pull requests remain approval-gated in the local RepoPilot agent.</div>
      </section>}

      <footer>RepoPilot · AI proposes, humans approve.</footer>
    </main>
  );
}

function Card({label,value}:{label:string,value:string}) {
  return <div className="card"><span>{label}</span><strong>{value}</strong></div>;
}
