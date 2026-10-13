# QQ Show 2000 Outfit Saver 👗✨

> Download, synchronize, and composite animated avatars from [qqshow2000.com](https://qqshow2000.com) into a single, perfectly-looping animated GIF.

<p align="center">
  <img src="qqshow_e9fn6oxd_My_Outfit.gif" alt="QQ Show Composited Avatar" width="280">
  <br>
  <em>Sample composited outfit (ID: <code>e9fn6oxd</code>), with 11 animated layers synchronized at 2x scale</em>
</p>

---

## 🌸 About & Cultural Context

Met [Viola](https://viola.city) at [TIAT postgeneration](https://luma.com/postgeneration). She was showing something totally different. I found her [Qzone Museum](https://viola.city) on her site and fell in.

It felt familiar. 1996, anime fan, no resources. [KiSS dolls](https://en.wikipedia.org/wiki/Kisekae_Set_System) were a huge step up from uuencoded images off Usenet. Download a doll, dress it up, get the whole character. All fan made. I was running [Dragon Ball Project](https://www.insidescanlation.com/spotlight/translators) then, sourcing raws / scans / lettering, Jason on translations. KiSS was my guilty pleasure too. Not allowed to have dolls, so I played dress up without asking permission.

Six weeks in China with my 6 month old, meeting family, made it click again. QZone next to MySpace in my head. Same era. Your own space, vibrant customization. Computer lib as a global phenomenon.

Kay Zeng's [QQ Show](https://qqshow2000.com) is that impulse turned all the way up. Super busy GIF composites. Too much on purpose. Unapologetically dumb and unapologetically cute. Same as my [Hyphy Kawaii](https://news.codame.com/p/hyphy-kawaii) work.

This tool is just a fix. Right click only saves one layer. Now you can save the whole fit and share it wherever you are comfortable.

The PFP lesson: real value is not floor price. It is people remixing after hype dies. [CC remix culture](https://creativecommons.org/) plus community building. Avatars and aliases are identity and privacy practice. My [DataBabies333 Picrew maker](https://picrew.me/en/image_maker/2720340) is still alive for people to appropriate the assets, even after the hype passed.

If this clicks, check out more of my artwork, starting with [Hyphy Kawaii](https://news.codame.com/p/hyphy-kawaii).

---

## 💡 Why This Tool?

When you create an outfit on [qqshow2000.com](https://qqshow2000.com) and try to save the avatar image by right-clicking or saving the GIF, the browser only saves **a single layer** (like just the background or hair). This happens because the web app layers dozens of transparent animated GIFs on top of each other using CSS `z-index` and absolute positioning.

Furthermore, each animated layer has its own frame delays and loop timings (e.g. wings flapping every 150ms/300ms, eyes blinking every 500ms, sparkle effects cycling every 200ms).

**QQ Show 2000 Outfit Saver** solves this by:
1. Fetching the shared outfit configuration directly from the database blueprint.
2. Resolving all z-index positions, two-part hairstyles (`frontHair` / `backHair`), defaults, and slot suppression.
3. Calculating the Least Common Multiple (LCM) timeline across all layer frame cycles.
4. Compositing every frame in order with full alpha transparency.
5. Exporting a single, synchronized animated GIF!

---

## 🌐 Live Web App

You can run the web app directly in your browser with **no installation or backend required**:

👉 **[https://starpause.github.io/qqshow2000-outfit-saver/](https://starpause.github.io/qqshow2000-outfit-saver/)**

The entire pipeline runs 100% client-side in the browser: it queries Supabase for the outfit blueprint, fetches the GIF assets, decodes frames via `omggif`, synchronizes the animation timeline, and renders the composite animated GIF using `gifenc`.

<p align="center">
  <img src="screenshot.jpg" alt="QQ Show Outfit Saver Web UI" width="640">
</p>

---

## ⚡ Features

- **100% Serverless Web App:** Runs entirely in modern browsers on GitHub Pages or locally.
- **Pixel-Art Crisp Scaling:** Export at native **1x** (140x226) or integer-scaled **2x** (280x452), **3x** (420x678), or **4x** (560x904) with nearest-neighbor interpolation.
- **Background Modes:** `auto` (preserves background scene or canvas), `transparent` (alpha-channel GIF transparency), or custom hex colors.
- **History & Faved Fits:** A built-in browser-local history box (`localStorage`) tracks your saved fits with one-click **Load**, **QQ Show link**, and **Copy URL** buttons. Never posted or stored on any external server.
- **Dual Interfaces:** Use the web app (hosted or local) or the Python **Command Line Interface (CLI)**.
- **Zero Heavy Dependencies:** Python tools require only standard Python 3 and Pillow.

---

## 🛠️ Installation & Local Usage

If you prefer to run it locally or use the CLI:

```bash
git clone https://github.com/starpause/qqshow2000-outfit-saver.git
cd qqshow2000-outfit-saver
pip install pillow
```

### 1. Local Web App

```bash
python server.py
# or
python cli.py --ui
```

Then open **[http://localhost:8080](http://localhost:8080)** in your browser:
- Paste any URL (e.g., `https://qqshow2000.com/?id=e9fn6oxd`) or ID (`e9fn6oxd`).
- Select your **Scale** and **Background** preference.
- Click **Generate GIF** to watch the real-time compositor run.
- Preview the animated GIF, review the layer stack, and click **Download Animated GIF**.
- Your generated outfits are automatically saved in the **History - Fits You Faved** box below.

---


### 2. Command-Line Interface (CLI)

```bash
# Save outfit (defaults to 2x crisp scale)
python cli.py https://qqshow2000.com/?id=e9fn6oxd

# Choose custom scale (1x, 2x, 3x, or 4x)
python cli.py e9fn6oxd -s 1 -o my_fit_1x.gif
python cli.py e9fn6oxd -s 2 -o my_fit_2x.gif

# Export with transparent background
python cli.py e9fn6oxd --bg transparent

# Inspect layers and animation cycles without rendering
python cli.py e9fn6oxd --info
```

CLI `--info` preview output:
```text
[1/3] Fetching outfit 'e9fn6oxd'...
      Found: "My Outfit" (ID: e9fn6oxd)

[2/3] Resolved 11 z-index layers:
      z=00 [backgrounds     ] 彩虹粉泡
      z=03 [wings           ] 闪粉蝴蝶
      z=08 [outfit          ] 猫咪粉裙套装
      z=09 [makeup          ] 动漫猫嘴水润眼
      z=11 [frontHair       ] 金棕绑带双丸子头
      z=11 [neckwear        ] 银色星星项链
      z=13 [face-decor      ] 温度计
      z=15 [headwear        ] 公主皇冠
      z=17 [frame           ] 爱心粉框
      z=19 [companion       ] 萝卜兔
      z=20 [sparkle         ] 云朵双子星
```

---

## 📜 Credits & Disclaimer

- Original QQ Show concept, assets & copyrights belong to **Tencent Holdings Limited (腾讯控股有限公司)**.
- Digital archive & website by **[Kay Zeng](https://www.kayzeng.com/)** at **[qqshow2000.com](https://qqshow2000.com)**.
- Inquiries / Wayback Machine archive project: `qqshow2000project@gmail.com`.
- Inspired by discovery via **[viola.city](https://viola.city/projects/qzone-museum/)**.
- Compositor tool by **[staRpauSe](https://github.com/starpause)**.
