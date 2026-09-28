import { NextResponse } from "next/server";

const ignored = /(^|\\/)(node_modules|.git|.next|dist|build|coverage|vendor)(\\/|$)/;
const allowed = /\\.(ts|tsx|js|jsx|py|java|cpp|c|go|rs|json|md|css|html|yml|yaml)$/i;

export async function POST(req: Request) {
  try {
    const { repoUrl, query = "" } = await req.json();
    const m = String(repoUrl || "").match(/^https?:\\/\\/github\\.com\\/([^/]+)\\/([^/#?]+)(?:[#?].*)?$/i);
    if (!m) return NextResponse.json({ error: "Use a public GitHub repository URL." }, { status: 400 });
    const owner=m[1], repo=m[2].replace(/\\.git$/,"");
    const base={headers:{"Accept":"application/vnd.github+json","User-Agent":"RepoPilot"}};
    const meta=await fetch(`https://api.github.com/repos/${owner}/${repo}`,base);
    if(!meta.ok) return NextResponse.json({error:"GitHub repository could not be read."},{status:meta.status});
    const info=await meta.json();
    const treeRes=await fetch(`https://api.github.com/repos/${owner}/${repo}/git/trees/${info.default_branch}?recursive=1`,base);
    if(!treeRes.ok) return NextResponse.json({error:"Repository tree could not be read."},{status:treeRes.status});
    const tree=await treeRes.json();
    const files=(tree.tree||[]).filter((x:any)=>x.type==="blob"&&allowed.test(x.path)&&!ignored.test(x.path)).slice(0,250);
    const q=String(query).toLowerCase().trim();
    const ranked=files.map((f:any)=>{
      const path=f.path.toLowerCase();
      let score=0;
      if(q){ for(const term of q.split(/\\s+/).filter(Boolean)) if(path.includes(term)) score+=4; }
      if(/(readme|package.json|pyproject|requirements|dockerfile|next.config|vite.config|tsconfig)/i.test(path)) score+=3;
      if(/(test|spec|api|route|page|component|server|src)/i.test(path)) score+=1;
      return {...f,score};
    }).sort((a:any,b:any)=>b.score-a.score).slice(0,12);
    const snippets=[];
    for(const f of ranked){
      try{
        const r=await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/${info.default_branch}/${f.path}`,base);
        if(!r.ok) continue;
        const text=await r.text();
        if(text.length>12000) snippets.push({path:f.path,content:text.slice(0,12000),truncated:true});
        else snippets.push({path:f.path,content:text,truncated:false});
      }catch{}
    }
    return NextResponse.json({repository:`${owner}/${repo}`,branch:info.default_branch,query,files:snippets});
  } catch(e) { return NextResponse.json({error:e instanceof Error?e.message:"Context retrieval failed"},{status:500}); }
}