/** Vercel serverless handler (Node req/res — not Edge Response API). */
export default async function handler(req, res) {
  if (req.method !== "POST" && req.method !== "GET") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const secret = req.headers["x-sync-secret"] || req.query?.secret || "";
  const authHeader = req.headers.authorization || "";
  const cronSecret = process.env.CRON_SECRET || process.env.SYNC_SECRET || "";
  const authorized =
    (cronSecret && authHeader === `Bearer ${cronSecret}`) ||
    (process.env.SYNC_SECRET && secret === process.env.SYNC_SECRET);

  if (!authorized) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  const githubToken = process.env.GITHUB_TOKEN;
  const githubRepo = process.env.GITHUB_REPO;

  if (githubToken && githubRepo) {
    try {
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
        return res.status(502).json({ error: "GitHub dispatch failed", detail });
      }

      return res.status(200).json({
        ok: true,
        queued: true,
        message: "Facebook sync queued on GitHub Actions",
      });
    } catch (error) {
      return res.status(500).json({
        error: "GitHub dispatch error",
        detail: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return res.status(200).json({
    ok: true,
    queued: false,
    message:
      "Set GITHUB_TOKEN and GITHUB_REPO on Vercel to auto-run sync. GitHub Actions also runs every 2 hours.",
  });
}
