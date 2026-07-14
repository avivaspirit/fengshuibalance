# AGENTS.md — Feng Shui Balance

## Project type
Static HTML site (no build step)

## Commands
- Dev: `cd ~/fengshuibalance && python -m http.server 8080`
- Deploy: `cd ~/fengshuibalance && vercel --prod --yes --force --archive=tgz`
- Live URL: https://fengshuibalance.vercel.app

## Conventions
- Language: Thai (lang="th")
- Bilingual Thai/English content
- CSS cache-bust: ?v=YYYYMMDDx
- GTM on every page
- SVG icons only, NEVER emoji
- Design: luxury with shadows

## DO NOT
- Delete URLs or domains
- Use emoji anywhere
- Deploy without QA (ship-loop Phase 5)
- Change bilingual content structure without user approval

## Related skills
- `fengshui-balance` — brand-specific rules
- `static-site-engineering` — deploy protocol
- `ship-loop` — build → QA → deploy → verify loop
