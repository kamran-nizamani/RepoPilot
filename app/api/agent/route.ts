import { NextResponse } from "next/server";

const MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite"] as const;
const MAX_RETRIES = 2;

type GeminiResponse = {
  candidates?: Array<{
    content?: { parts?: Array<{ text?: string }> };
  }>;
  error?: { message?: string; status?: string };
};

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function generate(model: string, apiKey: string, body: object) {
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": apiKey,
        },
        body: JSON.stringify(body),
      }
    );

    const data = (await response.json()) as GeminiResponse;

    if (response.ok) {
      return { response, data };
    }

    const transient = response.status === 429 || response.status === 503 || response.status >= 500;
    if (!transient || attempt === MAX_RETRIES) {
      return { response, data };
    }

    // Google recommends exponential backoff for transient 429/5xx errors.
    await sleep(1000 * 2 ** attempt + Math.floor(Math.random() * 500));
  }

  throw new Error("Gemini request failed after retries.");
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const question = String(body?.prompt || "").trim();
    const context = String(body?.context || "");

    if (!question) {
      return NextResponse.json({ error: "Enter a debugging question." }, { status: 400 });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: "Gemini is not configured. Add GEMINI_API_KEY to the Vercel environment variables." },
        { status: 503 }
      );
    }

    const systemInstruction = `You are RepoPilot, a senior software engineer and repository debugging agent.

Analyze only the repository evidence supplied in the request. Never claim that you executed code, changed files, ran tests, or opened a pull request unless the request explicitly provides evidence of that action.

Identify likely causes, cite concrete evidence from the supplied repository context, and propose the smallest safe next change.

Structure every answer exactly with these sections:
1. Diagnosis
2. Evidence
3. Files involved
4. Minimal patch plan
5. Verification
6. Risks

Keep mutations human-approved. Prefer minimal, reversible changes over broad refactors.`;

    const userPrompt =
      "Developer request:\n" +
      question +
      "\n\nRepository evidence:\n" +
      context.slice(0, 50000);

    const requestBody = {
      system_instruction: { parts: [{ text: systemInstruction }] },
      contents: [{ role: "user", parts: [{ text: userPrompt }] }],
      generationConfig: { maxOutputTokens: 3000 },
    };

    let lastMessage = "Gemini is temporarily unavailable.";

    for (const model of MODELS) {
      const { response, data } = await generate(model, apiKey, requestBody);

      if (!response.ok) {
        lastMessage = data.error?.message || `Gemini request failed with status ${response.status}.`;
        continue;
      }

      const text = data.candidates?.[0]?.content?.parts
        ?.map((part) => part.text || "")
        .join("")
        .trim();

      if (!text) {
        lastMessage = "Gemini returned an empty response.";
        continue;
      }

      return NextResponse.json({
        text,
        model,
        provider: "Google Gemini API",
      });
    }

    return NextResponse.json(
      {
        error:
          "Gemini is temporarily busy. RepoPilot retried the primary model and switched to a fallback model, but both were unavailable. Please try again shortly.",
        detail: lastMessage,
      },
      { status: 503 }
    );
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Gemini generation failed." },
      { status: 500 }
    );
  }
}
