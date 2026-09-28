import { NextResponse } from "next/server";

const ignored = /(^|\/)(node_modules|\.git|\.next|dist|build|coverage|vendor|out|target)(\/|$)/;
const allowed = /\.(ts|tsx|js|jsx|py|java|cpp|c|h|go|rs|json|toml|ini|cfg|md|css|scss|html|yml|yaml|xml|sh|sql)$/i;

function scorePath(path: string, query: string) {
  const lower = path.toLowerCase();
  let score = 0;
  const terms = query.toLowerCase().split(/[^a-z0-9_.-]+/).filter(Boolean);
  for (const term of terms) if (term.length > 1 && lower.includes(term)) score += 8;
  if (/(^|\/)readme(?:\.[^/]+)?$/i.test(path)) score += 10;
  if (/(^|\/)(pyproject\.toml|package\.json|go\.mod|cargo\.toml|pom\.xml|build\.gradle)$/i.test(path)) score += 10;
  if (/(^|\/)(src|app|lib|server|packages|integrations)(\/|$)/i.test(path)) score += 9;
  if (/(^|\/)(tests?|spec)(\/|$)/i.test(path) || /\.(test|spec)\.[^.]+$/i.test(path)) score += 7;
  if (/(^|\/)(api|routes?|services?|agents?|scanners?|vcs)(\/|$)/i.test(path)) score += 5;
  return score;
}

export async function POST(req: Request) {
  try {
    const { repoUrl, query = "" } = await req.json();
    const m = String(repoUrl || "").match(/^https?:\/\/github\.com\/([^/]+)\/([^/#?]+)(?:[#?].*)?$/i);
    if (!m) return NextResponse.json({ error: "Use a public GitHub repository URL." }, { status: 400 });

    const owner = m[1], repo = m[2].replace(/\.git$/, "");
    const base = { headers: { Accept: "application/vnd.github+json", "User-Agent": "RepoPilot" } };

    const meta = await fetch(`https://api.github.com/repos/${owner}/${repo}`, base);
    if (!meta.ok) return NextResponse.json({ error: "GitHub repository could not be read." }, { status: meta.status });
    const info = await meta.json();

    const treeRes = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/git/trees/${encodeURIComponent(info.default_branch)}?recursive=1`,
      base
    );
    if (!treeRes.ok) return NextResponse.json({ error: "Repository tree could not be read." }, { status: treeRes.status });

    const tree = await treeRes.json();
    const allFiles = (tree.tree || []).filter(
      (x: any) => x.type === "blob" && allowed.test(x.path) && !ignored.test(x.path)
    );

    const ranked = allFiles
      .map((f: any) => ({ ...f, score: scorePath(f.path, String(query || "")) }))
      .sort((a: any, b: any) => b.score - a.score || a.path.length - b.path.length)
      .slice(0, 18);

    const snippets = await Promise.all(ranked.map(async (f: any) => {
      try {
        const path = f.path.split("/").map(encodeURIComponent).join("/");
        const r = await fetch(
          `https://raw.githubusercontent.com/${owner}/${repo}/${encodeURIComponent(info.default_branch)}/${path}`,
          base
        );
        if (!r.ok) return null;
        const content = await r.text();
        return { path: f.path, content: content.slice(0, 12000), truncated: content.length > 12000, score: f.score };
      } catch { return null; }
    }));

    const files = snippets.filter(Boolean);
    return NextResponse.json({
      repository: `${owner}/${repo}`,
      branch: info.default_branch,
      query: String(query || ""),
      files,
      fileCount: files.length,
      scannedFileCount: allFiles.length
    });
  } catch (e) {
    return NextResponse.json(
      { error: e instanceof Error ? e.message : "Context retrieval failed" },
      { status: 500 }
    );
  }
}