import { NextResponse } from "next/server";
export async function POST(req:Request){
 try{
  const {repoUrl=""}=await req.json(); const m=String(repoUrl).match(/^https?:\/\/github\.com\/([^/]+)\/([^/#?]+)(?:[#?].*)?$/i);
  if(!m)return NextResponse.json({error:"Use a public GitHub repository URL."},{status:400});
  const owner=m[1],repo=m[2].replace(/\.git$/,""),h={headers:{Accept:"application/vnd.github+json","User-Agent":"RepoPilot"}};
  const meta=await fetch(`https://api.github.com/repos/${owner}/${repo}`,h);if(!meta.ok)throw Error("Repository could not be read.");const info=await meta.json();
  const names=["package.json","requirements.txt","pyproject.toml","go.mod","Cargo.toml","pom.xml"];
  const result:any[]=[];
  for(const name of names){const r=await fetch(`https://raw.githubusercontent.com/${owner}/${repo}/${encodeURIComponent(info.default_branch)}/${name}`,h);if(!r.ok)continue;const text=await r.text();let count=0;if(name==="package.json"){try{const x=JSON.parse(text);count=Object.keys({...x.dependencies,...x.devDependencies,...x.peerDependencies}).length}catch{}}else count=text.split("\n").filter(x=>x.trim()&&!x.trim().startsWith("#")).length;result.push({file:name,count,preview:text.slice(0,5000)})}
  return NextResponse.json({repository:`${owner}/${repo}`,branch:info.default_branch,manifests:result,totalDeclared:result.reduce((n,x)=>n+x.count,0)});
 }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"Dependency scan failed"},{status:500})}
}