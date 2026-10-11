#!/usr/bin/env python3
"""harness/fixtures/*/expected.json 대로 gate.py가 판정하는지 확인한다.

사용법: python harness/scripts/run_fixtures.py
모든 fixture가 기대대로면 exit 0.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(os.path.dirname(HERE), "fixtures")
GATE = os.path.join(HERE, "gate.py")


def main():
    failed = 0
    cases = sorted(d for d in os.listdir(FIX) if os.path.isfile(os.path.join(FIX, d, "expected.json")))
    for case in cases:
        with open(os.path.join(FIX, case, "expected.json"), encoding="utf-8") as f:
            exp = json.load(f)
        workdir = os.path.join(FIX, case, exp["workdir"])
        # G5는 p5-review.json을 쓰므로 이전 실행 결과가 남지 않게 지운다
        review = os.path.join(workdir, "p5-review.json")
        if os.path.exists(review):
            os.remove(review)
        proc = subprocess.run([sys.executable, GATE, exp["gate"], workdir] + exp["args"],
                              capture_output=True, text=True)
        try:
            got = json.loads(proc.stdout)
        except ValueError:
            got = {"pass": None, "return_to": None, "error": proc.stderr.strip()}
        ok = got["pass"] == exp["pass"] and got["return_to"] == exp["return_to"]
        failed += not ok
        print("%s %-16s %s  기대 pass=%s→%s / 결과 pass=%s→%s" % (
            "✅" if ok else "❌", case, exp["gate"], exp["pass"], exp["return_to"],
            got["pass"], got["return_to"]))
        if not ok:
            print("   ", json.dumps(got.get("violations") or got.get("error"), ensure_ascii=False))
        if os.path.exists(review):
            os.remove(review)
    print("\n%d/%d 통과" % (len(cases) - failed, len(cases)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
