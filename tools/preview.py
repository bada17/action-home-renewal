# -*- coding: utf-8 -*-
"""개편안을 브라우저에서 보는 미리보기 서버.

    python tools/preview.py            →  http://127.0.0.1:8777/

왜 필요한가
    이 저장소의 .html 은 통째로 된 문서가 아니라 캠페이너스 코드 위젯에 붙일
    **조각**입니다. <head> 가 없어서 파일을 그냥 열면 한글이 깨집니다.
    이 서버가 charset·viewport 를 씌워서 내보냅니다.

    또 하나. 활동/캠페인 페이지가 서로를 /49, /act-power 같은 주소로 가리키기
    때문에, 파일을 직접 열면 링크가 전부 깨집니다. 여기서는 그 주소를 실제
    파일에 이어 줍니다.

이어 둔 주소
    /               홈                    index.html
    /77             캠페인 목록             issue.html
    /49             활동 > 지자체 감시    activity-local.html
    /act-power      활동 > 권력감시       activity-power.html
    /27     활동 > 예산감시       activity-budget.html
    /51             활동 > 시민참여       activity-civic.html
    /76             활동 > 밑빠진 독상    dok-history.html
    /library        자료실                library.html
    /dok/           밑빠진 독상 원본      옆 저장소를 그 자리에서 읽습니다
    /80             참여예산 상담소       pb.html
    /pb-old/        상담소 옛 초안        옆 저장소를 그 자리에서 읽습니다

    /dok/ 과 /pb-old/ 는 **복사하지 않습니다.** 원본 저장소를 그대로 물려 주므로
    거기서 고치면 여기서도 바로 보입니다.
"""

import io
import os
import sys
import posixpath
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HEADER_PART = os.path.join(HERE, 'parts', 'header.html')
FOOTER_PART = os.path.join(HERE, 'parts', 'footer.html')
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8777

# 옆 저장소. 없으면 그 주소만 안내가 뜨고 나머지는 그대로 돕니다.
SIBLINGS = {
    '/dok/': [
        os.path.join(os.path.dirname(ROOT), 'dokseong', 'public'),
        r'C:\Users\dbqke\dokseong\public',
    ],
    # 2026-08-27: /80 은 이 저장소의 새 상담소(pb.html)가 씁니다.
    # 옛 초안은 견줘 보려고 /pb-old/ 로 옮겨 두었습니다.
    '/pb-old/': [
        r'C:\Users\dbqke\participatory-budget',
        os.path.join(os.path.dirname(ROOT), 'participatory-budget'),
    ],
}

ROUTES = {
    '/': 'index.html',
    '/69': 'index.html',
    '/77': 'issue.html',
    '/77/': 'issue.html',
    '/49': 'activity-local.html',
    '/act-power': 'activity-power.html',
    '/27': 'activity-budget.html',
    '/27/': 'activity-budget.html',
    '/51': 'activity-civic.html',
    '/76': 'dok-history.html',
    '/76/': 'dok-history.html',
    '/80': 'pb.html',
    '/80/': 'pb.html',
    '/library': 'library.html',
    '/library/': 'library.html',
    '/sign': 'sign.html',
    '/sign/': 'sign.html',
}

# 아직 화면이 없는 주소. 404 대신 "무엇이 없는지"를 알려 줍니다.
STUBS = {
    '/search': ('통합검색은 캠페이너스가 합니다',
                '헤더의 검색칸은 <b>/search?keyword=...</b> 로 보냅니다. 실제 action.or.kr 의 '
                '검색 폼에서 가져온 주소·이름이라 그대로 두면 캠페이너스 통합검색이 받습니다. '
                '미리보기에는 그 검색 기능이 없어 이 안내만 뜹니다 — 결함이 아닙니다.'),
    '/52': ('활동 전체', '활동 다섯을 모아 보여 줄 목록 화면입니다. 아직 안 만들었습니다.'),
    '/23': ('발행물', '게시판입니다. 자료실은 이제 /library 에 따로 있습니다.'),
    '/24': ('뉴스룸', '보도자료 게시판입니다.'),
    '/25': ('뉴스레터', '스티비 구독 페이지입니다.'),
    '/26': ('소식', '공지 게시판입니다.'),
    '/57': ('예산 모니터링', '게시판입니다. 활동 &gt; 예산감시의 글이 여기 올라가 있습니다.'),
    '/78': ('2026 하반기 밑빠진 독상', '캠페이너스 내부 캠페인 페이지입니다.'),
    '/78/': ('2026 하반기 밑빠진 독상', '캠페이너스 내부 캠페인 페이지입니다.'),
    '/79': ('10만원 예산편성', '캠페이너스 내부 캠페인 페이지입니다.'),
    '/79/': ('10만원 예산편성', '캠페이너스 내부 캠페인 페이지입니다.'),
}

SHELL = u'''<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s — 시민행동 개편안 미리보기</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
  html,body{margin:0;padding:0;background:#fff}
  /* 캠페이너스에 붙었을 때를 흉내 내려고 가운데 폭을 잡아 둡니다.
     실제 캠페이너스 폭과 다를 수 있으니 최종 확인은 /69 에서 하세요. */
  body{font-family:'Pretendard Variable',Pretendard,sans-serif}
  /* 미리보기 표시줄 — 실제 화면에는 없습니다 */
  #pv{position:fixed;left:0;right:0;top:0;z-index:9999;display:flex;gap:2px;
      background:#0b1e28;padding:6px 10px;font:600 12px/1 'Pretendard Variable',sans-serif;
      overflow-x:auto;scrollbar-width:none}
  #pv::-webkit-scrollbar{display:none}
  #pv a{color:#9fd7ee;text-decoration:none;padding:6px 11px;border-radius:999px;white-space:nowrap}
  #pv a:hover{background:#123344;color:#fff}
  #pv a.on{background:#00afec;color:#04222e}
  #pv b{color:#5b7f92;padding:6px 8px;white-space:nowrap;font-weight:700}
  body{padding-top:34px}
</style>
</head><body>
<nav id="pv">
  <b>미리보기</b>
  <a href="/"%(a_home)s>홈</a>
  <a href="/77"%(a_issue)s>캠페인</a>
  <b>활동</b>
  <a href="/49"%(a_local)s>지자체 감시</a>
  <a href="/act-power"%(a_power)s>권력감시</a>
  <a href="/27"%(a_budget)s>예산감시</a>
  <a href="/51"%(a_pb51)s>참여예산</a>
  <a href="/76"%(a_dok)s>밑빠진 독상</a>
  <b>캠페인</b>
  <a href="/80"%(a_pb)s>참여예산 상담소</a>
  <a href="/sign"%(a_sign)s>서명</a>
  <a href="/library"%(a_lib)s>자료실</a>
  <b>원본</b>
  <a href="/pb-old/">상담소 옛 초안</a>
  <a href="/dok/"%(a_dokorg)s>독상 사이트</a>
</nav>
%(body)s
</body></html>
'''

STUB_BODY = u'''<div style="max-width:640px;margin:14vh auto;padding:0 24px;
  font-family:'Pretendard Variable',sans-serif;color:#0b1e28;line-height:1.7">
  <p style="font-size:12px;font-weight:700;letter-spacing:.14em;color:#0079a6;margin:0 0 10px">아직 없는 화면</p>
  <h1 style="font-size:30px;letter-spacing:-.03em;margin:0 0 14px">%s</h1>
  <p style="font-size:15.5px;color:#4a6473;margin:0 0 26px">%s</p>
  <p style="font-size:14px;color:#7d95a3;margin:0">주소 <code>%s</code> · 미리보기 전용입니다.
  캠페이너스에 올릴 때는 실제 페이지 번호로 바꿔야 합니다.</p>
  <p style="margin-top:30px"><a href="/" style="color:#0079a6;font-weight:700">← 홈으로</a></p>
</div>'''

TITLES = {
    '/': '홈', '/69': '홈', '/77': '캠페인', '/77/': '캠페인',
    '/49': '활동 > 지자체 감시', '/act-power': '활동 > 권력감시',
    '/27': '활동 > 예산감시', '/51': '활동 > 시민참여',
    '/76': '활동 > 밑빠진 독상', '/76/': '활동 > 밑빠진 독상',
    '/80': '캠페인 > 참여예산 상담소', '/80/': '캠페인 > 참여예산 상담소',
    '/library': '자료실', '/library/': '자료실',
    '/sign': '캠페인 > 서명', '/sign/': '캠페인 > 서명',
}

MIME = {
    '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
    '.woff': 'font/woff', '.woff2': 'font/woff2', '.ico': 'image/x-icon',
    '.txt': 'text/plain; charset=utf-8',
}


# ─────────────────────────────────────────────────────────────
# ?data=demo  —  "게시판이 붙으면 이렇게 된다"를 눈으로 보는 장치
#
# tools/data/action-rss.xml (진짜 action.or.kr 게시판 글)을 읽어
# window.AH_DATA 를 만들어 화면 앞에 끼워 넣습니다.
# 미리보기 전용입니다. 실제 화면과는 상관없습니다.
#
# ★ 2026-09-01 정정: RSS 에 사진이 **있습니다.** 항목마다 <media:content url="...">
#   로 대표 이미지가 옵니다(49건 전부). 예전 주석은 "사진이 없다"고 적어 두었는데
#   틀린 말이었고, 그 때문에 소식 카드를 색 타일로만 그렸습니다. 이제 받아 씁니다.
# ─────────────────────────────────────────────────────────────
BOARD_NAME = {'51': '주민참여예산', '27': '일반 활동', '57': '예산 모니터링',
              '26': '소식', '23': '발행물', '25': '뉴스룸'}


def demo_data():
    import re, json
    f = os.path.join(ROOT, 'tools', 'data', 'action-rss.xml')
    if not os.path.isfile(f):
        return ''
    xml = io.open(f, encoding='utf-8').read()
    items = re.findall(r'<item>(.*?)</item>', xml, re.S)

    try:
        from html import unescape
    except ImportError:
        from HTMLParser import HTMLParser
        unescape = HTMLParser().unescape

    def img(block):
        # <media:content url="https://cdn.imweb.me/thumbnail/..." type="image/png" />
        m = re.search(r'<media:content[^>]*url="([^"]+)"', block)
        return unescape(m.group(1).strip()) if m else ''

    def pick(block, tag):
        m = re.search(r'<%s>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</%s>' % (tag, tag), block, re.S)
        # ★ 엔티티를 풀어서 넘깁니다. RSS 는 주소를 '&amp;' 로 주는데 그대로 넘기면
        #   화면 코드가 한 번 더 감싸 '&amp;amp;' 가 되어 링크가 깨집니다.
        return unescape(m.group(1).strip()) if m else ''

    MON = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
           'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}

    def ymd(pub):
        # 'Tue, 25 Aug 2026 09:00:00 +0900'  ->  '2026.08.25'
        m = re.search(r'(\d{1,2})\s+(\w{3})\s+(\d{4})', pub)
        if not m:
            return pub[:16]
        return '%s.%s.%02d' % (m.group(3), MON.get(m.group(2), '01'), int(m.group(1)))

    news = []
    for b in items[:8]:
        link = pick(b, 'link')
        bid = re.search(r'/(\d+)/', link)
        date = ymd(pick(b, 'pubDate'))
        news.append({
            'title': pick(b, 'title'),
            'url': link,
            'date': date,
            'board': BOARD_NAME.get(bid.group(1) if bid else '', '게시판'),
            'img': img(b),          # media:content — 진짜 대표 이미지입니다
        })

    # 2026-09-01: '더 걷힐 세금, 어디에 쓸래?' 는 사용자 지시로 캠페인에서 뺐습니다.
    issues = [
        {'title': '2026 하반기 밑빠진 독상',
         'lead': '세금이 새는 현장을 시민이 제보하고, 그중 최악의 사업을 함께 고릅니다.',
         'url': '/78', 'mark': '독상',
         'tile': '#062330', 'cat': '밑빠진 독상', 'due': '2026-09-15'},
        {'title': '10만원 예산편성',
         'lead': '내 몫의 예산 10만원을 어디에 쓸지 직접 짜 봅니다.',
         'url': '/79', 'mark': '편성',
         'tile': '#0d4f66', 'cat': '예산감시'},
        {'title': '참여예산 상담소',
         'lead': '참여예산위원들이 현장에서 부딪히는 고민을 모아 함께 풀어 봅니다.',
         'url': '/80', 'mark': '상담', 'tile': '#0b4a5e', 'cat': '시민참여'},
    ]

    for it in issues:
        it['kind'] = u'캠페인'

    # ── 첫 화면에 함께 오르는 '중요한 글' ──────────────────────────
    #   고르기 : 제목 맨 앞에 [주요] 를 붙인 글. 최신순 두 건까지.
    #   알약   : 무엇이라고 부를지. 아래 순서로 정합니다.
    #            1) [주요:논평] 처럼 표식에 적어 두면 그 말
    #            2) 안 적었으면 제목 머리말에서 — [논평] / 활동가 수첩_ / 뉴스 브리핑 -
    #            3) 그것도 없으면 게시판 이름 (일반 활동 · 예산 모니터링 …)
    #   표식과 머리말은 화면에 찍을 때 떼어 냅니다.
    #   자세한 것은 CONTENT.md 의 '첫 화면에 올릴 글 고르기'.
    def head_word(t):
        """제목 머리말을 떼어 (알약글자, 남은제목) 으로 돌려줍니다. 없으면 (None, 제목)."""
        m = re.match(r'\s*\[\s*([^\]]{1,10})\s*\]\s*(.+)$', t)          # [논평] 제목
        if m:
            return m.group(1).strip(), m.group(2).strip()
        m = re.match(r'\s*(.{2,10}?)\s*(?:_|\s-\s)\s*(.+)$', t)           # 활동가 수첩_제목
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return None, t.strip()

    def lead_post(block, forced=None):
        t = pick(block, 'title')
        link = pick(block, 'link')
        bid = re.search(r'/(\d+)/', link)
        board = BOARD_NAME.get(bid.group(1) if bid else '', u'게시판')
        kind, title = head_word(t)
        return {
            'kind': forced or kind or board,
            'title': title,
            'url': link,
            'lead': ymd(pick(block, 'pubDate')) + u' · ' + board,
            'img': img(block),
            'tile': '#3d5765',
        }

    MARK = u'[주요]'
    picked = []
    for b_ in items:
        t = pick(b_, 'title').strip()
        if not t.startswith(u'[주요'):
            continue
        m = re.match(r'\[주요(?::\s*([^\]]{1,10}))?\]\s*(.*)$', t)
        if not m:
            continue
        rest = m.group(2)
        # 표식만 떼어 낸 나머지로 다시 판단합니다.
        b2 = b_.replace(u'<title>' + pick(b_, 'title') + u'</title>',
                        u'<title>' + rest + u'</title>')
        picked.append(lead_post(b2, forced=(m.group(1) or u'').strip() or None))
        if len(picked) >= 2:
            break

    # ⚠️ 받아 둔 49건에는 [주요] 가 붙은 글이 아직 하나도 없습니다.
    #    미리보기에서 모양을 보시라고, 없을 때는 **맨 위 글 한 건**에 담당자가
    #    표식을 붙였다고 치고 올립니다. 미리보기 전용입니다.
    #    (맨 위 글이 '[논평]미래대응기금…' 이라 알약은 규칙 2 로 '논평'이 됩니다.)
    if not picked and items:
        picked = [lead_post(items[0])]
    issues = issues + picked

    # ── 종료된 캠페인 (issue.html 의 '종료' 탭) ──
    #    씨앗에 있는 실제 두 건입니다. 지어낸 값이 아닙니다.
    issues_done = [
        {'title': '2026 지방선거 서울시민행동',
         'lead': '시민사회가 함께 정책을 제안하고 후보자의 답을 기록했습니다.',
         'url': '/27/?idx=170844085&bmode=view', 'mark': '선거',
         'tile': '#3d5765', 'when': '2026년 6월 종료'},
        {'title': '한강버스 주민감사청구',
         'lead': '경제성 근거 없이 추진된 사업에 주민감사를 청구했고, 감사 결과가 나왔습니다.',
         'url': '/27/?idx=172916152&bmode=view',
         'img': 'https://cdn.imweb.me/thumbnail/20260810/50abe1798d723.png',
         'tile': '#3d5765', 'when': '2026년 8월 종료'},
    ]

    # ── 활동 다섯 장 ──
    #    글 목록만 게시판에서 받아 채웁니다. 이게 실제로 제일 먼저 붙을 자리입니다.
    #    숫자 셋은 값을 비워 두어 '확인 필요' 딱지가 그대로 뜨는 것을 보입니다.
    #
    #    ⚠️ 제목·한 줄·결과·현장 사진은 일부러 넣지 않았습니다. 자리는 나 있지만
    #       채울 값이 없어서, 넣으려면 지어내야 합니다. 그건 이 저장소의 규칙에 어긋납니다
    #       ("지어낸 값을 화면에 올리지 않는다"). 실제 값은 '페이지 문구' 게시판에서 옵니다.
    ACT_BOARD = {'local': ['27'], 'power': ['27'], 'budget': ['57', '27'], 'civic': ['51']}
    ACT_NUM = {
        'local':  [u'감시한 지자체 수', u'올해 낸 의견서'],
        'power':  [u'정보공개 청구', u'답을 못 받은 것'],
        'budget': [u'들여다본 사업', u'짚어낸 금액'],
        'civic':  [u'함께한 참여예산위원', u'연 교육 횟수'],
    }
    activity = {}
    for key, boards in ACT_BOARD.items():
        rows = []
        for b in items:
            link = pick(b, 'link')
            m = re.search(r'/(\d+)/', link)
            if m and m.group(1) in boards:
                rows.append({'title': pick(b, 'title'), 'date': ymd(pick(b, 'pubDate')), 'url': link})
            if len(rows) >= 4:
                break
        activity[key] = {
            'posts': rows,
            'nums': [{'n': None, 'unit': '', 'label': t} for t in ACT_NUM[key]],
        }

    return ('<script>/* 미리보기 데모 — 게시판에서 받았다고 치는 값 */\n'
            'window.AH_DATA = ' + json.dumps(
                {'news': news, 'issues': issues,
                 'issuesDone': issues_done, 'activity': activity},
                ensure_ascii=False, indent=1) + ';</script>\n')


def sibling_root(prefix):
    for p in SIBLINGS[prefix]:
        if os.path.isdir(p):
            return p
    return None


def wrap(path, body, title):
    marks = {
        'a_home': '', 'a_issue': '', 'a_local': '', 'a_power': '',
        'a_budget': '', 'a_pb51': '', 'a_dok': '', 'a_pb': '', 'a_dokorg': '',
        'a_lib': '', 'a_sign': '',
    }
    key = {'/': 'a_home', '/69': 'a_home', '/77': 'a_issue', '/77/': 'a_issue',
           '/49': 'a_local', '/act-power': 'a_power', '/27': 'a_budget',
           '/51': 'a_pb51', '/76': 'a_dok', '/76/': 'a_dok',
           '/80': 'a_pb', '/80/': 'a_pb',
           '/library': 'a_lib', '/library/': 'a_lib',
           '/sign': 'a_sign', '/sign/': 'a_sign'}.get(path)
    if key:
        marks[key] = ' class="on"'
    d = dict(marks)
    d['title'] = title
    d['body'] = body
    return (SHELL % d).encode('utf-8')


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *a):
        pass  # 조용히

    def send_bytes(self, data, ctype='text/html; charset=utf-8', code=200):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        # /dok/ 를 다른 포트에서 받아갈 수도 있어 열어 둡니다(로컬 전용).
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(data)

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = self.path.split('?', 1)[0].split('#', 1)[0]
        query = self.path.split('?', 1)[1] if '?' in self.path else ''

        # ── 옆 저장소 그대로 물려 주기 ──
        for prefix in SIBLINGS:
            if path.startswith(prefix):
                root = sibling_root(prefix)
                if not root:
                    self.send_bytes(wrap(path, STUB_BODY % (
                        '옆 저장소를 못 찾았습니다',
                        '이 주소는 다른 저장소를 그대로 읽습니다. 아래 경로 중 하나에 있어야 합니다:<br>'
                        + '<br>'.join(SIBLINGS[prefix]), path), '못 찾음'), code=404)
                    return
                rel = path[len(prefix):] or 'index.html'
                if rel.endswith('/'):
                    rel += 'index.html'
                full = os.path.normpath(os.path.join(root, *rel.split('/')))
                if not full.startswith(os.path.normpath(root)):
                    self.send_bytes(b'no', 'text/plain', 403); return
                if os.path.isdir(full):
                    full = os.path.join(full, 'index.html')
                if not os.path.isfile(full):
                    self.send_bytes(b'not found: ' + full.encode('utf-8'), 'text/plain; charset=utf-8', 404)
                    return
                ext = os.path.splitext(full)[1].lower()
                self.send_bytes(open(full, 'rb').read(), MIME.get(ext, 'application/octet-stream'))
                return

        # ── 개편안 화면 ──
        if path in ROUTES:
            f = os.path.join(ROOT, ROUTES[path])
            if not os.path.isfile(f):
                self.send_bytes(wrap(path, STUB_BODY % ('파일이 없습니다', ROUTES[path], path), '없음'), code=404)
                return
            page_body = io.open(f, encoding='utf-8').read()
            # 캠페이너스에서는 공통 상단·하단 위젯이 따로 붙입니다.
            # 페이지 조각에는 둘 다 없으므로 로컬 미리보기에서만 앞뒤로 합칩니다.
            body = (io.open(HEADER_PART, encoding='utf-8').read().rstrip() + '\n\n' +
                    page_body.strip() + '\n\n' +
                    io.open(FOOTER_PART, encoding='utf-8').read().lstrip())
            if 'data=demo' in query:
                body = demo_data() + body
            self.send_bytes(wrap(path, body, TITLES.get(path, path)))
            return

        if path in STUBS:
            t, d = STUBS[path]
            self.send_bytes(wrap(path, STUB_BODY % (t, d, path), t))
            return

        # ── 저장소 안의 그냥 파일 (사진 등) ──
        full = os.path.normpath(os.path.join(ROOT, *path.lstrip('/').split('/')))
        if full.startswith(os.path.normpath(ROOT)) and os.path.isfile(full):
            ext = os.path.splitext(full)[1].lower()
            if ext == '.html':
                body = io.open(full, encoding='utf-8').read()
                self.send_bytes(wrap(path, body, os.path.basename(full)))
            else:
                self.send_bytes(open(full, 'rb').read(), MIME.get(ext, 'application/octet-stream'))
            return

        self.send_bytes(wrap(path, STUB_BODY % (
            '이어 두지 않은 주소',
            '이 주소는 캠페이너스의 실제 게시판입니다. 미리보기에는 없습니다.',
            path), '없음'), code=404)


if __name__ == '__main__':
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), H)
    print('미리보기  http://127.0.0.1:%d/' % PORT)
    print('멈추려면 Ctrl+C')
    for p in SIBLINGS:
        r = sibling_root(p)
        print('  %-6s %s' % (p, r if r else '(저장소 못 찾음)'))
    srv.serve_forever()
