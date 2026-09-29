import { NextResponse } from "next/server";

const MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite"] as const;
const MAX_RETRIES = 2;

type GeminiResponse = {
  candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
  error?: { message?: string; status?: string };
};

function sleep(ms:number){ return new Promise(resolve=>setTimeout(resolve,ms)); }

async function generate(model:string, apiKey:string, body:object){
  for(let attempt=0;attempt<=MAX_RETRIES;attempt++){
    const response=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,{
      method:"POST",
      headers:{"Content-Type":"application/json","x-goog-api-key":apiKey},
      body:JSON.stringify(body),
    });
    const data=(await response.json()) as GeminiResponse;
    if(response.ok) return {response,data};
    const transient=response.status===429||response.status===503||response.status>=500;
    if(!transient||attempt===MAX_RETRIES) return {response,data};
    await sleep(1000*2**attempt+Math.floor(Math.random()*500));
  }
  throw new Error("Gemini request failed after retries.");
}

function extractJson(text:string){
  const cleaned=text.trim().replace(/^\`\`\`(?:json)?\s*/i,"").replace(/\s*\`\`\`$/,"");
  const start=cleaned.indexOf("{"), end=cleaned.lastIndexOf("}");
  if(start<0||end<start) throw new Error("AI did not return a structured patch.");
  return JSON.parse(cleaned.slice(start,end+1));
}

export async function POST(req:Request){
  try{
    const body=await req.json();
    const question=String(body?.prompt||"").trim();
    const context=String(body?.context||"");
    const focusPath=String(body?.focusPath||"").trim();
    if(!question) return NextResponse.json({error:"Enter a debugging question."},{status:400});
    const apiKey=process.env.GEMINI_API_KEY;
    if(!apiKey) return NextResponse.json({error:"Gemini is not configured. Add GEMINI_API_KEY to Vercel environment variables."},{status:503});

    const systemInstruction=`You are RepoPilot's controlled patch-planning agent.
Analyze ONLY the supplied repository evidence. Never claim you executed code or changed files.
Return ONLY valid JSON, with this exact shape:
{
  "summary": "short diagnosis",
  "verification": ["step 1"],
  "risks": ["risk"],
  "patches": [
    {"path":"existing/repository/file.ts","oldText":"exact existing text","newText":"replacement text"}
  ]
}
Rules:
- If a focus file is supplied, inspect it first and use it when the evidence supports a concrete defect.
- patches must contain ONLY files and exact oldText supported by the supplied evidence.
- If evidence is insufficient for a safe exact patch, return an empty patches array and explain why in risks.
- Prefer one concrete reproducible defect over a broad list of speculative concerns.
- Keep changes minimal and reversible.
- Never include secrets, tokens, passwords, or environment values.
- Do not invent file contents.`;

    const requestBody={
      system_instruction:{parts:[{text:systemInstruction}]},
      contents:[{role:"user",parts:[{text:"Developer request:\n"+question+"\n\nFocus file (if supplied): "+focusPath+"\n\nRepository evidence:\n"+context.slice(0,65000)}]}],
      generationConfig:{maxOutputTokens:4000,responseMimeType:"application/json"},
    };

    let lastMessage="Gemini is temporarily unavailable.";
    for(const model of MODELS){
      const {response,data}=await generate(model,apiKey,requestBody);
      if(!response.ok){lastMessage=data.error?.message||`Gemini request failed with status ${response.status}.`;continue;}
      const text=data.candidates?.[0]?.content?.parts?.map(p=>p.text||"").join("").trim();
      if(!text){lastMessage="Gemini returned an empty response.";continue;}
      try{
        const proposal=extractJson(text);
        if(!Array.isArray(proposal.patches)) throw new Error("Invalid patch proposal.");
        return NextResponse.json({proposal,model,provider:"Google Gemini API"});
      }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"Invalid AI patch response."},{status:502});}
    }
    return NextResponse.json({error:"Gemini is temporarily busy. RepoPilot retried the primary model and switched to a fallback model, but both were unavailable.",detail:lastMessage},{status:503});
  }catch(e){return NextResponse.json({error:e instanceof Error?e.message:"Patch proposal failed"},{status:500});}
}