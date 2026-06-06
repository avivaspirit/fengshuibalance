/** @vercel/node — CommonJS handler for static-site + /api routes */
module.exports = async function handler(req, res) {
  try {
    if (req.method !== "POST" && req.method !== "GET") {
      res.setHeader("Content-Type", "application/json");
      res.statusCode = 405;
      res.end(JSON.stringify({ error: "Method not allowed" }));
      return;
    }

    const secret = req.headers["x-sync-secret"] || (req.query && req.query.secret) || "";
    const authHeader = req.headers.authorization || "";
    const cronSecret = process.env.CRON_SECRET || process.env.SYNC_SECRET || "";
    const authorized =
      (cronSecret && authHeader === "Bearer " + cronSecret) ||
      (process.env.SYNC_SECRET && secret === process.env.SYNC_SECRET);

    if (!authorized) {
      res.setHeader("Content-Type", "application/json");
      res.statusCode = 401;
      res.end(JSON.stringify({ error: "Unauthorized" }));
      return;
    }

    const githubToken = process.env.GITHUB_TOKEN;
    const githubRepo = process.env.GITHUB_REPO;

    if (githubToken && githubRepo) {
      const response = await fetch("https://api.github.com/repos/" + githubRepo + "/dispatches", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + githubToken,
          Accept: "application/vnd.github+json",
          "Content-Type": "application/json",
          "User-Agent": "fengshui-balance-sync",
        },
        body: JSON.stringify({ event_type: "facebook-sync" }),
      });

      if (!response.ok) {
        const detail = await response.text();
        res.setHeader("Content-Type", "application/json");
        res.statusCode = 502;
        res.end(JSON.stringify({ error: "GitHub dispatch failed", detail: detail }));
        return;
      }

      res.setHeader("Content-Type", "application/json");
      res.statusCode = 200;
      res.end(
        JSON.stringify({
          ok: true,
          queued: true,
          message: "Facebook sync queued on GitHub Actions",
        })
      );
      return;
    }

    res.setHeader("Content-Type", "application/json");
    res.statusCode = 200;
    res.end(
      JSON.stringify({
        ok: true,
        queued: false,
        message:
          "Set GITHUB_TOKEN and GITHUB_REPO on Vercel to auto-run sync. GitHub Actions also runs every 2 hours.",
      })
    );
  } catch (error) {
    res.setHeader("Content-Type", "application/json");
    res.statusCode = 500;
    res.end(
      JSON.stringify({
        error: "Handler error",
        detail: error && error.message ? error.message : String(error),
      })
    );
  }
};
