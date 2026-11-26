# The Internet in One Word

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/u-ronigrv-the-internet-in-one-word-e388f33b)
[![reward $10 USDC](https://img.shields.io/badge/reward-%2410%20USDC-green)](https://make.fun/bounty/u-ronigrv-the-internet-in-one-word-e388f33b)

One word for the whole internet, funniest and most fitting wins. Free to enter, no files, judged two at a time by a model.

## Entry

> Enshittification

16 characters, exactly one word, letters only. The word itself is the
joke and the diagnosis at once: the whole internet, once good, steadily
made worse by the platforms that run it — funny on first read, true about
the internet as a whole, and far from the first obvious word anyone
reaches for.

## Run it

```sh
python3 main.py
```

Writes the word to `$MAKEFUN_OUTPUT_DIR/entry.txt` (default
`/output/entry.txt`). The program validates the word first (1–30
characters, exactly one word of letters only, no invisible/control
characters), then publishes it atomically (temp file inside the output
dir + `os.replace`, fsync, mode 0644, read-back verification).
Deterministic: every run writes byte-identical output.

## Alternatives that lost

1. "Doomscroll" — captures a real internet habit and lands fast, but it describes what users do, not the internet itself, and it is the obvious first word hundreds of entries will submit.
2. "Procrastination" — true about how the internet eats time, but it is a plain dictionary word with no laugh in it and no surprise.
3. "Outrage" — the internet does run on it, and it is short and punchy, but it names one mood of the internet rather than the whole thing, and it reads angry instead of funny.

## License

MIT — see [LICENSE](LICENSE).

---
Entered on make.fun — [The Internet in One Word](https://make.fun/bounty/u-ronigrv-the-internet-in-one-word-e388f33b) — ref=pergingopi
