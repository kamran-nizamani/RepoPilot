import { NextResponse } from "next/server";

const ignored = new Set([".git", "node_modules", ".next", "dist", "build", "__pycache__"]);
const languageMap: Record<string, string> = {
  ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript",
  ".tsx": "TypeScript", ".java": "Java", ".cpp": "C++", ".c": "C",
  ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
  ".html": "HTML", ".css": "CSS", ".md": "Markdown"
};

function parseRepo(value: string) {
  const url = value.trim().replace(/\.git$/, "").replace(/\/$/, "");
  const match = url.match(/^https?:\/\/(?:www\.)?github\.com\/([^/]+)\/([^/]+)$/);
  if (!match) throw new Error("Enter a public GitHub repository URL like https://github.com/owner/repo");
  return { owner: match[1], repo: match[2] };
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { owner, repo } = parseRepo(body.repoUrl || "");
    const headers = { Accept: "application/vnd.github+json", "User-Agent": "RepoPilot-Vercel-Demo" };

    const metaRes = await fetch(`https://api.github.com/repos/${owner}/${repo}`, { headers, cache: "no-store" });
    if (!metaRes.ok) throw new Error("GitHub repository could not be read. Make sure it is public.");
    const meta = await metaRes.json();

    const treeRes = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/git/trees/${meta.default_branch}?recursive=1`,
      { headers, cache: "no-store" }
    );
    if (!treeRes.ok) throw new Error("Could not read repository tree.");
    const tree = await treeRes.json();

    const files = (tree.tree || []).filter((item: any) => item.type === "blob" && !item.path.split("/").some((p: string) => ignored.has(p)));
    const languages: Record<string, number> = {};
    for (const file of files) {
      const ext = "." + (file.path.split(".").pop() || "").toLowerCase();
      const language = languageMap[ext];
      if (language) languages[language] = (languages[language] || 0) + 1;
    }

    return NextResponse.json({
      repository: `${owner}/${repo}`,
      branch: meta.default_branch,
      description: meta.description || "No description provided.",
      stars: meta.stargazers_count,
      files: files.length,
      languages,
      sizeKb: meta.size,
      demoMode: true
    });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : "Analysis failed" }, { status: 400 });
  }
}
