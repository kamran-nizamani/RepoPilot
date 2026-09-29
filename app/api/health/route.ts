import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    status: "ok",
    service: "repopilot-web",
    mode: "hosted",
    configuration: {
      gemini: Boolean(process.env.GEMINI_API_KEY),
      githubWrite: Boolean(process.env.GITHUB_TOKEN),
    },
  });
}
