# Linktrees.link motion video: project rules

The full creative brief is in `PROMPT.md`. These rules cover how to work in this repo.

## Cloud workflow
- This project runs in Claude Code on the web. The owner has a slow, unstable connection and only downloads results from GitHub, so do all installing, building and rendering here.
- After every render, **commit and push** so the owner can download it from GitHub:
  - previews: `renders/preview-vN.mp4`, 480×854, kept small (aim for under 10 MB)
  - final: `renders/final-1080x1920.mp4`
- Keep only the **latest preview** in `renders/`. Delete older previews before committing a new one so the repo stays small.
- No file over 90 MB (GitHub's limit is 100 MB). If the final render is bigger, re-encode with H.264 at a higher CRF until it fits.
- Commit source files too (compositions, scripts, downloaded assets) so the work can be resumed in a new session.
- Never commit `node_modules/`, caches or temporary frames.

## If something is blocked
- If fetching linktrees.link, Google Fonts, or the Chrome download for rendering fails because of network restrictions, stop and tell the owner exactly which host is blocked. They can allow it in the environment's network settings. Don't silently swap in a different font or made-up content.

## Content rules
- Never mention AI, automation, or how the platform works behind the scenes.
- On-screen text is Arabic, right-to-left. Use the brand's own spelling "Chiken Hut".
- Don't use Anas Moqresh's example page.

## Audio
- The owner will add `assets/voiceover.mp3` and `assets/music.mp3`. When they appear, re-time all scenes to the real voiceover.
