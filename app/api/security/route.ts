import { NextResponse } from "next/server";

const ignored=/(^|\\/)(node_modules|.git|.next|dist|build|coverage|vendor)(\\/|$)/;
const allowed=/\\.(ts|tsx|js|jsx|py|java|go|rs|php|rb|json|yml|yaml|env|ini|cfg|toml|sql)$/i;
const rules=[
  {id:"hardcoded-secret",severity:"high",re:/\b(api[_-]?key|secret|password|token)\s*[:=]\s*["'][^"']{8,}["']/i,message:"Possible hardcoded credential."},
  {id:"private-key",severity:"critical",re:/-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/i,message:"Private key material detected."},
  {id:"dangerous-eval",severity:"medium",re:/\beval\s*\(/,message:"Dynamic eval can execute untrusted input."},
  {id:"shell-exec",severity:"medium",re:/\b(?:child_process\.exec|os\.system|subprocess\.(?:run|Popen)|Runtime\.getRuntime\(\)\.exec)\b/,message:"Shell execution requires input validation."},
  {id:"sql-concat",severity:"high",re:/(SELECT|INSERT|UPDATE|DELETE)[^\n]{0,160}\+\s*[A-Za-z_$]/i,message:"Possible SQL string concatenation."}
];
export async function POST(req:Request){
 try{
  const {repoUrl=""}=await req.json();
  const m=String(repoUrl).match(/^https?:\/\/github\.com\/([^/]+)\/([^/#?]+)(?:[#?].*)?$/i);
  if(!m)return NextResponse.json({error:"Use a public GitHub repository URL."},{status:400});
  const owner=m[1],repo=m[2].replace(/\.git$/,""),h={headers:{Accept:"application/vnd.github+json","User-Agent":"RepoPilot"}};
  const meta=await fetch(`https://api.github.com/repos/${owner}/${repo}`,h); if(!meta.ok)throw Error("Repository could not be read.");
  const info=await meta.json(); const tr=await fetch(`https://api.github.com/repos/${owner}/${repo}/git/trees/${encodeURIComponent(info.default_branch)}?recursive=1`,h);
  if(!tr.ok)throw Error("Repository tree could not be read."); const tree=await tr.json();
  const files=(tree.tree||[]).filter((x:any)=>x.type==="blob"&&!ignored.test(x.path)&&allowed.test(x.path)).slice(0,120);
  const findings:any[]=[];
  await Promise.all(files.map(async(f:any)=>{try{const p=f.path.split("/").map(encodeURIComponent).join("/");const r=await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/${encodeURIComponent(info.default_branch)}/${p}`,h);if(!r.ok)return;const text=(await r.text()).slice(0,30000);for(const rule of rules){const lines=text.split("\n");lines.forEach((line,i)=>{if(rule.re.test(line)&&findings.length<100)findings.push({id:rule.id,severity:rule.severity,path:f.path,line:i+1,message:rule.message});});}}catch{}}));
  const order={critical:0,high:1,medium:2,low:3};findings.sort((a,b)=>(order[a.severity as keyof typeof order]??9)-(order[b.severity as keyof typeof order]??9));
  return NextResponse.json({repository:`${owner}/${repo}`,branch:info.default_branch,scanned:files.length,findings});
 }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"Security scan failed"},{status:500})}
}