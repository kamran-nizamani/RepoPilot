"use client";
import {useState} from "react";
import Link from "next/link";

export default function Agent(){
 const [repoUrl,setRepoUrl]=useState("https://github.com/kamran-nizamani/RepoPilot");
 const [query,setQuery]=useState("production error, API route, Next.js");
 const [prompt,setPrompt]=useState("Find the most likely production issue and give me a minimal safe fix plan.");
 const [context,setContext]=useState(""); const [answer,setAnswer]=useState(""); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
 async function run(){
  setBusy(true);setError("");setAnswer("");
  try{
   const cr=await fetch("/api/context",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({repoUrl,query})});
   const cd=await cr.json(); if(!cr.ok) throw Error(cd.error); setContext(JSON.stringify(cd,null,2));
   const ar=await fetch("/api/agent",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({prompt,context:JSON.stringify(cd)} )});
   const ad=await ar.json(); if(!ar.ok) throw Error(ad.error); setAnswer(ad.text);
  }catch(e){setError(e instanceof Error?e.message:"Agent failed")}finally{setBusy(false)}
 }
 return <div className="shell"><nav className="nav"><Link href="/" className="brand"><span className="logo">R</span>RepoPilot</Link><div className="navlinks"><Link href="/dashboard">Workspace</Link><Link href="/dashboard/issues">Issues</Link><Link href="/dashboard/runs">Runs</Link></div><span className="pill">AI + human approval</span></nav>
 <main className="workspace"><aside className="side"><div className="sideTitle">Agent</div><div className="sideItem active">Debugging</div><div className="sideItem">Context retrieval</div><div className="sideItem">Patch planning</div><div className="sideItem">Approval gate</div></aside>
 <section className="content"><div className="eyebrow">CODE INTELLIGENCE</div><h1>Debug a real repository</h1><p className="muted">RepoPilot retrieves relevant source context, then asks the AI to diagnose and plan. It does not write to GitHub.</p>
 <div className="two"><div className="panel"><h3>Repository</h3><input className="agentinput" value={repoUrl} onChange={e=>setRepoUrl(e.target.value)}/><input className="agentinput" value={query} onChange={e=>setQuery(e.target.value)}/><textarea className="agentbox" rows={5} value={prompt} onChange={e=>setPrompt(e.target.value)}/><button className="btn" onClick={run} disabled={busy}>{busy?"Analyzing…":"Analyze + debug →"}</button></div><div className="panel"><h3>Safety</h3><div className="rowline"><span>Read public source</span><b className="good">ON</b></div><div className="rowline"><span>Generate diagnosis</span><b className="good">ON</b></div><div className="rowline"><span>Write files</span><b className="warn">OFF</b></div><div className="rowline"><span>Git push / merge</span><b className="warn">APPROVAL</b></div></div></div>
 {error&&<div className="panel error">{error}</div>}
 {answer&&<div className="panel"><h3>Agent diagnosis</h3><pre className="code">{answer}</pre></div>}
 {context&&<details className="panel"><summary>Retrieved context</summary><pre className="code">{context}</pre></details>}
 </section></main></div>
}