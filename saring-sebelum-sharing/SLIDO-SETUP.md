# Slido setup — step by step

End goal: a live "real or fake" poll your audience votes in from their phones during the talk, with results you can show on screen.

The deck already has a `<PollEmbed>` component on **slide 4 ("Cast your vote")** that expects a Slido URL. This guide takes you from "no Slido account" to "the slide shows a working QR code" in about 15 minutes.

**Who this is for:** you've never used Slido before.

---

## tl;dr

1. Sign up at [slido.com](https://www.slido.com) with your Sentinel Tech email.
2. Create an event titled `Saring Sebelum Sharing · 6 Nov 2026`.
3. Add one **Multiple choice** poll — question: *"Which ones are REAL?"*, options `A`, `B`, `C`, `D`, allow multiple answers.
4. Copy the event's **Share** link (looks like `https://app.sli.do/event/<hash>`).
5. Open `slides.md`, find both `POLL_URL_HERE` strings, paste the link in.
6. Rebuild with `pnpm dev` and confirm the QR code renders on slide 4.
7. On the day: Start the poll from Slido's **Present** mode when you reach slide 4.

Rest of the doc is detail + gotchas + what to do if free Slido isn't enough.

---

## Step 1 — Sign up

1. Go to <https://www.slido.com>.
2. Click **Sign up free** (top right).
3. Use your work email (`hirzi.n@sentineltech.com`). Pick a strong password.
4. Confirm the email Slido sends.
5. Skip the onboarding survey if you don't care; it only picks default templates.

You now have a **Basic (free) workspace**. See the free-plan limits section at the bottom — the 100-participant cap matters for a hybrid townhall.

## Step 2 — Create the event

An "event" in Slido = one container for all the questions, polls and quizzes you run in a session. One townhall = one event.

1. From the dashboard, click **Create slido**.
2. **Event name:** `Saring Sebelum Sharing · 6 Nov 2026`.
3. **Event date:** `6 Nov 2026`. (Keeping it narrow helps analytics later.)
4. **Access code:** leave as the auto-generated one, or set a short custom code (e.g. `saring`) so the share link reads `app.sli.do/event/saring`.
5. **Privacy:** leave as **Anyone with the link can join** for a townhall. Set to **Only authenticated users** if your IT policy requires it.
6. Click **Create slido**.

Slido drops you into the event editor.

## Step 3 — Add the real/fake poll

The deck's quiz has four cards (A, B, C, D). The audience should mark **every one they think is real**.

1. Left sidebar → **Polls** → **+ Create poll**.
2. Pick **Multiple choice**.
3. Question text: `Which of these are REAL?`
4. Options:
   - `A — Malaysia · RM100 SARA via MyKad headline`
   - `B — Indonesia · Sri Mulyani "teachers are a burden" video`
   - `C — Malaysia · JPJ customer-rage TikTok`
   - `D — Indonesia · Coin-hoarding in water-gallons photo`
5. Toggle **"Multiple answers"** ON (so people can pick several).
6. Toggle **"Correct answers"** OFF (don't reveal correctness in the chart; the slide reveal does that).
7. Toggle **"Anonymous"** ON. Hands up more honestly.
8. Click **Save**.

Keep the poll **inactive** for now. You'll activate it when you reach slide 4 during the talk.

> **Why not two polls (one per round)?** You cut Round 2, so one poll is enough. If you add Round 2 back later, create a **second** multiple-choice poll with the new items; both polls live in the same event, so the audience doesn't re-join.

## Step 4 — Get the sharing link

1. In the event editor, click the **Share** button (top right).
2. You'll see:
   - **Audience join link** — e.g. `https://app.sli.do/event/abc123xyz`
   - **QR code** — a PNG you can download, but you don't need it: the deck generates its own QR from the link.
3. **Copy the audience join link.** This is the one you paste into the deck.

## Step 5 — Wire the link into the deck

1. Open `saring-sebelum-sharing/slides.md`.
2. Search for `POLL_URL_HERE`. There's one occurrence (slide 4, "Cast your vote").
3. Replace it with the link from Step 4. The line should end up looking like:

   ```html
   <PollEmbed url="https://app.sli.do/event/abc123xyz" title="Real or fake? A · B · C · D" />
   ```

4. Save.

## Step 6 — Verify the QR renders

```bash
cd saring-sebelum-sharing
pnpm dev
```

Open `http://localhost:3030/#/4` (slide 4). You should see:
- A QR code on the right (scanning it on your phone opens the Slido event in a browser).
- The URL printed under the QR as a fallback.
- An iframe on the left — **this is where free vs. paid Slido matters** (next section).

## Step 7 — On the day

**Before the talk starts:**
1. Open Slido in a second browser window on your laptop, in **Present** mode.
2. Have the poll **ready** but not yet **activated** (so the audience doesn't vote before you reach it).

**When you hit slide 4:**
1. In Slido's Present mode, **activate** the poll.
2. The audience's Slido view updates with the question — they vote.
3. Watch the bar chart fill in Slido's Present mode (don't put this on the shared screen yet; it reveals real-vs-fake prematurely).
4. After ~20 seconds, hit space to go to slide 5 (the reveal).
5. During Q&A, you can briefly share Slido's **Results** view to show the final poll bars — now that the answers are out.

**Timing fits:** slide 4 has a 30-second budget for voting. Slido takes ~5 sec to activate + show results.

---

## Free plan: hard limits that will bite you

Slido's **Basic (free)** plan was last confirmed with these limits (verify at [slido.com/pricing](https://www.slido.com/pricing) before the talk — paid-plan features move around):

| Limit | What it means for this talk |
|---|---|
| **3 polls per event** | 1 poll (Round 1 only) — fine. If Round 2 comes back, still fine. |
| **100 participants per event (cumulative)** | **This is the big one.** If your townhall has >100 attendees (office + remote combined), the 101st person who tries to join gets rejected. |
| **No iframe embedding** (Professional-tier feature) | Slide 4's iframe pane won't load the poll. The QR + link still work — audience just opens Slido in a separate browser tab. **The deck's `PollEmbed` already handles this.** |
| **No question moderation on free** | Audience Q&A is unmoderated. For a townhall this might be fine; if you want to vet questions, you need Engage or higher. |

### What to do if you have more than 100 attendees

Three options, in order of least effort:

1. **Upgrade to Slido Engage** (~€15/month, cancel after the talk). Also unlocks iframe embed, so the slide 4 pane fills in nicely.
2. **Use Mentimeter free** instead — different split: up to 2 slides per presentation + unlimited participants on free. The deck's `PollEmbed` takes any URL, so you can swap in a Menti link the same way.
3. **Use Google Forms** — unlimited, but no live chart during the talk. You'd pivot slide 4 to just "scan this, vote now, I'll show results after".

### If the iframe doesn't load (CORS / corporate network / free plan)

The `PollEmbed` component already renders the QR + link regardless of whether the iframe loads. You can also force QR-only mode by passing `qr-only`:

```html
<PollEmbed url="..." title="Real or fake? A · B · C · D" qr-only />
```

This gives you a bigger, centred QR + the link — no iframe. Cleaner on free-plan Slido anyway.

---

## Testing checklist (before the talk)

- [ ] Open the Slido event link on your phone. Submit a test vote.
- [ ] Reset the poll results in Slido (**… → Reset results**) so test votes don't bias the real count.
- [ ] Open slide 4 at `http://localhost:3030/#/4`. Confirm the QR shows and the link under it matches.
- [ ] Scan the QR with your phone's camera. It should open the same Slido page.
- [ ] If the iframe is empty: free plan, expected — the QR is doing the work. Consider `qr-only` for a cleaner layout.
- [ ] On the venue Wi-Fi (not your home): scan the QR again. Many corporate networks block `app.sli.do`.
- [ ] From a remote viewer's angle: drop the plain link into the chat and open it. It should load without login.

---

## Alternatives (if you'd rather not use Slido)

| Tool | Free-plan audience cap | Iframe embed on free? | Setup effort |
|---|---|---|---|
| **Slido** | 100 | No | Low (this guide) |
| **Mentimeter** | 2 slides, unlimited audience | No | Low |
| **Poll Everywhere** | 25 responses/poll | No | Low |
| **Google Forms** | Unlimited | Yes, but no live chart | Lowest |
| **Wooclap** | 1,000 audience on free | Yes | Medium |

For a townhall with a predictable audience, Mentimeter free actually fits better than Slido free — no participant cap. If you anticipate >100 but <1000, Wooclap free is worth a look.

Whichever you pick, drop the public share URL into `<PollEmbed url="...">` on slide 4 and the component takes care of the QR + fallback.
