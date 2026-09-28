import { NextResponse } from "next/server";
import { generateText } from "ai";

export async function POST(req: Request) {
  try {
    const { prompt, context = "" } = await req.json();
    if (!String(prompt || "").trim()) return NextResponse.json({error:"Enter a debugging question."},{status:400});
    if (!process.env.AI_GATEWAY_API_KEY) return NextResponse.json({error:"AI Gateway is not configured on this deployment."},{status:503});
    const result=await generateText({
      model:"anthropic/claude-sonnet-4.6",
      system:`You are RepoPilot, a senior software engineer. Analyze only the repository evidence provided. Do not claim to have executed code or changed files. Be precise and concise. Structure the response as Diagnosis, Evidence, Files involved, Minimal patch plan, Verification, Risks. Every mutation must remain human-approved.`,
      prompt:`Developer request:\n${String(prompt)}\n\nRepository evidence:\n${String(context).slice(0,50000)}`
    });
    return NextResponse.json({text:result.text});
  } catch(e){ return NextResponse.json({error:e instanceof Error?e.message:"AI generation failed"},{status:500}); }
}