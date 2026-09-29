#!/usr/bin/env python3
"""Build a NEO curriculum.json manifest from the Oak curriculum ontology.

Same shape as neo-maths/docs/data/curriculum.json, so the same Classroom sync
script consumes it. Each lesson carries Oak learner and educator URLs; when a
lesson is NEO-fied, replace `url` with a site-relative `file` and re-sync.

Usage:
  python3 oak_manifest.py --ontology /path/to/oak-curriculum-ontology \
      --subject the-sciences --files science-key-stage-3.ttl the-sciences-programme-structure.ttl \
      --programme-prefix programme-science-year-group- --years 7 8 9 \
      --stage Foundations --site-title "NEO Science · Foundations (Oak)" \
      --teacher-programme science-secondary-ks3 --pupil-programme science-secondary-year-{year} \
      --out curriculum.json

Oak content: © Oak National Academy, Open Government Licence v3.0.
"""
import argparse, json, re, sys
import rdflib
from rdflib import RDF, RDFS, URIRef

ONT = "https://w3id.org/uk/oak/curriculum/ontology/"

def clean(x):
    return re.sub(r"\s+", " ", str(x)).strip() if x is not None else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ontology", required=True)
    ap.add_argument("--subject", required=True, help="folder under data/subjects")
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--programme-prefix", required=True, help="e.g. programme-science-year-group-")
    ap.add_argument("--years", nargs="+", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--site-title", required=True)
    ap.add_argument("--teacher-programme", required=True, help="e.g. science-secondary-ks3")
    ap.add_argument("--pupil-programme", required=True, help="e.g. science-secondary-year-{year}")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    g = rdflib.Graph()
    for f in a.files:
        g.parse(f"{a.ontology}/data/subjects/{a.subject}/{f}", format="turtle")

    def val(s, p):
        for o in g.objects(s, URIRef(p)):
            return clean(o)
        return None
    def label(s): return val(s, str(RDFS.label)) or ""
    def strand_of(unit):
        # scheme → subject label (Biology / Chemistry / Physics); fall back to thread label
        for sch in g.objects(unit, URIRef(ONT + "isUnitOf")):
            l = label(sch)
            m = re.match(r"^(\w+)", l)
            if m: return m.group(1)
        return ""

    units_out, seen = [], set()
    for year in a.years:
        prog = URIRef(f"https://w3id.org/uk/oak/curriculum/{a.programme_prefix}{year}")
        # find programme by local name suffix (namespace may differ)
        progs = [s for s in g.subjects(RDF.type, URIRef(ONT + "Programme")) if str(s).endswith(f"{a.programme_prefix}{year}")]
        if not progs:
            sys.exit(f"programme not found: {a.programme_prefix}{year}")
        prog = progs[0]
        incs = []
        for inc in g.objects(prog, URIRef(ONT + "hasUnitVariantInclusion")):
            pos = val(inc, ONT + "sequencePosition")
            uv = next(g.objects(inc, URIRef(ONT + "includesUnitVariant")), None)
            if uv is not None and pos: incs.append((int(pos), uv))
        for pos, uv in sorted(incs):
            unit = next(g.objects(uv, URIRef(ONT + "isUnitVariantOf")), None)
            if unit is None: continue
            uslug = val(unit, ONT + "slug")
            uid = f"y{year}-{pos:02d}-{uslug}"
            if uid in seen: continue
            seen.add(uid)
            lessons = []
            for linc in g.objects(uv, URIRef(ONT + "hasLessonInclusion")):
                lpos = val(linc, ONT + "sequencePosition")
                les = next(g.objects(linc, URIRef(ONT + "includesLesson")), None)
                if les is not None and lpos: lessons.append((int(lpos), les))
            lrows = []
            for lpos, les in sorted(lessons):
                lslug = val(les, ONT + "slug")
                outcome = ""
                for plo in g.objects(les, URIRef(ONT + "hasPupilLessonOutcome")):
                    outcome = label(plo) or val(plo, str(RDFS.comment)) or ""
                pupil_prog = a.pupil_programme.format(year=year)
                lrows.append({
                    "id": f"{uslug}-{lpos:02d}-{lslug}",
                    "num": f"Lesson {lpos:02d}",
                    "title": label(les),
                    "url": f"https://www.thenational.academy/pupils/programmes/{pupil_prog}/units/{uslug}/lessons/{lslug}",
                    "teacherUrl": f"https://www.thenational.academy/teachers/programmes/{a.teacher_programme}/units/{uslug}/lessons/{lslug}",
                    "outcome": outcome,
                    "status": "live",
                    "source": "oak",
                    "cornerstones": [],
                })
            strand = strand_of(unit)
            units_out.append({
                "id": uid,
                "title": label(unit),
                "topic": f"Y{year}.{pos:02d} · {label(unit)}" + (f" ({strand})" if strand else ""),
                "stage": a.stage,
                "year": int(year),
                "sequence": pos,
                "strand": strand,
                "oakSlug": uslug,
                "oakUnitUrl": f"https://www.thenational.academy/teachers/programmes/{a.teacher_programme}/units/{uslug}",
                "summary": val(unit, str(RDFS.comment)) or "",
                "whyThisWhyNow": val(unit, ONT + "whyThisWhyNow") or "",
                "lessons": lrows,
            })

    out = {
        "version": "0.1",
        "brand": "NEO by Nudge Education",
        "site_title": a.site_title,
        "attribution": "Sequencing, lesson titles and outcomes adapted from the Oak National Academy curriculum, © Oak National Academy, licensed under the Open Government Licence v3.0.",
        "units": units_out,
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    n = sum(len(u["lessons"]) for u in units_out)
    print(f"{len(units_out)} units, {n} lessons → {a.out}")

if __name__ == "__main__":
    main()
