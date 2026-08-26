# -*- coding: utf-8 -*-
"""dok-history.html 이 원본에서 얼마나 어긋났는지 알려 준다.

배경
  '활동 > 밑빠진 독상' 페이지(dok-history.html)는 밑빠진 독상 사이트에서
  CSS 와 지도 코드를 골라 온 것이다.

  **수상 기록(awards.json)은 복사하지 않는다.** 화면이 뜰 때 원본에서 받아온다.
  그래서 회차가 늘어나는 것은 저절로 따라온다 — 이 도구를 돌릴 필요가 없다.

  이 도구가 잡는 것은 **디자인·코드가 바뀐 경우**다.
  원본에서 색을 바꾸거나 지도 코드를 고치면 여기만 옛날 것으로 남는다.

쓰는 법
  python tools/sync-dok.py

  어긋난 곳이 있으면 무엇이 달라졌는지 알려 준다. 고치는 것은 사람이 판단한다
  (여기서는 제보·투표 부분을 일부러 뺐기 때문에, 다른 것이 정상이다).
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINE = os.path.join(HERE, "dok-history.html")

# 밑빠진 독상 저장소. 옆에 없으면 알려만 주고 끝낸다.
ORIGIN = os.path.normpath(os.path.join(HERE, "..", "dokseong", "public", "index.html"))

# 일부러 안 가져온 것들 — 이 접두어가 원본에만 있는 건 정상이다
SKIPPED = ("dok-report", "dok-camp", "dok-vote", "dok-join", "dok-sample",
           "dok-deadline", "dok-donate", "dok-hero-actions", "dok-btn-main", "dok-btn-line")


def read(path):
    if not os.path.isfile(path):
        return None
    return io.open(path, encoding="utf-8").read()


def style_of(html):
    m = re.search(r"<style>(.*?)</style>", html, re.S)
    return m.group(1) if m else ""


def selectors(css):
    """셀렉터 이름만 모은다. 값(색·크기)까지 비교하면 잡음이 너무 많다."""
    out = set()
    for sel in re.findall(r"([^{}]+)\{", css):
        sel = re.sub(r"/\*.*?\*/", " ", sel, flags=re.S).strip()
        if not sel or sel.startswith("@"):
            continue
        for part in sel.split(","):
            part = " ".join(part.split())
            if part:
                out.add(part)
    return out


def main():
    mine = read(MINE)
    origin = read(ORIGIN)

    if mine is None:
        print("dok-history.html 이 없습니다:", MINE)
        return 1
    if origin is None:
        print("밑빠진 독상 저장소를 못 찾았습니다:", ORIGIN)
        print("저장소를 이 폴더 옆에 두거나, 이 파일의 ORIGIN 경로를 고치세요.")
        return 1

    a = selectors(style_of(origin))
    b = selectors(style_of(mine))

    # 원본에 새로 생겼는데 우리 쪽에 없는 것 (일부러 뺀 것은 제외)
    missing = sorted(s for s in (a - b) if not any(k in s for k in SKIPPED))
    # 우리 쪽에만 있는 것 (이 페이지 전용 dokh- 규칙은 정상)
    extra = sorted(s for s in (b - a) if "dokh-" not in s)

    print("원본 셀렉터 %d개 / 이 페이지 %d개" % (len(a), len(b)))
    print()

    if missing:
        print("원본에 있는데 이 페이지엔 없는 규칙 %d개" % len(missing))
        print("  (제보·투표 쪽이면 무시하세요. 지도·역대·숫자 쪽이면 가져와야 합니다)")
        for s in missing[:40]:
            print("   -", s)
        if len(missing) > 40:
            print("   ... 외 %d개" % (len(missing) - 40))
        print()

    if extra:
        print("이 페이지에만 있는 규칙 %d개 (원본에서 사라졌을 수 있음)" % len(extra))
        for s in extra[:20]:
            print("   +", s)
        print()

    if not missing and not extra:
        print("어긋난 곳 없습니다.")

    print("참고: 수상 기록(awards.json)은 복사본이 아니라 원본에서 받아옵니다.")
    print("      회차가 늘어난 것은 이 도구와 상관없이 저절로 반영됩니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
