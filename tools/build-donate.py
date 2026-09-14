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

★ 첫 화면 임시 보관 — 구운 파일 맨 위에도 적힙니다
  새 첫 화면(cover)과 바로 아래 '시민행동이 하는 일' 띠는 사진과 문구가 확정될 때까지
  원본의 <template id="cover-draft"> 안에 보존되어 화면에는 나오지 않습니다.
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

# 후원 폼 칸을 걷어내면서 #donate 로 가던 링크들이 갈 곳을 잃습니다. 도너스로 바로 보냅니다.
# (공통 상단의 떠 있는 후원 버튼 .ah-float 이 쓰는 것과 같은 주소입니다.)
DONUS_URL = 'https://secure.donus.org/withaction0909/pay/step1'


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


def comment_mask(css):
    u"""주석 `/* … */` 안이면 1 인 표를 만듭니다.

    ⚠️ 왜 필요한가 — 주석 안에 중괄호가 있을 수 있습니다. CSS 설명을 적다 보면
       `.num { display:inline-block }` 처럼 규칙을 예로 드는 일이 흔한데,
       중괄호를 그냥 세면 그 예시에서 규칙이 시작된 줄 알고 껍데기를 엉뚱한
       자리에 붙입니다. 실제로 2026-09-14 에 그렇게 돼서
       `#ah-donate #ah-donate .trust-cell …` 이라는, 아무것도 안 맞는 선택자가
       만들어졌습니다(자기 자신의 자손일 수는 없으니까요).
    """
    mask = bytearray(len(css))
    i = 0
    while True:
        a = css.find('/*', i)
        if a < 0:
            break
        b = css.find('*/', a + 2)
        end = len(css) if b < 0 else b + 2
        for k in range(a, end):
            mask[k] = 1
        if b < 0:
            break
        i = end
    return mask


def scope_block(css):
    u"""중괄호 깊이를 세며 최상위 규칙만 골라 껍데기를 붙입니다.

    @font-face · @keyframes 는 선택자가 아니므로 통째로 지나갑니다.
    @media · @supports 는 안쪽을 다시 훑습니다.
    주석 안의 중괄호는 세지 않습니다 — comment_mask 를 보세요.
    """
    out = []
    mask = comment_mask(css)
    i, n = 0, len(css)

    def find_brace(frm):
        k = css.find('{', frm)
        while k >= 0 and mask[k]:
            k = css.find('{', k + 1)
        return k

    while i < n:
        brace = find_brace(i)
        if brace < 0:
            out.append(css[i:])
            break
        head = css[i:brace]
        depth, j = 0, brace
        while j < n:
            if mask[j]:
                j += 1
                continue
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

def cut(text, begin, end, label, dropped, keep_end=False):
    u"""begin 으로 시작해 end 로 끝나는 첫 덩이를 잘라 냅니다.

    keep_end=True 면 end 표시 자체는 남깁니다 — 그 표시가 잘라 낼 덩이의 것이
    아니라 **뒤에 이어지는 코드의 첫 줄**일 때 씁니다.
    """
    i = text.find(begin)
    if i < 0:
        print(u'  ! 못 찾음 — %s' % label)
        return text
    j = text.find(end, i)
    if j < 0:
        print(u'  ! 끝을 못 찾음 — %s' % label)
        return text
    dropped.append(label)
    return text[:i] + text[j if keep_end else j + len(end):]


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
    # ⚠️ 끝 표시('트랙 무한 루프')는 잘라 낼 덩이가 아니라 **다음 코드의 첫 줄**입니다.
    #    keep_end 없이 자르면 그 줄의 앞머리만 사라지고 ' (케이스·뉴스 공통) ─────'
    #    가 코드 한복판에 남습니다. 그러면 SyntaxError 하나로 이 화면의 스크립트가
    #    통째로 죽습니다 — 숫자 카운트업도, 사례 트랙도 안 돕니다.
    #    2026-09-14 에 실제로 /74 에서 그러고 있었습니다.
    body = cut(body, u'// ───── 지금, 시민행동 — RSS 연동 최신 소식 카드 ─────',
               u'// ───── 트랙 무한 루프', u'최신 소식 스크립트', dropped, keep_end=True)

    # ══════════════════════════════════════════════════════════════
    #  후원 폼 칸과 뉴스레터 칸을 걷어냅니다 (2026-09-14 사용자 결정)
    #
    #  "필요없을듯. 걍 후원하기가 홈화면처럼 옆에 따라다니게" —
    #  후원은 공통 상단이 띄우는 떠 있는 버튼(.ah-float, 도너스로 바로 감)이
    #  맡고, 뉴스레터 신청은 홈에 같은 폼이 있습니다. 두 벌을 두지 않습니다.
    #  ⚠️ 랜딩(donate.action.or.kr)에는 그대로 남습니다 — 여기서만 걷어냅니다.
    # ══════════════════════════════════════════════════════════════
    body = cut(body, u'<section class="donate" id="donate">', u'</section>',
               u"'미래를 만드는 힘 +1!' 후원 폼 칸 — 2026-09-14 사용자 결정", dropped)
    body = cut(body, u'<section class="newsletter" id="newsletter">', u'</section>',
               u"'시민행동의 소식을 받아보세요' 뉴스레터 칸 — 2026-09-14 사용자 결정", dropped)
    body = cut(body, u'<script type="text/javascript" src="https://resource.stibee.com/subscribe/stb_subscribe_form.js">',
               u'</script>', u'스티비 폼 스크립트 (뉴스레터 칸과 함께)', dropped)

    # 칸이 사라졌으니 그 칸을 만지던 자바스크립트도 함께 걷습니다.
    # ⚠️ 안 걷으면 document.getElementById('donate-go').addEventListener 에서
    #    바로 죽습니다. 캠페이너스는 코드 위젯들의 스크립트를 <script> 하나로
    #    이어 붙이므로, 여기서 한 번 죽으면 **공통 상단 코드까지 같이 죽습니다.**
    body = cut(body, u'// ───── 상태 ─────', u'// ───── 사례 카드 클릭 추적 ─────',
               u'후원 폼·뉴스레터 스크립트 (금액 고르기 · 임팩트 문구 · 구독 추적)',
               dropped, keep_end=True)

    # 첫 임팩트 문구를 채우던 한 줄. 함수가 사라졌으니 이것도 걷습니다
    # (남겨 두면 ReferenceError 로 그 뒤 코드가 통째로 안 돕니다).
    body, nu = re.subn(r'\n*^updateImpact\(\);\s*$', u'', body, count=1, flags=re.M)
    if nu:
        dropped.append(u'updateImpact() 첫 호출 — 그 함수와 함께 없앴습니다')

    # 남은 '3가지 방법' 칸의 뉴스레터 카드 — 갈 곳이 없어졌으니 함께 걷고 둘로 만듭니다.
    body, nc = re.subn(
        r'\s*<div class="cta-card">\s*<div class="cta-num">2</div>.*?</div>'
        r'\s*(?=<div class="cta-card cta-card-primary">)',
        u'\n      ', body, count=1, flags=re.S)
    if nc:
        body = body.replace(u'<div class="cta-num">3</div>', u'<div class="cta-num">2</div>', 1)
        body = body.replace(u'함께하는 <span class="accent">3가지 방법</span>',
                            u'함께하는 <span class="accent">2가지 방법</span>', 1)
        dropped.append(u"'3가지 방법' 중 뉴스레터 카드 — 뉴스레터 칸이 없어져 둘로 줄였습니다")

    # 후원 폼이 없어졌으니 #donate 로 가던 링크는 도너스로 바로 보냅니다.
    # ⚠️ 자바스크립트 안의 선택자가 먼저입니다. 이것까지 통째로 바꾸면
    #    'a[href="…" target="_blank" …]' 이라는 말이 안 되는 선택자가 되어
    #    querySelectorAll 이 던지고, 그 뒤 코드가 전부 안 돕니다.
    body = body.replace(
        u"""document.querySelectorAll('a[href="#donate"]')""",
        u"""document.querySelectorAll('a[href^="https://secure.donus.org/"]')""")
    body, nd = re.subn(r'href="#donate"',
                       u'href="%s" target="_blank" rel="noopener"' % DONUS_URL, body)
    if nd:
        dropped.append(u'#donate 로 가던 링크 %d 개를 도너스 주소로 바꿨습니다' % nd)
    if u'href="#newsletter"' in body:
        print(u'  ! 갈 곳 없는 #newsletter 링크가 남았습니다 — 확인하세요')

    # 스티비 폼이 없어졌으니 그 CSS 도 부르지 않습니다(쓸모없는 바깥 요청 하나).
    if u'stb_subscribe' not in body:
        before = len(head_bits)
        head_bits = [t for t in head_bits if 'stibee' not in t]
        if len(head_bits) < before:
            dropped.append(u'스티비 폼 CSS — 뉴스레터 칸과 함께 필요 없어졌습니다')

    # 사진은 본문뿐 아니라 CSS 의 url('img/…') 에도 있습니다.
    pat = r'(?<=["\'(])img/([A-Za-z0-9_\-./]+)'
    rep = IMG_BASE.rstrip('/') + r'/\1'
    body, n1 = re.subn(pat, rep, body)
    css, n2 = re.subn(pat, rep, css)
    imgs = n1 + n2

    # 스티비 폼이 준 코드에는 모달 바탕 두 개의 id 가 **똑같습니다**
    # (개인정보 모달·광고성 모달 둘 다 stb_form_modal_bg). 한 화면에 같은 id 가
    # 둘이면 안 되고, 홈(index.html)에서는 이미 고쳐 두었습니다.
    # 스티비 스크립트는 getElementById 로 먼저 나오는 하나만 잡으므로 하는 일은
    # 달라지지 않습니다 — 광고성 모달은 원래도 바탕을 눌러 닫히지 않았습니다.
    body, n3 = re.subn(r'(class="stb_form_ad_modal_bg"\s+id=")stb_form_modal_bg(")',
                       r'\1stb_form_ad_modal_bg\2', body)
    if n3:
        dropped.append(u'겹치던 id 하나를 갈았습니다 — '
                       u'광고성 모달 바탕 stb_form_modal_bg → stb_form_ad_modal_bg')

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

     ⚠️ 임시 보관 중 —
       · 새 첫 화면(cover)과 바로 아래 '시민행동이 하는 일' 띠는 사진과 문구가
         확정될 때까지 <template id="cover-draft"> 안에 있어 화면에 나오지 않습니다.
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
