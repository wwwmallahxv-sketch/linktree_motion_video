# Prompt for Claude Code: Linktrees.link explainer video (HyperFrames)

Open this repo in Claude Code on the web and paste everything below the line.

---

You are making a motion graphics explainer video with **HyperFrames** (HeyGen's open-source HTML-to-video framework). If the HyperFrames skills aren't installed yet, install them first:

```
npx skills add heygen-com/hyperframes -g -a claude-code -y
```

Read the HyperFrames skills (`hyperframes`, `motion-graphics`, `hyperframes-animation`) before writing any code, and follow their rules.

## The product

**linktrees.link** is an Arabic-first, done-for-you link-in-bio service by Devmmnd Solutions (Aleppo, Syria). We design a branded page for a business that collects its WhatsApp, phone, save-contact button, map location and social accounts under one short link, `linktrees.link/<slug>`. Every page also comes with a printable SVG QR code.

Look at the site yourself before you start: https://linktrees.link. The example pages are:
- https://linktrees.link/chikenhut (fast-food restaurant, the main example. The brand spells it "Chiken Hut", so keep that spelling)
- https://linktrees.link/devmmnd (software company)
- https://linktrees.link/courseing (tech and education)
- https://linktrees.link/https-t-me-free-studen-ts (university dorm students group, Telegram community)
- Do **not** use Anas Moqresh's page.

Features to show: short branded link · printable SVG QR code · WhatsApp button · one-tap call · save-contact button (vCard) · map location with directions · all social accounts · custom branding (colors, logo, cover image) · Arabic right-to-left, with English available · light pages that open on weak internet · edits any time, and the link stays the same.

## Audience and goal

The viewer is a **shop or business owner** (restaurant, café, store, clinic) who is buying a page from us. After watching, they should understand what they get, how their customers will use it, and where to put their link and QR code. Tone: friendly, simple, confident. No tech jargon.

**Never mention AI, automation, or how the platform works behind the scenes.**

## Specs

- **Vertical 1080×1920, 30fps, 80–120 seconds.**
- **All on-screen text is Arabic, right-to-left.** Use a good Arabic font from Google Fonts (Tajawal, Cairo or IBM Plex Sans Arabic, bold for headlines). Check that Arabic letters connect properly and that nothing is mirrored. Latin text such as `linktrees.link/chikenhut` stays left-to-right inside RTL lines.
- Keep on-screen text short (a few words per line), and leave each line up long enough to read. The voiceover carries the detail.
- Brand: teal `#0f766e` as the main color, with white, a soft off-white, and one warm accent for buttons and highlights. Logo: https://linktrees.link/assets/logo.png
- Audio: Arabic voiceover + background music. I will provide `assets/voiceover.mp3` and `assets/music.mp3`. Until I do, time the scenes to the estimated durations below and leave the audio tracks as placeholders. Once the voiceover file is in place, re-time every scene to the real audio.

## Scenes and voiceover (Syrian dialect, light)

1. **The problem (~0–10s).** A shop owner's phone fills up with chat bubbles from customers asking for things. Five separate links fly around and pile up messily.
   VO: «عندك محل، مطعم، أو شغل خاص… وزبونك كل شوي بيسألك: شو رقمك؟ وين موقعك؟ عندك إنستغرام؟ وأنت كل مرة بتبعت خمس روابط.»

2. **The answer (~10–18s).** The messy links snap together into one clean link, and the Linktrees.link logo appears.
   VO: «من اليوم، كل هالشي صار برابط واحد. Linktrees.link.»

3. **Your link (~18–30s).** A browser or address bar types `linktrees.link/` and then the slug, cycling through `chikenhut` → `yourshop` → `yourname`. Highlight that the slug is the business's own name.
   VO: «بنعطيك رابط قصير باسمك: linktrees.link وبعدها اسم محلك. سهل ينحفظ، وسهل ينبعت.»

4. **What's on the page (~30–50s).** A phone mockup shows a page modeled on the real Chiken Hut page (logo, name, tagline, then the buttons). Each button lights up and gets a short label and a micro-animation as the VO names it: WhatsApp opens a chat, call shows a dialing ring, save contact shows a contact card dropping into the phone, map shows a pin and a route, and the social icons pop in.
   VO: «بس يفتح الزبون الرابط، بيلاقي كل شي قدامه: زر واتساب يحكيك فوراً، زر اتصال بضغطة وحدة، زر يحفظ رقمك على موبايله، وموقعك على الخريطة يوصّله لعندك، وكل صفحاتك على السوشال ميديا.»

5. **Made for you (~50–62s).** The same page re-skins live: colors change, a logo and cover image swap in, and three different brand looks appear side by side. Then a "weak signal" icon appears while the page still loads instantly. Finally, a small "edited" tick appears while the link underneath stays exactly the same.
   VO: «والصفحة مصممة على ذوقك: ألوانك، شعارك، وصورتك. عربية، وخفيفة بتفتح حتى لو النت ضعيف. وإذا بدك تعدّل شي؟ منعدّلك ياه، والرابط بيضل نفسه.»

6. **The QR code (~62–85s), the hero section. Spend the most effort here.** A QR code draws itself in, then appears in real-world mockups, one after another with smooth transitions:
   - a table tent stand on a restaurant table, with plates and a coffee cup around it
   - a sticker on a shop's glass door or window
   - a printed menu
   - a business card
   - a takeaway bag or packaging

   End with a customer's hand holding a phone up to the table QR. The camera frame locks on, and the Chiken Hut page opens on the phone. Show a quick scale-up to prove it stays sharp at any size (SVG).
   Build the mockups in HTML/CSS/SVG with depth, shadows and perspective so they feel like real objects, not flat icons. For the QR itself, try the real file at `https://linktrees.link/clients%20QRs/chikenhut/chikenhut.svg`. If it doesn't exist, generate a real, scannable QR that points to `https://linktrees.link/chikenhut`.
   VO: «ومع كل صفحة، بتاخد QR كود خاص فيك. اطبعه على طاولات المطعم، على باب المحل، على كرت الزيارة، أو على أكياسك. بأي حجم، وبدون ما تخرب الجودة. الزبون بيوجّه الكاميرا… وبثانية بيوصل لصفحتك.»

7. **Real examples (~85–100s).** Phones slide in showing Chiken Hut, Devmmnd, Courseing and the students' group page, each with its link underneath. Recreate them from the live pages, keeping their real names, logos and links.
   VO: «متل Chiken Hut، وDevmmnd، وCourseing، وغيرهم كتير. صار عندهم رابط واحد لكل شي.»

8. **Where to use it (~100–110s).** Quick icons with the link dropping into each place: Instagram bio, WhatsApp status, the Google Maps listing, and the printed QR by the cash register.
   VO: «حط رابطك ببايو الإنستغرام، بحالة الواتساب، وعلى Google Maps… وخلّي الـQR بمكان واضح بمحلك.»

9. **Call to action (~110–120s).** Logo, tagline, `linktrees.link`, and a WhatsApp button that pulses.
   VO: «Linktrees.link… رابط واحد، وكل حضورك أونلاين. اطلب صفحتك اليوم عبر واتساب.»
   On-screen: «رابط واحد… وكل حضورك أونلاين» + «اطلب صفحتك عبر واتساب»

## How to work

1. Fetch the site and the four example pages, and download the logos and assets you need into `assets/`.
2. Show me a short storyboard first: one line per scene covering the visual, the motion and the on-screen text. Wait for my OK.
3. Build the composition scene by scene. Render a low-res preview, check frames yourself for Arabic rendering, text overflow, empty-looking frames and timing, and fix what you find.
4. When I add `voiceover.mp3` and `music.mp3`, sync everything to the voiceover, duck the music under the voice, and render the final MP4 at 1080×1920.
5. Follow the cloud workflow rules in `CLAUDE.md`: commit and push every preview and the final render to `renders/` so I can download them from GitHub, and tell me the file name each time.
