# -*- coding: utf-8 -*-
u"""정기후원 안내 — 랜딩(donate.action.or.kr)을 캠페이너스 코드 위젯용으로 굽습니다.

    python tools/build-donate.py

읽는 것 : action-landing 저장소의 index.html (아래 LANDING)
쓰는 것 : donate-guide.html (이 저장소 안)

★ 왜 스크립트인가
  랜딩은 다른 저장소에서 계속 고쳐집니다. 손으로 한 번 옮겨 두면 그때부터 두 벌이
  갈라집니다. 랜딩이 바뀌면 이걸 다시 돌리면 됩니다.

★ 무엇을 바꾸는가 (그대로 붙이면 캠페이너스 화면 전체가 깨집니다)
  1. 전역 CSS 를 껍데기 하나(#ah-donate) 안에 가둡니다. 랜딩에는 * · html · body · a
     규칙이 있어, 손대지 않으면 공통 상단·하단까지 물듭니다.
  2. 랜딩 자기 <header class="topbar"> 와 <footer> 를 걷어냅니다. 캠페이너스가 공통
     상단·하단을 따로 붙입니다 — 그대로 두면 머리가 둘이 됩니다.
  3. 떠 있는 후원 막대(.sticky-cta)를 걷어냅니다. 공통 상단·모바일 목차에 이미 떠 있는
     후원 버튼이 있어 둘이 겹칩니다.
  4. '지금, 시민행동'(최신 소식) 칸과 그 스크립트를 걷어냅니다. 2026-09-02 사용자
     결정입니다. 랜딩에서는 GitHub 봇이 구운 data/news.json 을 상대경로로 읽는데,
     캠페이너스 안에는 그 경로가 없습니다.
  5. 사진 상대경로(img/…)를 절대 주소로 바꿉니다 — IMG_BASE 를 보세요.
  6. 구글 애널리틱스 심는 부분을 걷어냅니다(캠페이너스에 이미 있으면 두 번 셉니다).
     gtag('event', …) 호출은 typeof 검사로 감싸여 있어 그대로 두어도 조용합니다.

★ 건드리지 않는 것
  스티비 구독 폼(주소록은 이미 홈과 같은 것으로 통일돼 있습니다) · 카카오 공유 ·
  본문 글과 사진 · 후원 신청서 링크.

★ 아직 사람이 봐야 하는 것 — 구운 파일 맨 위에도 적힙니다
  랜딩은 '현관'으로 쓰려고 만든 화면입니다. 안쪽 페이지가 되면 첫 화면(cover)처럼
  어색해지는 칸이 있습니다. 무엇을 남길지는 화면을 보고 정해야 합니다.
"""
import io
import os
import re
import sys

try:                                    # 윈도우 콘솔이 cp949 라 —·· 를 못 찍습니다
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# 랜딩 저장소는 이 저장소 밖에 있습니다. 환경변수로 덮어쓸 수 있습니다.
LANDING = os.environ.get(
    'ACTION_LANDING',
    os.path.join(os.path.expanduser('~'), 'action-landing', 'index.html'))

OUT = os.path.join(ROOT, 'donate-guide.html')

# ⚠️ 사진을 어디에 둘지 아직 정하지 않았습니다(2026-09-02 사용자: "고민중").
#    지금은 랜딩 도메인을 그대로 가리킵니다 — 그 주소가 살아 있어야 사진이 보입니다.
#    캠페이너스에 올리기로 하면 여기만 cdn.imweb.me 주소로 바꾸면 됩니다.
IMG_BASE = 'https://donate.action.or.kr/img'

# ⚠️ 캠페이너스 페이지 번호도 아직 없습니다. 정해지면 여기만 고치세요.
PAGE = '(번호 미정)'

SCOPE = 'ah-donate'


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


# ══════════════════════════════════════════════════════════════════
#  CSS 를 껍데기 안에 가두기
# ══════════════════════════════════════════════════════════════════

# 껍데기 자체가 되는 선택자들. 랜딩이 페이지 전체에 걸던 것이라
# 그대로 두면 캠페이너스 화면이 물듭니다.
ROOTISH = ('html', 'body', ':root', 'html body', 'body html')

remapped = []   # 어디로 옮겼는지 구운 파일 맨 위에 적으려고 모읍니다


def split_top_level(text, sep=','):
    u"""괄호 안의 쉼표는 건너뛰고 선택자 목록을 나눕니다( :is(a,b) 같은 것 )."""
    out, depth, buf = [], 0, []
    for ch in text:
        if ch in '([':
            depth += 1
        elif ch in ')]':
            depth -= 1
        if ch == sep and depth == 0:
            out.append(''.join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append(''.join(buf))
    return out


def scope_selector(sel):
    s = sel.strip()
    if not s:
        return sel
    low = s.lower()
    if low in ROOTISH:
        remapped.append(s)
        return '#%s' % SCOPE
    # `*` · `*::before` 처럼 전체를 겨냥한 것
    if s == '*' or s.startswith('*:'):
        return '#%s %s' % (SCOPE, s)
    if low.startswith('html ') or low.startswith('body '):
        remapped.append(s)
        return '#%s %s' % (SCOPE, s.split(' ', 1)[1].strip())
    return '#%s %s' % (SCOPE, s)


def scope_block(css):
    u"""중괄호 깊이를 세며 최상위 규칙만 골라 껍데기를 붙입니다.

    @font-face · @keyframes 는 선택자가 아니므로 통째로 지나갑니다.
    @media · @supports 는 안쪽을 다시 훑습니다.
    """
    out = []
    i, n = 0, len(css)
    while i < n:
        brace = css.find('{', i)
        if brace < 0:
            out.append(css[i:])
            break
        head = css[i:brace]
        depth, j = 0, brace
        while j < n:
            if css[j] == '{':
                depth += 1
            elif css[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        body = css[brace + 1:j]
        # 규칙 앞에 붙어 있던 주석은 그대로 두고 뒤쪽만 봅니다.
        # (주석까지 묶어서 보면 /* … */@media 를 선택자로 잘못 읽습니다.)
        lead, sel = '', head
        last_comment = head.rfind('*/')
        if last_comment >= 0:
            lead, sel = head[:last_comment + 2], head[last_comment + 2:]
        stripped = sel.strip()
        if stripped.startswith('@'):
            name = stripped.split()[0].lower()
            if name in ('@media', '@supports', '@layer'):
                out.append(head + '{' + scope_block(body) + '}')
            else:                       # @font-face · @keyframes · @import 등
                out.append(head + '{' + body + '}')
        else:
            sels = [scope_selector(p) for p in split_top_level(sel)]
            out.append(lead + ', '.join(sels) + ' {' + body + '}')
        i = j + 1
    return ''.join(out)


# ══════════════════════════════════════════════════════════════════
#  본문에서 걷어낼 것들
# ══════════════════════════════════════════════════════════════════

def cut(text, begin, end, label, dropped):
    u"""begin 으로 시작해 end 로 끝나는 첫 덩이를 잘라 냅니다."""
    i = text.find(begin)
    if i < 0:
        print(u'  ! 못 찾음 — %s' % label)
        return text
    j = text.find(end, i)
    if j < 0:
        print(u'  ! 끝을 못 찾음 — %s' % label)
        return text
    dropped.append(label)
    return text[:i] + text[j + len(end):]


def main():
    if not os.path.exists(LANDING):
        print(u'랜딩을 못 찾았습니다: %s' % LANDING)
        print(u'ACTION_LANDING 환경변수로 index.html 경로를 알려 주세요.')
        return 1

    src = read(LANDING)
    print(u'  읽음   %s' % LANDING)

    # ── <head> 에서 데려올 것만 고릅니다 ──
    #    글꼴(pretendard) · 스티비 폼 CSS · 카카오 공유 SDK 는 있어야 화면이 산다.
    #    <title>·og:·twitter: 메타는 캠페이너스 페이지 설정이 맡으므로 안 가져옵니다.
    #    구글 애널리틱스는 캠페이너스에 이미 있으면 두 번 세므로 안 가져옵니다.
    head = src[src.index(u'<head>'):src.index(u'</head>')]
    head_bits, ga = [], []
    for m in re.finditer(r'<link\b[^>]*>|<script\b[^>]*>.*?</script>', head, re.S):
        tag = m.group(0)
        if 'googletagmanager' in tag or 'dataLayer' in tag:
            ga.append(tag)
            continue
        head_bits.append(tag)
    if ga:
        dropped_head = u'구글 애널리틱스(<head> 에 있던 것) %d 덩이' % len(ga)
    else:
        dropped_head = None

    s0 = src.index(u'<style>') + len(u'<style>')
    s1 = src.index(u'</style>', s0)
    css = scope_block(src[s0:s1])

    b0 = src.index(u'<body>') + len(u'<body>')
    b1 = src.rindex(u'</body>')
    body = src[b0:b1]

    dropped = []
    if dropped_head:
        dropped.append(dropped_head)
    body = cut(body, u'<header class="topbar">', u'</header>',
               u'랜딩 자기 상단(topbar) — 공통 상단이 대신합니다', dropped)
    body = cut(body, u'<footer>', u'</footer>',
               u'랜딩 자기 하단(footer) — 공통 하단이 대신합니다', dropped)
    body = cut(body, u'<div class="sticky-cta"', u'</div>',
               u'떠 있는 후원 막대(sticky-cta) — 공통 것과 겹칩니다', dropped)
    body = cut(body, u'<section class="news" id="news">', u'</section>',
               u"'지금, 시민행동' 최신 소식 칸 — 2026-09-02 사용자 결정", dropped)
    body = cut(body, u'// ───── 지금, 시민행동 — RSS 연동 최신 소식 카드 ─────',
               u'// ───── 트랙 무한 루프', u'최신 소식 스크립트', dropped)

    # 위에서 '트랙 무한 루프' 머리말까지 함께 잘렸으니 되살립니다
    if u'───── 트랙 무한 루프' not in body:
        body = body.replace(
            u'// 카드를 한 세트 복제해',
            u'// ───── 트랙 무한 루프 (케이스 공통) ─────\n// 카드를 한 세트 복제해', 1)

    # 사진은 본문뿐 아니라 CSS 의 url('img/…') 에도 있습니다.
    pat = r'(?<=["\'(])img/([A-Za-z0-9_\-./]+)'
    rep = IMG_BASE.rstrip('/') + r'/\1'
    body, n1 = re.subn(pat, rep, body)
    css, n2 = re.subn(pat, rep, css)
    imgs = n1 + n2

    note = u'\n'.join(u'       · %s' % d for d in dropped)
    remap = u', '.join(sorted(set(remapped))) or u'없음'

    out = u"""<!-- CAMPAIGNERS:DONATE-GUIDE START -->
<!-- 후원 > 정기후원 안내 %(page)s — 코드 위젯 하나에 이 파일 전체를 붙입니다.
     공통 상단은 tools/parts/header.html, 공통 하단은 tools/parts/footer.html 이
     따로 맡습니다. 이 파일에는 둘 다 들어 있지 않습니다.

     ⚠️ 손으로 고치지 마세요. tools/build-donate.py 가 랜딩 저장소(action-landing)의
        index.html 을 읽어 굽습니다. 랜딩이 바뀌면 그걸 다시 돌리세요.

     걷어낸 것 —
%(note)s

     껍데기(#%(scope)s) 안으로 옮긴 전역 선택자 — %(remap)s
     사진 %(imgs)d 곳을 %(imgbase)s 로 바꿨습니다.
     ⚠️ 사진을 어디에 둘지는 아직 미정입니다(지금은 랜딩 도메인을 가리킵니다).

     ⚠️ 아직 사람이 볼 것 —
       · 랜딩은 '현관'으로 만든 화면입니다. 안쪽 페이지가 된 지금
         첫 화면(cover)·미션과 비전 같은 칸을 남길지 정해야 합니다.
       · 페이지 번호가 정해지면 홈과 푸터의 '정기후원 안내' · '후원 안내' 링크를
         donate.action.or.kr 에서 그 번호로 바꿔야 합니다(아직 안 바꿨습니다). -->

<!-- 랜딩 <head> 에서 데려온 것 — 글꼴 · 스티비 폼 CSS · 카카오 공유 SDK -->
%(head)s

<style>
%(css)s
</style>

<div id="%(scope)s">
%(body)s
</div>
<!-- CAMPAIGNERS:DONATE-GUIDE END -->
""" % {'page': PAGE, 'note': note, 'scope': SCOPE, 'remap': remap,
       'imgs': imgs, 'imgbase': IMG_BASE, 'css': css.strip(),
       'head': u'\n'.join(head_bits), 'body': body.strip()}

    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
    print(u'  걷어냄 %d 덩이' % len(dropped))
    print(u'  사진   %d 곳 → %s' % (imgs, IMG_BASE))
    print(u'  껍데기 #%s 로 옮긴 전역 선택자 — %s' % (SCOPE, remap))
    print(u'  씀     %s  (%d 바이트)' % (OUT, len(out.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
