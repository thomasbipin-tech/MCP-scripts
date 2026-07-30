# Project memory — Netforge.ai video work

## Networking-term pronunciation (authoritative)

Any narration produced for this project — TTS or a script handed to a human reader —
must use these pronunciations. They are pinned as **phonemes**, not respellings, and fed
straight into the synthesiser (`is_phonemes=True` in `docs/demo-video/build/vo.py`).

| Term | Say it as | Phonemes (espeak/Kokoro convention) | Untreated output (wrong) |
|---|---|---|---|
| `VLAN` | VEE-lan | `vˈiːlæn` | `vlˈæn` — one syllable, "vlan" |
| `VLANs` | VEE-lans | `vˈiːlænz` | `vlˈæn` — plural silently dropped |
| `VXLAN` | vee-eks-LAN | `vˌiːˌɛkslˈæn` | stress on the wrong letter |
| `EVPN` | ee-vee-pee-EN | `ˌiːvˌiːpˌiːˈɛn` | `ˈɛvpən` — "evpen" |
| `CLI` | see-ell-EYE | `sˌiːˌɛlˈaɪ` | `klˈaɪ` — "cly" |
| `AVD` | ay-vee-DEE | `ˌeɪvˌiːdˈiː` | `ˈævd` — "avd" |
| `CVD` | see-vee-DEE | `sˌiːvˌiːdˈiː` | correct natively; pinned anyway |
| `BGP` | bee-gee-PEE | `bˌiːdʒˌiːpˈiː` | correct natively; pinned anyway |
| `STP` | ess-tee-PEE | `ˌɛstˌiːpˈiː` | correct natively; pinned anyway |
| `IP` | eye-PEE | `ˌaɪpˈiː` | correct natively; pinned anyway |
| `PDF` | pee-dee-EFF | `pˌiːdˌiːˈɛf` | correct natively; pinned anyway |
| `AI` | ay-EYE | `ˌeɪˈaɪ` | correct natively; pinned anyway |
| `YAML` | YAM-mel | `jˈæməl` | correct natively; pinned anyway |
| `BOM` | say "bill of materials" | `bˈɪl ʌv mətˈɪɹiəlz` | `bˈɑːm` — "bahm" |
| `Arista` | a-RIS-ta | `əɹˈɪstə` | `ˈæɹɪstə` — "ARR-ista" |
| `Visio` | VIZ-ee-oh | `vˈɪzioʊ` | `vˈɪsɪˌoʊ` — "VIS-ee-oh" |
| `Netforge.ai` | NET-forj dot ay-eye | `nˈɛtfɔːɹdʒ dˌɑːt ˌeɪˈaɪ` | joins the dot into the word |
| `Netforge` | NET-forj | `nˈɛtfɔːɹdʒ` | — |

### Rules that keep these correct

1. **Never respell orthographically.** `C. L. I` forces *primary* stress onto every letter
   and puts a sentence break between each one — that is what makes acronyms sound
   staccato. Spoken acronyms take secondary stress on every letter but the last, and
   primary on the last.
2. **Stress marks go immediately before the vowel**, espeak's convention
   (`ˌeɪvˌiːdˈiː`), *not* before the syllable as IPA textbooks do (`ˌeɪvˌiːˈdiː`).
   Kokoro is trained on espeak's convention. Getting this wrong rendered `AVD` as
   "Avi the" and stuttered `VXLAN` into a loop.
3. **`VLAN`/`VLANs` must be synthesised at speed 1.0.** Above 1.0× they compress until
   they read as "VLN" or "villain". Enforced by rule (`RISKY_ABOVE_1X`), never left to
   the ASR check.
4. **Never trust the ASR read-back as the primary check.** Synthesis is deterministic
   (identical SHA-1 across runs); the Whisper oracle is not — byte-identical audio
   transcribes differently run to run and has dropped whole clauses. Use it as a
   secondary net only, sampling twice.
5. **Valid read-backs that look like failures:** "Visio" correctly pronounced comes back
   spelled **"Vizio"**; letters come back comma-separated ("C, V, D"); "Netforge" is a
   coined word ASR spells any number of ways, so it is excluded from checking entirely.
6. **Verify on clean narration, before the music mix.** With the bed under it, ASR
   rendered a correct "transposed VLAN / missing BGP neighbor" as "V-line / V-neighbor".

`python3 vo.py audit` reprints the table against the live phonemiser — run it after any
model, voice or dependency change.

## Video content rules

- **Every topic gets its own dedicated screen.** Narration and picture must describe the
  same thing. Do not narrate account security over a tools grid, or a cable schedule over
  a rack elevation.
- **Do not reuse a screen for a different subject**, within a video or across the set.
  Build a new scene instead.
- **Screens must be full-bleed and uncropped** — see `docs/demo-video/SHOTLIST.md` §0.
- **Nothing invented.** Product facts come from netforge.ai's own site and `/docs`
  (22 pages plus a dated release history). No fabricated metrics, features or roadmap.
