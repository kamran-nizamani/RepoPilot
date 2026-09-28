import { NextResponse } from "next/server";

function unifiedDiff(path:string, oldText:string, newText:string){
 const a=oldText.split("\n"), b=newText.split("\n");
 let start=0; while(start<a.length&&start<b.length&&a[start]===b[start]) start++;
 let endA=a.length-1,endB=b.length-1; while(endA>=start&&endB>=start&&a[endA]===b[endB]){endA--;endB--;}
 const oldPart=a.slice(start,endA+1), newPart=b.slice(start,endB+1);
 return `--- a/${path}\n+++ b/${path}\n@@ -${start+1},${oldPart.length} +${start+1},${newPart.length} @@\n${oldPart.map(x=>"-"+x).join("\n")}\n${newPart.map(x=>"+"+x).join("\n")}`;
}
export async function POST(req:Request){
 try{
  const body=await req.json(); const path=String(body.path||"").trim();
  const oldText=String(body.oldText??""); const newText=String(body.newText??"");
  if(!path||newText.length>200000) return NextResponse.json({error:"Invalid patch request."},{status:400});
  return NextResponse.json({path,diff:unifiedDiff(path,oldText,newText),requiresApproval:true});
 }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"Patch generation failed"},{status:500});}
}