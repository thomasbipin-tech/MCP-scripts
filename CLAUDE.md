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
| `WAN` | wan (rhymes with "van") | `wˈæn` | `wˈɑːn` — the English word "wan", pale |
| `SD-WAN` | ess-dee-WAN | `ˌɛsdˌiːwˈæn` | reads "SD" as a word |
| `LAN` | lan | `lˈæn` | correct natively; pinned anyway |
| `MPLS` | em-pee-ell-ESS | `ˌɛmpˌiːˌɛlˈɛs` | correct natively; pinned anyway |
| `VPN` | vee-pee-EN | `vˌiːpˌiːˈɛn` | correct natively; pinned anyway |
| `VRF` / `VRFs` | vee-ar-EFF | `vˌiːˌɑːɹˈɛf` / `vˌiːˌɑːɹˈɛfs` | `vˌiːˌɑːɹɹˈɛf` — doubled r; plural dropped |
| `SVI` / `SVIs` | ess-vee-EYE | `ˌɛsvˌiːˈaɪ` / `ˌɛsvˌiːˈaɪz` | plural silently dropped |
| `HSRP` | aitch-ess-ar-PEE | `ˌeɪtʃˌɛsˌɑːɹpˈiː` | correct natively; pinned anyway |
| `VRRP` | vee-ar-ar-PEE | `vˌiːˌɑːɹˌɑːɹpˈiː` | `vˌiːˌɑːɹɹˌɑːɹpˈiː` — doubled r |
| `FHRP` | eff-aitch-ar-PEE | `ˌɛfˌeɪtʃˌɑːɹpˈiː` | correct natively; pinned anyway |
| `OSPF` | oh-ess-pee-EFF | `ˌoʊˌɛspˌiːˈɛf` | `ˈɑːspf` — "ospf" as a word |
| `MTU` | em-tee-YOU | `ˌɛmtˌiːjˈuː` | correct natively; pinned anyway |
| `VTY` | vee-tee-WHY | `vˌiːtˌiːwˈaɪ` | correct natively; pinned anyway |
| `ACL` | ay-see-ELL | `ˌeɪsˌiːˈɛl` | `ˈækəl` — "ackle" |
| `IPv6` | eye-pee-vee-SIX | `ˌaɪpˌiːvˌiːsˈɪks` | `ˈɪpv sˈɪks` — "ipv six" |
| `IPAM` | EYE-pam | `ˈaɪpæm` | `ˈɪpæm` — "ipp-am" |
| `CIDR` | CIDER | `sˈaɪdɚ` | `sˈɪdɚ` — "sidder" |
| `MAC` | mack | `mˈæk` | correct natively; pinned anyway |
| `DHCP` | dee-aitch-see-PEE | `dˌiːˌeɪtʃsˌiːpˈiː` | correct natively; pinned anyway |
| `DNS` | dee-en-ESS | `dˌiːˌɛnˈɛs` | correct natively; pinned anyway |
| `AAA` | ay-ay-AY | `ˌeɪˌeɪˈeɪ` | correct natively; pinned anyway |
| `TACACS` | TACK-axe | `tˈækæks` | correct natively; pinned anyway |
| `RADIUS` | RAY-dee-us | `ɹˈeɪdiəs` | correct natively; pinned anyway |
| `SNMP` | ess-en-em-PEE | `ˌɛsˌɛnˌɛmpˈiː` | correct natively; pinned anyway |
| `NTP` | en-tee-PEE | `ˌɛntˌiːpˈiː` | correct natively; pinned anyway |
| `SSH` | ess-ess-AITCH | `ˌɛsˌɛsˈeɪtʃ` | correct natively; pinned anyway |
| `LLDP` | ell-ell-dee-PEE | `ˌɛlˌɛldˌiːpˈiː` | correct natively; pinned anyway |
| `CDP` | see-dee-PEE | `sˌiːdˌiːpˈiː` | correct natively; pinned anyway |
| `OOB` | oh-oh-BEE | `ˌoʊˌoʊˈbiː` | `ˈuːb` — "oob" |
| `MD5` | em-dee-FIVE | `ˌɛmdˌiːfˈaɪv` | breaks after "MD" |
| `SFP` / `QSFP` | ess-eff-PEE / cue-ess-eff-PEE | `ˌɛsˌɛfpˈiː` / `kjˌuːˌɛsˌɛfpˈiː` | correct natively; pinned anyway |
| `DAC` | dack | `dˈæk` | correct natively; pinned anyway |
| `EOS` | ee-oh-ESS | `ˌiːˌoʊˈɛs` | `ɪˈoʊz` — "ee-ohz" |
| `NX-OS` | en-ex oh-ESS | `ˌɛnˈɛks ˌoʊˈɛs` | runs the two halves together |
| `IOS-XE` | eye-oh-ess ex-EE | `ˌaɪˌoʊˈɛs ˌɛksˈiː` | `ˌaɪˌoʊˈɛszˈiː` — "ios-zee" |
| `PAN-OS` | pan oh-ESS | `pˈæn ˌoʊˈɛs` | runs the two halves together |
| `ArubaOS-CX` | a-ROO-ba oh-ess see-EX | `əɹˈuːbə ˌoʊˈɛs sˌiːˈɛks` | unintelligible |
| `SLA` / `SLAs` | ess-ell-AY | `ˌɛsˌɛlˈeɪ` / `ˌɛsˌɛlˈeɪz` | correct natively; pinned anyway |
| `HTML` | aitch-tee-em-ELL | `ˌeɪtʃtˌiːˌɛmˈɛl` | correct natively; pinned anyway |
| `CSV` | see-ess-VEE | `sˌiːˌɛsvˈiː` | correct natively; pinned anyway |
| `UI` | you-EYE | `jˌuːˈaɪ` | correct natively; pinned anyway |
| `NIST` | nist | `nˈɪst` | correct natively; pinned anyway |
| `CIS` | see-eye-ESS | `sˌiːˌaɪˈɛs` | `sˈɪs` — "sis" |
| `AS` (autonomous system) | ay-ESS | `ˌeɪˈɛs` | `æz` — the word "as" |
| `HMAC-SHA1` | aitch-mack shah ONE | `ˌeɪtʃmˈæk ʃˈɑː wˈʌn` | unintelligible |
| `HMAC-SHA2-256` | aitch-mack shah two, two-fifty-six | `ˌeɪtʃmˈæk ʃˈɑː tˈuː tˌuːfˈɪfti sˈɪks` | unintelligible |

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
7. **Match on word boundaries, and phonemise the sentence whole.** An unbounded match
   plucks `IP` out of `IPAM`. And phonemising the fragments *either side* of a term in
   isolation loses sentence context, so espeak gives function words their citation form —
   "a WAN overview" came out as stressed "AY wan". `vo.py` therefore masks each term with
   an ordinary word, phonemises the whole line in one pass, and swaps the mask for the
   pinned phonemes afterwards.
8. **Any new acronym in narration needs an entry before it ships.** Plurals count as
   separate entries (`VRF`/`VRFs`); without one the plural is silently dropped.

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
