# -*- coding: utf-8 -*-
"""공통 부품(헤더 · 맨 아래)을 각 화면에 심습니다.

왜 이렇게 하는가
----------------
캠페이너스는 화면마다 코드 위젯을 따로 붙이는 구조라, 여섯 화면이
스타일시트나 헤더를 **공유할 수 없습니다.** 그래서 같은 내용을 여섯 번
복사해 넣어야 합니다. 손으로 복사하면 반드시 어긋납니다(실제로 색이
#0087b8 과 #0079a6 으로 갈렸던 적이 있습니다).

그래서 원본은 tools/parts/header.html 한 곳에만 두고, 이 스크립트가
각 .html 의 표시 사이를 그 내용으로 덮어씁니다.

    <!-- PART:header --> ... <!-- /PART:header -->

표시가 없는 파일에는 뿌리 요소(<div id="...">) 바로 앞에 새로 만들어
넣습니다. 헤더가 뿌리 **밖**에 있어야 하는 이유는 header.html 맨 위
주석에 적어 두었습니다(overflow:hidden 과 position:sticky 문제).

쓰는 법
-------
    python tools/build-parts.py            # 전부 다시 심기
    python tools/build-parts.py --check    # 안 고치고 어긋난 곳만 알려 주기
"""

import io
import os
import re
import sys

# 윈도우 콘솔은 기본이 cp949 라 한글·기호가 섞이면 print 에서 터집니다.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PART = os.path.join(HERE, 'parts', 'header.html')
FOOT = os.path.join(HERE, 'parts', 'footer.html')

BEGIN = '<!-- PART:header -->'
END = '<!-- /PART:header -->'

# 맨 아래(후원 띠 + 푸터). 2026-08-31 사용자 지시:
#   "이건 소개나 모든 페이지 밑에 같은 형식으로 가자.
#    있는 모든 페이지에 똑같이 넣고 새로 만드는 페이지에도 무조건 넣어"
# → 새 화면을 만들면 아래 PAGES 에 한 줄 더하기만 하면 됩니다. 빠뜨리지 마세요.
FBEGIN = '<!-- PART:footer -->'
FEND = '<!-- /PART:footer -->'

# 맨 아래 부품을 받지 않는 화면.
# 홈은 맨 아래가 [CTA 둘] → [뉴스레터] → [푸터] 로 더 길고, 2026-08-31 사용자가
# "홈만 예전 그대로 되돌린다"를 골랐습니다. 그래서 홈은 자기 푸터를 그대로 씁니다.
# ⚠️ 그 대신 **푸터를 고치면 두 곳을 고쳐야 합니다** — 이 부품과 index.html.
NO_FOOT = {'index.html'}

# 화면 → (뿌리 요소 id, 헤더에서 켤 메뉴 값)
#
# 'here' 값은 header.html 의 data-nav 와 짝을 맞춘 것입니다.
# 'home' 은 아무것도 켜지 않는다는 뜻입니다(홈에서는 현재 위치 표시가 필요 없음).
PAGES = [
    ('index.html',           'action-home-v2', 'home'),
    ('activity-local.html',  'act',            'act-local'),
    ('activity-power.html',  'act',            'act-power'),
    ('activity-budget.html', 'act',            'act-budget'),
    ('activity-civic.html',  'act',            'act-civic'),
    ('dok-history.html',     'dok',            'act-dok'),
    ('issue.html',           'iss',            'issue'),
    ('pb.html',              'pb',             'pb'),
    ('library.html',         'lib',            'library'),
    ('sign.html',            'sign',           'issue'),
]


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def block_for(here):
    """헤더 원본을 읽고, 이 화면에 맞게 data-here 만 바꿔서 돌려줍니다."""
    part = read(PART).rstrip('\n')
    part = part.replace('<header id="ah-nav" data-here="home">',
                        '<header id="ah-nav" data-here="%s">' % here, 1)
    return '%s\n%s\n%s' % (BEGIN, part, END)


def foot_block():
    """맨 아래 부품 원본을 그대로 돌려줍니다(화면마다 다른 곳이 없습니다)."""
    return '%s\n%s\n%s' % (FBEGIN, read(FOOT).rstrip('\n'), FEND)


def inject_foot(text, block):
    """표시 사이를 덮어쓰거나, 표시가 없으면 파일 맨 끝에 붙입니다.

    맨 끝에 붙이는 이유: 뿌리 요소(<div id="act"> 등)가 닫힌 **뒤**에 와야
    전체 폭이 제대로 나옵니다. 뿌리는 overflow:hidden 이라 그 안에 두면
    좌우로 못 펼칩니다(헤더와 같은 이유). 파일 끝의 <script> 뒤에 와도
    화면에는 아무 차이가 없습니다.
    """
    if FBEGIN in text and FEND in text:
        pat = re.compile(re.escape(FBEGIN) + '.*?' + re.escape(FEND), re.S)
        return pat.sub(lambda m: block, text, count=1), 'replaced'
    return text.rstrip('\n') + '\n\n' + block + '\n', 'appended'


def inject(text, block, root_id):
    """표시 사이를 덮어쓰거나, 표시가 없으면 뿌리 앞에 새로 넣습니다."""
    if BEGIN in text and END in text:
        pat = re.compile(re.escape(BEGIN) + '.*?' + re.escape(END), re.S)
        return pat.sub(lambda m: block, text, count=1), 'replaced'

    anchor = '<div id="%s"' % root_id
    i = text.find(anchor)
    if i < 0:
        return None, 'no-anchor'
    return text[:i] + block + '\n\n' + text[i:], 'inserted'


def main():
    check = '--check' in sys.argv
    if not os.path.exists(PART):
        print('원본이 없습니다: %s' % PART)
        return 1

    changed, problems = [], []
    for name, root_id, here in PAGES:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            # pb.html 처럼 아직 안 만든 화면은 조용히 건너뜁니다.
            print('  - %-22s 없음 (건너뜀)' % name)
            continue

        old = read(path)
        new, how = inject(old, block_for(here), root_id)
        if new is None:
            problems.append('%s: 뿌리 요소 <div id="%s"> 를 못 찾았습니다' % (name, root_id))
            continue

        # 맨 아래(후원 띠 + 푸터) — 홈을 뺀 여덟 화면이 같은 것을 씁니다.
        if name not in NO_FOOT:
            new, how_f = inject_foot(new, foot_block())
            if how == 'replaced' and how_f != 'replaced':
                how = how_f

        if new == old:
            print('  = %-22s 그대로' % name)
            continue

        changed.append(name)
        if check:
            print('  ! %-22s 어긋남 (%s)' % (name, how))
        else:
            write(path, new)
            print('  * %-22s %s (here=%s)' % (name, '덮어씀' if how == 'replaced' else '새로 넣음', here))

    for p in problems:
        print('  ⚠ %s' % p)

    if check and changed:
        print('\n%d 개 화면이 원본과 다릅니다. python tools/build-parts.py 를 돌리세요.' % len(changed))
        return 1
    if problems:
        return 1
    print('\n원본은 두 곳뿐입니다:')
    print('  헤더      tools/parts/header.html')
    print('  맨 아래   tools/parts/footer.html   (후원 띠 + 푸터)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
