#!/usr/bin/env python3
"""cally 디자인 하네스 게이트 판정기.

사용법:
    python harness/scripts/gate.py <G1|G2|G3|G5> work/S{n} [--page TEST]

- 규칙은 harness/rules.yaml, 디자인 값은 docs/design.md 에서 읽는다.
- 결과를 JSON으로 stdout에 출력한다. 통과 시 exit 0, 실패 시 exit 1, 사용 오류 시 exit 2.
- G5는 결과를 work/S{n}/p5-review.json 에도 쓴다.
"""
import fnmatch
import json
import os
import re
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RULES_PATH = os.path.join(ROOT, "harness", "rules.yaml")
GATE_STAGES = {"G1": ["P1"], "G2": ["P2"], "G3": ["P3"], "G5": ["P4", "P5"]}


# ---------------------------------------------------------------- YAML
# PyYAML이 없어도 돌도록 rules.yaml·design.md에 쓰인 범위만 지원하는 작은 파서.

def _strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def _split_top(s, sep=","):
    parts, depth, quote, buf = [], 0, None, ""
    for ch in s:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        elif ch == sep and depth == 0:
            parts.append(buf.strip())
            buf = ""
            continue
        buf += ch
    if buf.strip():
        parts.append(buf.strip())
    return parts


def _split_key(s):
    """'key: value' → (key, value). 따옴표 안의 콜론은 무시."""
    quote = None
    for i, ch in enumerate(s):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == ":" and (i + 1 == len(s) or s[i + 1] == " "):
            return _scalar(s[:i].strip()), s[i + 1:].strip()
    raise ValueError("YAML 키를 찾을 수 없음: " + s)


def _scalar(s):
    s = s.strip()
    if s == "":
        return None
    if s[0] in "\"'" and s[-1] == s[0]:
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        return [_scalar(p) for p in _split_top(s[1:-1])]
    if s.startswith("{") and s.endswith("}"):
        out = {}
        for p in _split_top(s[1:-1]):
            k, v = _split_key(p)
            out[k] = _scalar(v)
        return out
    if s in ("true", "false"):
        return s == "true"
    if s in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


def yaml_load(text):
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except ImportError:
        pass
    lines = []
    for raw in text.splitlines():
        line = _strip_comment(raw)
        if line.strip():
            lines.append((len(line) - len(line.lstrip(" ")), line.strip()))

    def block(i, indent):
        if lines[i][1].startswith("- ") or lines[i][1] == "-":
            out = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("-"):
                out.append(_scalar(lines[i][1][1:]))
                i += 1
            return out, i
        out = {}
        while i < len(lines) and lines[i][0] == indent:
            k, v = _split_key(lines[i][1])
            i += 1
            if v == "" and i < len(lines) and lines[i][0] > indent:
                out[k], i = block(i, lines[i][0])
            else:
                out[k] = _scalar(v)
        return out, i

    return block(0, lines[0][0])[0] if lines else {}


def load_design_tokens(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        raise ValueError("design.md 앞부분 YAML을 찾을 수 없음")
    fm = yaml_load(m.group(1))

    def px(v):
        return float(str(v).replace("px", "").strip())

    return {
        "colors": {str(v).lower() for v in fm.get("colors", {}).values()},
        "rounded": {px(v) for v in fm.get("rounded", {}).values()},
        "spacing": {px(v) for v in fm.get("spacing", {}).values()},
    }


# ---------------------------------------------------------------- 공통

def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def screen_of(workdir):
    m = re.search(r"S([1-3])$", os.path.basename(os.path.normpath(workdir)))
    return "S" + m.group(1) if m else None


def violation(rule, value, node_id=None, kind="value"):
    return {"rule": rule, "node_id": node_id, "value": value, "kind": kind}


def scope_check(gate, workdir, rules):
    """state.json의 stage_started_at 이후 바뀐 파일이 그 단계 범위 안인지 검사."""
    state_path = os.path.join(workdir, "state.json")
    if not os.path.exists(state_path):
        return [], "state.json 없음 — 범위 검사 생략"
    started = read_json(state_path).get("stage_started_at", {})
    stages = GATE_STAGES[gate]
    times = [started[s] for s in stages if s in started]
    if not times:
        return [], "stage_started_at 없음 — 범위 검사 생략"
    since = min(datetime.fromisoformat(t).timestamp() for t in times)
    sc = rules.get("scope_check", {})
    allowed = list(sc.get("always_allowed", []))
    for s in stages:
        allowed += sc.get(s, [])
    out = []
    for dirpath, _, files in os.walk(workdir):
        for fn in files:
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, workdir)
            if os.path.getmtime(full) <= since:
                continue
            ok = any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat.replace("/**", "/*"))
                     or (pat.endswith("/**") and rel.startswith(pat[:-3] + os.sep))
                     for pat in allowed)
            if not ok:
                out.append(violation("scope_check", rel, kind="scope"))
    return out, None


# ---------------------------------------------------------------- 게이트

def gate_g1(workdir, cfg, screen):
    v = []
    refs_p = os.path.join(workdir, "p1-references.json")
    items_p = os.path.join(workdir, "p1-items.json")
    for p in (refs_p, items_p):
        if not os.path.exists(p):
            v.append(violation("file_missing", os.path.basename(p)))
    if v:
        return v
    refs, items = read_json(refs_p), read_json(items_p)
    if len(refs) < cfg["references_min"]:
        v.append(violation("references_min", len(refs)))
    urls = set()
    for r in refs:
        url = str(r.get("url", ""))
        urls.add(url)
        if cfg.get("references_url_domain") and cfg["references_url_domain"] not in url:
            v.append(violation("references_url_domain", url))
    if len(items) < cfg["items_min"]:
        v.append(violation("items_min", len(items)))
    for idx, it in enumerate(items):
        for f in cfg["item_required_fields"]:
            if not str(it.get(f, "")).strip():
                v.append(violation("item_required_fields", "items[%d].%s" % (idx, f)))
        if cfg.get("source_url_in_references") and it.get("source_url") and it["source_url"] not in urls:
            v.append(violation("source_url_in_references", it["source_url"]))
        if it.get("story") and it["story"] not in cfg["story_allowed"]:
            v.append(violation("story_allowed", it["story"]))
        if it.get("kind") and it["kind"] not in cfg["kind_allowed"]:
            v.append(violation("kind_allowed", it["kind"]))
    return v


def gate_g2(workdir, cfg, screen):
    p = os.path.join(workdir, "p2-spec.md")
    if not os.path.exists(p):
        return [violation("file_missing", "p2-spec.md")]
    lines = [l.rstrip() for l in open(p, encoding="utf-8").read().splitlines()]
    v = [violation("required_headings", h) for h in cfg["required_headings"] if h not in lines]
    if not v:
        start = lines.index("## 대상 유저스토리")
        section = []
        for l in lines[start + 1:]:
            if l.startswith("## "):
                break
            section.append(l)
        if not re.search(r"\bU[1-5]\b", "\n".join(section)):
            v.append(violation("story_reference", "## 대상 유저스토리에 U1~U5 없음"))
    return v


def gate_g3(workdir, cfg, screen):
    p = os.path.join(workdir, "p3-approval.json")
    if not os.path.exists(p):
        return [violation("file_missing", "p3-approval.json")]
    a = read_json(p)
    v = []
    if a.get("approved") is not True:
        v.append(violation("approved", a.get("approved")))
    if cfg["pass_if"].get("utterance_not_empty") and not str(a.get("utterance", "")).strip():
        v.append(violation("utterance_not_empty", a.get("utterance")))
    return v


def _segments(name):
    return [s for s in re.split(r"[/\-_\s.]+", name.lower()) if s]


def check_n_rules(nodes, screen, rules, page_mode):
    v = []
    for key, r in rules.get("n_rules", {}).items():
        applies = r.get("applies_to")
        applies = applies if isinstance(applies, list) else [applies]
        if not page_mode and screen not in applies:
            continue
        names = [n.get("name", "") for n in nodes]
        for layer in r.get("must_have_layers", []):
            if layer not in names and not page_mode:
                v.append(violation(key, "레이어 없음: " + layer, kind="n_rule"))
        for n in nodes:
            segs = _segments(n.get("name", ""))
            for bad in r.get("forbidden_layer_name_segments", []):
                if bad in segs:
                    v.append(violation(key, "금지 레이어 이름: " + n.get("name", ""), n.get("id"), "n_rule"))
            text = n.get("characters") or ""
            for bad in r.get("forbidden_text", []):
                if bad in text:
                    v.append(violation(key, "금지 텍스트: " + bad, n.get("id"), "n_rule"))
        lim = r.get("max_layers_matching")
        if lim:
            cnt = sum(1 for nm in names if fnmatch.fnmatch(nm, lim["pattern"]))
            if cnt > lim["max"]:
                v.append(violation(key, "%s 레이어 %d개 (최대 %d)" % (lim["pattern"], cnt, lim["max"]), kind="n_rule"))
    return v


def gate_g5(workdir, cfg, screen, rules, page=None):
    p = os.path.join(workdir, cfg["input"])
    if not os.path.exists(p):
        return [violation("file_missing", cfg["input"])]
    dump = read_json(p)
    tokens = load_design_tokens(os.path.join(ROOT, rules["tokens_from"]))
    dv = cfg["design_values"]
    radius_ok = tokens["rounded"]
    space_ok = tokens["spacing"] | {float(x) for x in dv["gap_padding"].get("also_allow", [])}
    fonts_ok = set(cfg["font_family_allowed"])

    if page:
        frames = [f for f in dump.get("frames", []) if dump.get("page") == page or f.get("page") == page]
    else:
        target = "%s-final" % screen
        frames = [f for f in dump.get("frames", []) if f.get("name") == target]
        if not frames:
            return [violation("frame_missing", target)]

    v = []
    for fr in frames:
        size = cfg["frame_size"]
        if (fr.get("width"), fr.get("height")) != (size["width"], size["height"]):
            v.append(violation("frame_size", "%sx%s" % (fr.get("width"), fr.get("height")), fr.get("id")))
        nodes = fr.get("nodes", [])
        for n in nodes:
            nid = n.get("id")
            for key in ("fills", "strokes"):
                for paint in n.get(key, []):
                    if paint.get("type", "SOLID") == "SOLID":
                        hx = str(paint.get("hex", "")).lower()
                        if hx not in tokens["colors"]:
                            v.append(violation("fill_stroke_hex", hx, nid))
                    elif paint.get("type") != "IMAGE":
                        v.append(violation("fill_type", paint.get("type"), nid))
            for r in n.get("cornerRadii", []) or ([n["cornerRadius"]] if n.get("cornerRadius") is not None else []):
                if float(r) not in radius_ok:
                    v.append(violation("corner_radius", r, nid))
            for key in ("itemSpacing", "paddingLeft", "paddingRight", "paddingTop", "paddingBottom"):
                if n.get(key) is not None and float(n[key]) not in space_ok:
                    v.append(violation("gap_padding", "%s=%s" % (key, n[key]), nid))
            for fam in n.get("fontFamilies", []):
                if fam not in fonts_ok:
                    v.append(violation("font_family", fam, nid))
        v += check_n_rules(nodes, screen, rules, page_mode=bool(page))
    return v


# ---------------------------------------------------------------- main

def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    page = None
    if "--page" in argv:
        i = argv.index("--page")
        page = argv[i + 1] if i + 1 < len(argv) else None
        args = [a for a in args if a != page]
    if len(args) != 2 or args[0] not in GATE_STAGES:
        print(__doc__, file=sys.stderr)
        return 2
    gate, workdir = args
    rules = yaml_load(open(RULES_PATH, encoding="utf-8").read())
    cfg = rules["gates"][gate]
    screen = screen_of(workdir)
    if screen is None and not page:
        print("작업 폴더 이름은 S1/S2/S3 으로 끝나야 함: " + workdir, file=sys.stderr)
        return 2

    if gate == "G1":
        v = gate_g1(workdir, cfg, screen)
    elif gate == "G2":
        v = gate_g2(workdir, cfg, screen)
    elif gate == "G3":
        v = gate_g3(workdir, cfg, screen)
    else:
        v = gate_g5(workdir, cfg, screen, rules, page)

    sv, note = scope_check(gate, workdir, rules)
    v += sv
    passed = not v
    if passed:
        return_to = None
    elif gate == "G5":
        return_to = cfg["on_fail"]["n_rule_any"] if any(x["kind"] == "n_rule" for x in v) \
            else cfg["on_fail"]["design_values_only"]
    else:
        return_to = cfg["on_fail"]

    result = {"gate": gate, "screen": screen, "page": page, "pass": passed,
              "return_to": return_to, "violations": v}
    if note:
        result["note"] = note
    if gate == "G5" and not page:
        with open(os.path.join(workdir, cfg["output"]), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
