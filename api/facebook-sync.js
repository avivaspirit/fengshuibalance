export default async function handler(request) {
  if (request.method !== "POST" && request.method !== "GET") {
    return Response.json({ error: "Method not allowed" }, { status: 405 });
  }

  const secret =
    request.headers.get("x-sync-secret") ||
    new URL(request.url).searchParams.get("secret") ||
    "";
  const authHeader = request.headers.get("authorization") || "";
  const cronSecret = process.env.CRON_SECRET || process.env.SYNC_SECRET || "";
  const authorized =
    (cronSecret && authHeader === `Bearer ${cronSecret}`) ||
    (process.env.SYNC_SECRET && secret === process.env.SYNC_SECRET);

  if (!authorized) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  const githubToken = process.env.GITHUB_TOKEN;
  const githubRepo = process.env.GITHUB_REPO;

  if (githubToken && githubRepo) {
    const response = await fetch(`https://api.github.com/repos/${githubRepo}/dispatches`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${githubToken}`,
        Accept: "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "fengshui-balance-sync",
      },
      body: JSON.stringify({ event_type: "facebook-sync" }),
    });

    if (!response.ok) {
      const detail = await response.text();
      return Response.json({ error: "GitHub dispatch failed", detail }, { status: 502 });
    }

    return Response.json({
      ok: true,
      queued: true,
      message: "Facebook sync queued on GitHub Actions",
    });
  }

  return Response.json({
    ok: true,
    queued: false,
    message:
      "Set GITHUB_TOKEN and GITHUB_REPO on Vercel to auto-run sync. Scheduled GitHub Actions can also run scripts/sync-facebook-posts.py.",
  });
}
