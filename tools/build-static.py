# -*- coding: utf-8 -*-
"""검토용 정적 사이트를 만듭니다 (dist/).

    python tools/build-static.py

왜 필요한가
-----------
이 저장소의 .html 들은 **완성된 웹페이지가 아니라 조각**입니다.
캠페이너스 코드 위젯에 붙일 용도라 <html>·<head>·<body> 껍데기가 없습니다.
로컬에서는 tools/preview.py 가 그때그때 감싸 주지만, 어딘가에 올리려면
껍데기를 미리 씌워 진짜 HTML 로 뽑아 둬야 합니다. 그 일을 하는 스크립트입니다.

미리보기(preview.py)와 다른 점 셋
---------------------------------
1. **밑빠진 독상 데이터를 같이 담습니다.**
   원본 사이트에서 받아오면 CORS 에 막혀 지도와 표가 빈 채로 보입니다
   (그 CORS 고침 배포는 GPT 몫이고 아직 안 됐습니다). 그래서 awards.json 을
   dist/dok/data/ 에 복사하고, 같은 출처에서 읽도록 바꿔 넣습니다.
   → **데이터가 그때 그때가 아니라 만든 시점의 사본**입니다. 회차가 늘면 다시 돌리세요.

2. **맨 위에 '시안' 띠를 붙입니다.**
   남들에게 보여 주는 주소이므로, 이게 실제 홈페이지가 아니라는 것이
   한눈에 보여야 합니다. 화면 사이를 오갈 수 있는 링크도 겸합니다.
   (preview.py 의 검은 도구막대와 같은 자리지만 문구가 다릅니다.)

3. **없는 주소는 404 한 장으로 받습니다.**
   /aboutus · /26 · /23 같은 링크는 캠페이너스 실제 게시판이라 여기엔 없습니다.
   그냥 404 를 내면 보는 사람이 "고장 났나?" 합니다. 그래서 설명을 띄웁니다.

⚠️ dist/ 는 만들어지는 폴더입니다. 손으로 고치지 마세요. 다음에 돌리면 지워집니다.
⚠️ 원본 .html 은 건드리지 않습니다. 바꿔 넣는 것은 dist/ 안의 사본뿐입니다.
"""

import io
import os
import re
import shutil
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, 'dist')
HEADER_PART = os.path.join(HERE, 'parts', 'header.html')
FOOTER_PART = os.path.join(HERE, 'parts', 'footer.html')

# 밑빠진 독상 저장소 — 지도·수상 기록 데이터를 여기서 가져옵니다.
DOK_CANDIDATES = [
    os.path.join(os.path.dirname(ROOT), 'dokseong', 'public', 'data'),
    r'C:\Users\dbqke\dokseong\public\data',
]

# 만들 화면 — (원본 파일, 나갈 자리, 제목, 띠에서 켤 열쇠)
#
# 자리를 '49/index.html' 처럼 폴더+index 로 두는 이유:
# 정적 호스팅에서 /49 로 들어와도 그대로 열리고, 화면 안의 링크(/49)를 안 고쳐도 됩니다.
PAGES = [
    ('index.html',           'index.html',              '홈',                    'home'),
    ('issue.html',           'issue/index.html',        '캠페인',                  'issue'),
    ('activity-local.html',  '49/index.html',           '활동 › 지자체 감시',    'local'),
    # 2026-09-01 사용자 지시로 숨겼습니다 — 지운 것이 아닙니다. 확정되면 주석만 벗기세요.
    # ('activity-power.html',  'act-power/index.html',    '활동 › 권력감시',       'power'),
    ('activity-budget.html', '27/index.html',           '활동 › 예산감시',       'budget'),
    ('activity-civic.html',  '51/index.html',           '활동 › 시민참여',       'civic'),
    ('dok-history.html',     'dok-history/index.html',  '활동 › 밑빠진 독상',    'dok'),
    ('pb.html',              'pb/index.html',           '캠페인 › 참여예산 상담소', 'pb'),
    # 2026-09-01 사용자 지시로 숨겼습니다 — 지운 것이 아닙니다. 쓰게 되면 주석만 벗기세요.
    # ('library.html',         'library/index.html',      '자료실',                'lib'),
]

NAV = [
    ('home',   '/',             '홈'),
    ('issue',  '/issue/',       '캠페인'),
    ('local',  '/49',           '지자체 감시'),
    # 2026-09-01 사용자 지시로 숨겼습니다 — 지운 것이 아닙니다. 확정되면 주석만 벗기세요.
    # ('power',  '/act-power',    '권력감시'),
    ('budget', '/27',           '예산감시'),
    ('civic',  '/51',           '시민참여'),
    ('dok',    '/dok-history',  '밑빠진 독상'),
    ('pb',     '/pb/',          '참여예산 상담소'),
    # 2026-09-01 사용자 지시로 숨겼습니다 — 지운 것이 아닙니다. 쓰게 되면 주석만 벗기세요.
    # ('lib',    '/library',      '자료실'),
]

SHELL = u'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s · 함께하는 시민행동 홈 개편 시안</title>
<meta name="description" content="함께하는 시민행동 홈페이지 개편 시안입니다. 실제 홈페이지가 아닙니다.">
<!-- 검색엔진에 잡히면 안 됩니다. 실제 홈페이지가 아니라 검토용 시안입니다. -->
<meta name="robots" content="noindex,nofollow">
<style>
  html{-webkit-text-size-adjust:100%%}
  body{margin:0;background:#fff}
  /* ── 시안 띠 ──
     실제 홈페이지가 아니라는 표시이자, 화면 사이를 오가는 길입니다.
     자리에 붙박이(sticky)로 두지 않습니다. 그 밑의 진짜 헤더가 sticky 라서
     둘 다 붙으면 좁은 화면에서 내용이 볼 자리가 없어집니다. */
  .draft-bar{
    background:#062330;color:#cfe8f4;
    font:600 13px/1.5 'Pretendard Variable',Pretendard,'Noto Sans KR',-apple-system,sans-serif;
    padding:9px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px
  }
  .draft-bar b{color:#fff;font-weight:700;margin-right:4px}
  .draft-bar .tag{
    background:#9a5c06;color:#fff;border-radius:999px;padding:2px 9px;
    font-size:11px;font-weight:700;letter-spacing:.02em
  }
  .draft-bar a{color:#7fb7ce;text-decoration:none;white-space:nowrap}
  .draft-bar a:hover{color:#fff;text-decoration:underline;text-underline-offset:3px}
  .draft-bar a.on{color:#fff;text-decoration:underline;text-underline-offset:3px}
  .draft-bar .sep{opacity:.3}
  @media(max-width:700px){
    .draft-bar{font-size:12px;gap:5px 11px;padding:8px 12px}
  }
</style>
</head>
<body>

<nav class="draft-bar" aria-label="시안 안내">
  <span class="tag">시안</span>
  <b>함께하는 시민행동 홈 개편안</b>
  <span class="sep">|</span>
%(nav)s
</nav>

%(body)s

</body>
</html>
'''

NOT_FOUND = u'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>아직 없는 화면 · 함께하는 시민행동 홈 개편 시안</title>
<meta name="robots" content="noindex,nofollow">
<style>
  body{margin:0;background:#fff;color:#0b1e28;
    font:400 16px/1.7 'Pretendard Variable',Pretendard,'Noto Sans KR',-apple-system,sans-serif;
    word-break:keep-all}
  .box{max-width:600px;margin:14vh auto;padding:0 24px}
  .kick{font-size:12px;font-weight:700;letter-spacing:.14em;color:#0079a6;margin:0 0 10px}
  h1{font-size:clamp(24px,5vw,32px);letter-spacing:-.03em;margin:0 0 14px;line-height:1.3}
  p{color:#4a6473;margin:0 0 14px}
  .back{display:inline-block;margin-top:18px;font-weight:700;color:#0079a6;text-decoration:none}
  .back:hover{text-decoration:underline;text-underline-offset:3px}
</style>
</head>
<body>
  <div class="box">
    <p class="kick">아직 없는 화면</p>
    <h1>이 주소는 시안에 없습니다</h1>
    <p>지금 보고 계신 것은 <b>개편 시안</b>이라 일곱 화면만 만들어져 있습니다.
      소개 · 공지 · 발행물 같은 나머지 메뉴는 실제 홈페이지(action.or.kr)의 게시판이라
      여기엔 담겨 있지 않습니다. <b>고장이 아닙니다.</b></p>
    <p>만들어진 화면은 맨 위 띠에서 고르실 수 있습니다.</p>
    <a class="back" href="/">← 첫 화면으로</a>
  </div>
</body>
</html>
'''



def rebase(html, base):
    """사이트 안쪽 절대경로 앞에 기준경로를 붙입니다.

    왜 필요한가
    -----------
    깃허브 페이지스의 프로젝트 사이트는 주소가 `/저장소이름/` 아래로 들어갑니다.
    예: https://bada17.github.io/action-home-preview/
    그런데 화면 안의 링크는 `/49`, `/pb/` 처럼 최상위 절대경로라 그대로 두면
    `bada17.github.io/49` 로 나가 전부 깨집니다.

    그래서 사이트 안쪽을 가리키는 절대경로에만 기준경로를 붙입니다.

    건드리지 않는 것
      · https://... http://... //... (바깥 주소)
      · #... mailto: tel: (주소가 아님)
      · 상대경로 (이미 잘 찾아갑니다)

    캠페이너스에 올릴 때는 이 함수를 쓰지 않습니다(base='' ). 거기서는
    `/49` 가 실제 페이지 번호라 그대로여야 합니다.
    """
    if not base:
        return html
    b = '/' + base.strip('/')

    # href="/49" · src="/img/x.png" → href="/action-home-preview/49"
    # (?!/) 는 //cdn.example.com 같은 프로토콜 생략 주소를 건드리지 않으려는 것입니다.
    html = re.sub(r'\b(href|src)="/(?!/)', r'\1="%s/' % b, html)

    # 밑빠진 독상이 데이터를 읽어 가는 자리 (자바스크립트 문자열이라 위 규칙에 안 걸립니다)
    html = html.replace("var BASE = '/dok/';", "var BASE = '%s/dok/';" % b)

    return html


def strip_comments(html):
    """공개 주소에 실리면 안 되는 주석을 걷어냅니다.

    왜: 이 저장소의 화면에는 "⚠️ 대표 이미지가 나오면 교체" 같은 **내부 메모**가
    주석으로 잔뜩 달려 있습니다. 공개 주소에 올리면 그것도 같이 읽힙니다.
    보는 사람에게 필요한 '확인 필요' 딱지는 화면에 보이는 글자라 그대로 남습니다.

    걷어내는 것
      · HTML 주석  <!-- ... -->
      · CSS 주석   <style> 안의 /* ... */

    걷어내지 않는 것
      · 자바스크립트 주석 (<script> 안)
        정규식으로 지우려면 'https://' 의 // 나 정규식 리터럴 안의 /* 까지
        잘못 잡습니다. 코드가 한 글자만 잘려도 화면이 통째로 죽으므로 두고 봅니다.
        지워야 한다면 esbuild 같은 진짜 도구로 minify 하세요.
    """
    keep = []

    def stash(m):
        keep.append(m.group(0))
        # 원래 글에 없을 표시를 씁니다. 주석 지우기가 이걸 건드리면 안 됩니다.
        return '@@KEEP%d@@' % (len(keep) - 1)

    # 1. <script> 를 통째로 빼놓습니다 (안은 건드리지 않습니다)
    html = re.sub(r'<script\b[^>]*>.*?</script\s*>', stash, html,
                  flags=re.S | re.I)

    # 2. <style> 안의 CSS 주석만 지웁니다.
    #    CSS 에는 // 주석이 없고, 우리 CSS 의 content:"..." 안에 /* 가 없어
    #    HTML/JS 와 달리 정규식으로 지워도 안전합니다.
    def clean_style(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)
        body = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
        body = re.sub(r'\n[ \t]*\n[ \t]*\n+', '\n\n', body)
        return head + body + tail

    html = re.sub(r'(<style\b[^>]*>)(.*?)(</style\s*>)', clean_style, html,
                  flags=re.S | re.I)

    # 3. 남은 마크업에서 HTML 주석을 지웁니다
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)

    # 4. 주석이 있던 자리에 남는 빈 줄을 정리합니다
    html = re.sub(r'\n[ \t]*\n[ \t]*\n+', '\n\n', html)

    # 5. 빼놨던 <script> 를 도로 끼웁니다
    #    (문자열 치환이 아니라 함수로 넣어야 코드 안의 역슬래시가 안 망가집니다)
    html = re.sub(r'@@KEEP(\d+)@@', lambda m: keep[int(m.group(1))], html)
    return html


def read(p):
    with io.open(p, encoding='utf-8') as f:
        return f.read()


def write(p, s):
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def nav_html(current):
    out = []
    for key, href, name in NAV:
        on = ' class="on"' if key == current else ''
        aria = ' aria-current="page"' if key == current else ''
        out.append(u'  <a href="%s"%s%s>%s</a>' % (href, on, aria, name))
    return u'\n'.join(out)


def find_dok_data():
    for p in DOK_CANDIDATES:
        if os.path.isdir(p):
            return p
    return None


def main():
    # 기준경로 — 깃허브 페이지스처럼 /저장소이름/ 밑에 올릴 때 씁니다.
    #   python tools/build-static.py --base action-home-preview
    # 안 주면 최상위(/)에 올리는 것으로 봅니다.
    base = ''
    for i, a in enumerate(sys.argv):
        if a == '--base' and i + 1 < len(sys.argv):
            base = sys.argv[i + 1]
        elif a.startswith('--base='):
            base = a.split('=', 1)[1]
    if base:
        print(u'  기준경로: /%s/' % base.strip('/'))

    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)

    # ── 밑빠진 독상 데이터 ──
    # 원본 사이트에서 받아오면 CORS 에 막힙니다. 같이 담아 같은 출처에서 읽습니다.
    src = find_dok_data()
    dok_ok = False
    if src:
        shutil.copytree(src, os.path.join(DIST, 'dok', 'data'))
        n = len(os.listdir(os.path.join(DIST, 'dok', 'data')))
        print(u'  밑빠진 독상 데이터 %d개 담음  (%s)' % (n, src))
        dok_ok = True
    else:
        print(u'  ⚠ 밑빠진 독상 데이터를 못 찾았습니다. 지도와 표가 빈 채로 보입니다.')
        print(u'    찾아본 곳: %s' % ' / '.join(DOK_CANDIDATES))

    # ── 화면 ──
    for name, out_rel, title, key in PAGES:
        path = os.path.join(ROOT, name)
        if not os.path.isfile(path):
            print(u'  ⚠ %s 없음 — 건너뜁니다' % name)
            continue

        page_body = read(path)

        # 실제 캠페이너스에서는 공통 상단·하단 위젯이 따로 붙습니다.
        # 페이지 조각에는 둘 다 없으므로 정적 검토본을 만들 때만 앞뒤로 합칩니다.
        body = (read(HEADER_PART).rstrip() + '\n\n' + page_body.strip() + '\n\n' +
                read(FOOTER_PART).lstrip())

        # 밑빠진 독상만: 데이터를 같은 출처에서 읽게 바꿉니다.
        # 원본 파일은 그대로 두고 여기 나가는 사본만 바꿉니다
        # (캠페이너스에 붙일 때는 원본 사이트에서 받아와야 하므로).
        if name == 'dok-history.html' and dok_ok:
            old = "var BASE = isLocal ? '/dok/' : LIVE;"
            new = ("var BASE = '/dok/';   // 정적 시안: 데이터를 같이 담아 CORS 를 피합니다\n"
                   "  void isLocal; void LIVE;")
            if old in body:
                body = body.replace(old, new, 1)
            else:
                print(u'  ⚠ dok-history 의 BASE 줄을 못 찾았습니다 — 지도가 빌 수 있습니다')

        # 내부 메모가 공개 주소에 실리지 않게 주석을 걷어냅니다.
        before = len(body)
        body = strip_comments(body)
        page = strip_comments(SHELL % {'title': title, 'nav': nav_html(key), 'body': body})
        page = rebase(page, base)
        write(os.path.join(DIST, out_rel), page)
        print(u'  %-24s → dist/%-24s 주석 %d자 걷어냄'
              % (name, out_rel, before - len(body)))

    write(os.path.join(DIST, '404.html'), rebase(NOT_FOUND, base))
    print(u'  %-24s → dist/404.html' % '(없는 주소 안내)')

    # 정적 호스팅 대부분이 읽는 파일. 검색엔진에 잡히면 안 됩니다.
    write(os.path.join(DIST, 'robots.txt'), u'User-agent: *\nDisallow: /\n')

    # 깃허브 페이지스는 기본으로 Jekyll 을 돌려 _ 로 시작하는 것을 무시합니다.
    # 이 파일이 있으면 그냥 정적 파일로 그대로 내보냅니다.
    write(os.path.join(DIST, '.nojekyll'), u'')

    total = sum(len(files) for _, _, files in os.walk(DIST))
    print(u'\n  dist/ 에 파일 %d개. 이 폴더를 통째로 올리면 됩니다.' % total)
    print(u'  로컬에서 확인:  python -m http.server 8090 --directory dist')
    return 0


if __name__ == '__main__':
    sys.exit(main())
