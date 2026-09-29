# NEO Science · GreenPrint

**Repository:** nudgeeducation/neo-science — the working home for the Nudge Education Online science curriculum, operated by Nudge Education Ltd.

Built on the maths pattern (`nudgeeducation/neo-maths`): git is canonical, the site publishes, Google Classroom is derived.

## What is here now

| Path | What it is |
|---|---|
| `docs/data/curriculum-foundations-oak.json` | Manifest of the Foundations science course as sequenced by Oak National Academy (KS3 science, all strands, Years 7–9: 41 units, 290 lessons). Every lesson links to its Oak learner page and educator page. |
| `scripts/oak_manifest.py` | Generates such a manifest from the [Oak curriculum ontology](https://github.com/oaknational/oak-curriculum-ontology). Re-run when Oak publishes a new release. |
| `docs/` | The future GitHub Pages site, where NEO-fied lessons will live (same build as neo-maths). |

## How the manifest is used

The Classroom sync script in `nudgeeducation/neo-curriculum-vault/classroom/` reads this manifest and mirrors it into the "Science | Foundation | Master (Oak)" classroom: one topic per unit, one material per lesson. Re-running it after any change updates the classroom in place.

## NEO-fying a lesson

1. Author the interactive lesson page under `docs/lessons/<unit>/<nn>-<slug>.html` (use the neo-maths build as the mould).
2. In the manifest, replace that lesson's `url` with `"file": "lessons/<unit>/<nn>-<slug>.html"` and set `"source": "neo"`.
3. Commit, push, re-run the sync. The Classroom material now points at the NEO page; the Oak educator resources stay linked in the description.

## Regenerating from Oak

```bash
git clone https://github.com/oaknational/oak-curriculum-ontology.git /tmp/oak
pip install rdflib
python3 scripts/oak_manifest.py --ontology /tmp/oak --subject the-sciences \
  --files science-key-stage-3.ttl the-sciences-programme-structure.ttl \
  --programme-prefix programme-science-year-group- --years 7 8 9 \
  --stage Foundations --site-title "NEO Science · Foundations (Oak)" \
  --teacher-programme science-secondary-ks3 --pupil-programme "science-secondary-year-{year}" \
  --out docs/data/curriculum-foundations-oak.json
```

Pin to an Oak release (the ontology repo tags them) rather than tracking `main`, and record which release a manifest was built from in the commit message.

## Licences

Code and tooling: MIT (see `LICENSE`). Oak National Academy sequencing, lesson titles and outcomes: © Oak National Academy, [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). NEO-authored curriculum content: see `CONTENT_LICENSE.md`.

---

Nudge Education Online · [nudgeeducation.online](https://nudgeeducation.online) · neo@nudgeeducation.online
