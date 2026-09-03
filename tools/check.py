# -*- coding: utf-8 -*-
"""캠페이너스에 붙이기 전에 화면을 훑어보는 도구.

    python tools/check.py           내려받지 않고 파일만 읽어 봅니다
    python tools/check.py --net     바깥 주소를 실제로 열어 봅니다 (한 번에 여덟 개씩)

왜 필요한가
    **붙인 뒤에는 고치기가 비쌉니다.** 화면마다 코드 위젯을 손으로 붙이는 구조라,
    헤더 한 곳을 고쳐도 아홉 화면에 다시 붙여야 합니다. 그래서 붙이기 전에
    기계가 잡아낼 수 있는 것은 기계가 먼저 잡습니다.

무엇을 보나 (사람이 봐야 하는 것은 안 봅니다)
    1. 죽은 링크 — 미리보기가 모르는 안쪽 주소, 열리지 않는 바깥 주소
    2. 같은 문장이 두 번 — 화면의 큰 제목이 공통 푸터 띠와 겹치는지
    3. 낭독기·키보드 — alt 없는 그림, 이름 없는 단추, 겹치는 id, h1 개수
    4. '확인 필요' 딱지가 몇 곳 남았는지 (공개 전에 하나도 남으면 안 됩니다)

무엇을 못 보나
    · **가로로 넘치는 곳**은 브라우저가 있어야 잽니다. 이 도구로는 안 됩니다.
      재는 법은 README 의 2026-09-03 항목에 적어 두었습니다.
    · 글의 내용이 사실인지. 그건 사람이 봅니다.

⚠️ 주석 안의 주소는 세지 않습니다. 이 저장소는 지운 것을 주석으로 남겨 두므로,
   주석까지 세면 없앤 링크가 계속 살아 있는 것처럼 보입니다.
"""

import argparse
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:                      # 파이썬 3.6 아래
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARTS = os.path.join(HERE, 'parts')

# 캠페이너스가 이미 갖고 있는, 번호가 아닌 주소들. 미리보기에는 없는 것이 정상입니다.
CAMPAIGNERS = {'/aboutus', '/login', '/join', '/search'}

# 통째로 된 화면이 아니라 **조각**인 파일들. 캠페이너스에서 다른 코드와 이어 붙습니다.
# 그래서 h1 이 없는 것이 맞습니다.
FRAGMENTS = {
    'activity-budget-after-board.html',
    'activity-civic-after-board.html',
    'activity-local-after-board.html',
    'activity-budget-before-board.html',
    'activity-civic-before-board.html',
    'activity-local-before-board.html',
    'campaign-together-layout.html',
    'campaign-together-scripts.html',
    'redirect-snippet.html',
}

COMMENT = re.compile(r'<!--.*?-->', re.S)
SCRIPT = re.compile(r'<script\b.*?</script>', re.S | re.I)
LINK = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.I)
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')


def pages():
    """볼 파일들. 저장소 맨 위의 화면 + 공통 상단·하단."""
    out = []
    for name in sorted(os.listdir(ROOT)):
        if name.endswith('.html'):
            out.append(os.path.join(ROOT, name))
    for name in sorted(os.listdir(PARTS)):
        if name.endswith('.html'):
            out.append(os.path.join(PARTS, name))
    return out


def short(path):
    return os.path.relpath(path, ROOT).replace('\\', '/')


def known_routes():
    """미리보기가 아는 주소. preview.py 를 불러오지 않고 글자만 읽습니다
    (불러오면 서버가 뜨거나 argv 를 포트로 읽습니다)."""
    src = open(os.path.join(HERE, 'preview.py'), encoding='utf-8').read()
    keys = set()
    for block in ('ROUTES', 'STUBS'):
        m = re.search(block + r'\s*=\s*\{(.*?)\n\}', src, re.S)
        if m:
            keys.update(re.findall(r"'(/[^']*)'", m.group(1)))
    keys.update(re.findall(r"'(/[^']*/)':\s*\[", src))     # SIBLINGS (/dok/ 같은 것)
    return keys


# ───────────────────────── 1. 링크 ─────────────────────────

def collect_links():
    inside, outside = {}, {}
    for path in pages():
        raw = open(path, encoding='utf-8').read()
        live = COMMENT.sub('', raw)
        for url in LINK.findall(live):
            url = url.strip()
            if (not url or url[0] in '#?' or url.startswith(('data:', 'mailto:', 'tel:', 'javascript:'))):
                continue
            if "' +" in url or url.startswith("' "):        # 스크립트가 만드는 주소
                continue
            (outside if url.startswith(('http://', 'https://')) else inside)\
                .setdefault(url, set()).add(short(path))
    return inside, outside


def check_inside(inside, problems):
    known = known_routes()
    for url in sorted(inside):
        if not url.startswith('/'):
            continue                        # img/ohjieun.webp 같은 상대 주소는 붙일 때 정합니다
        head = url.split('?')[0].split('#')[0].rstrip('/') or '/'
        if head in known or head + '/' in known or head in CAMPAIGNERS:
            continue
        # 캠페이너스 게시판 번호(/26, /57 …)는 미리보기에 없는 것이 정상입니다.
        if re.fullmatch(r'/\d+', head):
            continue
        problems.append(('죽은 링크', '%s — 미리보기가 모르는 주소 (%s)'
                         % (url, ', '.join(sorted(inside[url])))))


def check_outside(outside, problems):
    import concurrent.futures as cf
    import ssl
    import urllib.error
    import urllib.request

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    def probe(url):
        for method in ('HEAD', 'GET'):
            req = urllib.request.Request(url.replace('&amp;', '&'),
                                         method=method, headers={'User-Agent': UA})
            try:
                with urllib.request.urlopen(req, timeout=20, context=ctx) as res:
                    return res.status
            except urllib.error.HTTPError as e:
                if method == 'HEAD' and e.code in (403, 405, 501):
                    continue
                return e.code
            except Exception:
                if method == 'HEAD':
                    continue
                return 0
        return 0

    with cf.ThreadPoolExecutor(max_workers=8) as pool:
        got = dict(zip(outside, pool.map(probe, outside)))

    for url in sorted(outside):
        code = got[url]
        if 200 <= code < 400:
            continue
        # 페이스북은 사람이 아닌 접속에 400 을 줍니다. 화면에서는 정상입니다.
        if 'facebook.com' in url and code == 400:
            continue
        problems.append(('열리지 않는 바깥 주소', '%s (%s) — %s'
                         % (url, code or 'TLS·DNS 실패', ', '.join(sorted(outside[url])))))


# ───────────────────────── 2. 겹치는 제목 ─────────────────────────

def footer_headings():
    raw = open(os.path.join(PARTS, 'footer.html'), encoding='utf-8').read()
    live = COMMENT.sub('', raw)
    return set(re.findall(r'<h[123][^>]*>(.*?)</h[123]>', live, re.S))


def norm(text):
    return re.sub(r'\s+', '', re.sub(r'<[^>]+>', '', text))


def check_dupes(problems):
    common = {norm(h) for h in footer_headings() if norm(h)}
    for path in pages():
        if path.startswith(PARTS):
            continue
        live = COMMENT.sub('', open(path, encoding='utf-8').read())
        live = SCRIPT.sub('', live)
        for h in re.findall(r'<h[123][^>]*>(.*?)</h[123]>', live, re.S):
            if norm(h) and norm(h) in common:
                problems.append(('같은 문장이 두 번',
                                 '%s — "%s" 가 공통 푸터 띠와 같습니다'
                                 % (short(path), norm(h)[:40])))


# ───────────────────────── 3. 낭독기·키보드 ─────────────────────────

class Look(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.no_alt = []
        self.ids = Counter()
        self.h = []
        self.nameless = []
        self.cur = None
        self.in_svg = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'svg':
            self.in_svg += 1
        if 'id' in a:
            self.ids[a['id']] += 1
        if tag == 'img':
            if 'alt' not in a:
                self.no_alt.append(a.get('src', '')[:60])
            elif self.cur:
                self.cur[2].append(a['alt'])      # 그림의 alt 가 링크 이름이 됩니다
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.h.append(int(tag[1]))
        if tag in ('button', 'a'):
            self.cur = [tag, a, []]

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == 'svg' and self.in_svg:
            self.in_svg -= 1
        if tag in ('button', 'a') and self.cur and self.cur[0] == tag:
            kind, a, txt = self.cur
            named = (''.join(txt).strip() or a.get('aria-label') or a.get('title')
                     or a.get('aria-labelledby'))
            if not named:
                self.nameless.append('%s(%s)' % (kind, (a.get('href') or a.get('class') or '')[:34]))
            self.cur = None

    def handle_data(self, data):
        if self.cur and not self.in_svg:
            self.cur[2].append(data)


def check_a11y(problems):
    for path in pages():
        if path.startswith(PARTS):
            continue
        raw = open(path, encoding='utf-8').read()
        head = open(os.path.join(PARTS, 'header.html'), encoding='utf-8').read()
        foot = open(os.path.join(PARTS, 'footer.html'), encoding='utf-8').read()
        look = Look()
        look.feed(head + raw + foot)          # 실제 화면과 같은 차림으로 봅니다

        if look.no_alt:
            problems.append(('alt 없는 그림', '%s — %d곳: %s'
                             % (short(path), len(look.no_alt), ', '.join(look.no_alt[:2]))))
        dup = [k for k, v in look.ids.items() if v > 1]
        if dup:
            problems.append(('겹치는 id', '%s — %s' % (short(path), ', '.join(dup[:5]))))
        if look.nameless:
            problems.append(('이름 없는 링크·단추', '%s — %d곳: %s'
                             % (short(path), len(look.nameless), ', '.join(look.nameless[:2]))))
        if os.path.basename(path) not in FRAGMENTS and look.h.count(1) == 0:
            problems.append(('h1 없음', '%s — 화면의 큰 제목 하나를 h1 로 두세요' % short(path)))


# ───────────────────────── 4. 확인 필요 딱지 ─────────────────────────

def count_tbd():
    rows = []
    for path in pages():
        n = open(path, encoding='utf-8').read().count('확인 필요')
        if n:
            rows.append((short(path), n))
    return sorted(rows, key=lambda r: -r[1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--net', action='store_true', help='바깥 주소를 실제로 열어 봅니다')
    args = ap.parse_args()

    problems = []
    inside, outside = collect_links()
    check_inside(inside, problems)
    if args.net:
        check_outside(outside, problems)
    check_dupes(problems)
    check_a11y(problems)

    print('화면 %d개 · 안쪽 주소 %d개 · 바깥 주소 %d개%s'
          % (len(pages()), len(inside), len(outside),
             '' if args.net else ' (바깥은 --net 을 줘야 열어 봅니다)'))
    print()

    if problems:
        last = None
        for kind, line in sorted(problems, key=lambda p: p[0]):   # 같은 갈래끼리 모읍니다
            if kind != last:
                print('── ' + kind)
                last = kind
            print('   ' + line)
    else:
        print('걸리는 것 없음.')

    tbd = count_tbd()
    if tbd:
        print()
        print('── 확인 필요 딱지 %d곳 (공개 전에 하나도 남으면 안 됩니다)'
              % sum(n for _, n in tbd))
        for name, n in tbd:
            print('   %-42s %d' % (name, n))

    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())
