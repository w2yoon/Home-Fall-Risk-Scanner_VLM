# Source Documents Index — Home Safety Knowledge Base

These files contain the actual fetched text of every public-domain / OGL source identified for the SEVA Home Safety Assistant knowledge base, as of 2026-07-17.

**Rule for use: every item in `data/knowledge/hazards.json` must trace to a passage in one of these files (or another source fetched and saved the same way). Do not write an item and attribute it to one of these sources from memory — open the file, find the passage, then write the item and record the reference.**

| File | Source | Authority label to use | License |
|---|---|---|---|
| `01_CDC_STEADI_checklist.md` | CDC STEADI | `"CDC STEADI"` | Public domain |
| `02_NIA_preventing_falls_room_by_room.md` | National Institute on Aging | `"NIA"` | Public domain |
| `03_ADA_AccessBoard_Ch6_ToiletRooms.md` | U.S. Access Board / ADA Standards §§603-610 | `"ADA Standards 2010"` or `"U.S. Access Board"` | Public domain |
| `04_ADA_805_and_ClearFloorSpace.md` | ADA Standards §805, §304, §305 | `"ADA Standards 2010"` | Public domain |
| `05_NHSinform_hazard_identification.md` | NHS inform (Scotland) | `"NHS"` | OGL v3 — **verify site-specific notice before shipping; attribution required if used** |
| `06_NHSinform_home_safety_check_PARTIAL.md` | NHS inform (Scotland) | `"NHS"` | **DO NOT USE — content unverified, partial fetch only. Re-fetch required.** |

## Known gaps — not yet sourced

These were identified as candidate topics but were not found verified in any source fetched so far. Search CPSC and FDA directly before defaulting these to `"SEVA internal"`:

- Sharp/angular furniture corners and secondary-impact injury on falling
- Round vs. angular table shape as a preference
- Specific bed-height numeric range (sources say "the right height to get in/out easily" but do not give a number — do not invent one)
- Kitchen/bathroom door width compatibility with walking frames (partial NHS lead in file 06, unverified)

## What was deliberately excluded

- **AARP HomeFit Guide** — copyrighted, all rights reserved. Not fetched, not to be used as a text source anywhere in this codebase. May be mentioned to users as an external resource by name only.
- **WHO** — CC BY-NC-SA 3.0 IGO. Not fetched. The ShareAlike clause would force this entire knowledge base to be released under the same license if used; NonCommercial clause conflicts with SEVA's subscription model.
- **ICC A117.1 / ANSI** — referenced *by name* inside the ADA Access Board guide (e.g., the vertical grab bar requirement) as a point of comparison, but the standard itself is commercial and was not fetched or reproduced. Only note where the guide explicitly says "the ADA Standards do NOT require this, but ICC A117.1 does" — do not attribute ICC-only requirements to the ADA.

## Next steps for whoever builds the KB

1. Read each file above end to end.
2. For each hazard/recommendation found, write a KB item per the schema in the build instruction, in your own words (paraphrase, don't copy sentences verbatim — even for OGL content, which permits reuse but this project's style still prefers original phrasing for the `simple` field).
3. Set `source.verified_against_source: true` only after having actually located the passage in the corresponding file.
4. For the two remaining rooms with thin coverage (kitchen, living room), search CPSC.gov and FDA.gov directly and fetch/save any additional sources the same way these were — do not skip straight to `SEVA internal`.
5. Re-fetch file 06 properly before using any of its content.
