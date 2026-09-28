import { NextResponse } from "next/server";

const GEMINI_MODEL = "gemini-3.5-flash";

type GeminiResponse = {
  candidates?: Array<{
    content?: { parts?: Array<{ text?: string }> };
  }>;
  error?: { message?: string; status?: string };
};

export async function POST(req: Request) {
  try {
    const { prompt, context = "" } = await req.json();
    const question = String(prompt || "").trim();

    if (!question) return NextResponse.json({ error: "Enter a debugging question." }, { status: 400 });

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return NextResponse.json({
        error: "Gemini is not configured. Add GEMINI_API_KEY to the Vercel environment variables.",
      }, { status: 503 });
    }

    const systemInstruction = `You are RepoPilot, a senior software engineer and repository debugging agent.

Analyze only the repository evidence supplied in the request. Never claim that you executed code, changed files, ran tests, or opened a pull request unless the request explicitly provides evidence of that action.

Your job is to identify likely causes, cite concrete evidence from the supplied repository context, and propose the smallest safe next change.

Structure every answer exactly with these sections:
1. Diagnosis
2. Evidence
3. Files involved
4. Minimal patch plan
5. Verification
6. Risks

Keep mutations human-approved. Prefer minimal, reversible changes over broad refactors.`;

    const userPrompt = "Developer request:\n" + question +
      "\n\nRepository evidence:\n" + String(context).slice(0, 50000);

    const response = await fetch(
      "https://generativelanguage.googleapis.com/v1beta/models/" + GEMINI_MODEL + ":generateContent",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": apiKey,
        },
        body: JSON.stringify({
          system_instruction: { parts: [{ text: systemInstruction }] },
          contents: [{ role: "user", parts: [{ text: userPrompt }] }],
          generationConfig: { temperature: 0.2, maxOutputTokens: 3000 },
        }),
      }
    );

    const data = (await response.json()) as GeminiResponse;
    if (!response.ok) {
      return NextResponse.json({
        error: data.error?.message || `Gemini API request failed with status ${response.status}.`,
      }, { status: 502 });
    }

    const text = data.candidates?.[0]?.content?.parts?.map((part) => part.text || "").join("").trim();
    if (!text) return NextResponse.json({ error: "Gemini returned an empty response." }, { status: 502 });

    return NextResponse.json({ text, model: GEMINI_MODEL, provider: "Google Gemini API" });
  } catch (error) {
    return NextResponse.json({
      error: error instanceof Error ? error.message : "Gemini generation failed.",
    }, { status: 500 });
  }
}
