# -*- coding: utf-8 -*-
"""개편안을 브라우저에서 보는 미리보기 서버.

    python tools/preview.py            →  http://127.0.0.1:8777/

왜 필요한가
    이 저장소의 .html 은 통째로 된 문서가 아니라 캠페이너스 코드 위젯에 붙일
    **조각**입니다. <head> 가 없어서 파일을 그냥 열면 한글이 깨집니다.
    이 서버가 charset·viewport 를 씌워서 내보냅니다.

    또 하나. 활동/이슈 페이지가 서로를 /49, /act-power 같은 주소로 가리키기
    때문에, 파일을 직접 열면 링크가 전부 깨집니다. 여기서는 그 주소를 실제
    파일에 이어 줍니다.

이어 둔 주소
    /               홈                    index.html
    /issue/         이슈 목록             issue.html
    /49             활동 > 지자체 감시    activity-local.html
    /act-power      활동 > 권력감시       activity-power.html
    /act-budget     활동 > 예산감시       activity-budget.html
    /51             활동 > 참여예산       (아직 없음 — 안내가 뜹니다)
    /dok-history    활동 > 밑빠진 독상    dok-history.html
    /library        자료실                library.html
    /dok/           밑빠진 독상 원본      옆 저장소를 그 자리에서 읽습니다
    /pb/            참여예산 상담소       pb.html
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
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8777

# 옆 저장소. 없으면 그 주소만 안내가 뜨고 나머지는 그대로 돕니다.
SIBLINGS = {
    '/dok/': [
        os.path.join(os.path.dirname(ROOT), 'dokseong', 'public'),
        r'C:\Users\dbqke\dokseong\public',
    ],
    # 2026-08-27: /pb/ 는 이 저장소의 새 상담소(pb.html)가 씁니다.
    # 옛 초안은 견줘 보려고 /pb-old/ 로 옮겨 두었습니다.
    '/pb-old/': [
        r'C:\Users\dbqke\participatory-budget',
        os.path.join(os.path.dirname(ROOT), 'participatory-budget'),
    ],
}

ROUTES = {
    '/': 'index.html',
    '/69': 'index.html',
    '/issue/': 'issue.html',
    '/issue': 'issue.html',
    '/49': 'activity-local.html',
    '/act-power': 'activity-power.html',
    '/act-budget': 'activity-budget.html',
    '/dok-history': 'dok-history.html',
    '/pb/': 'pb.html',
    '/pb': 'pb.html',
    '/library': 'library.html',
    '/library/': 'library.html',
}

# 아직 화면이 없는 주소. 404 대신 "무엇이 없는지"를 알려 줍니다.
STUBS = {
    '/51': ('활동 &gt; 참여예산', '이 활동의 화면은 아직 없습니다. 캠페이너스 /51 (주민참여예산 활성화) 게시판으로 이어질 자리입니다.'),
    '/52': ('활동 전체', '활동 다섯을 모아 보여 줄 목록 화면입니다. 아직 안 만들었습니다.'),
    '/23': ('발행물', '게시판입니다. 자료실은 이제 /library 에 따로 있습니다.'),
    '/24': ('뉴스룸', '보도자료 게시판입니다.'),
    '/25': ('뉴스레터', '스티비 구독 페이지입니다.'),
    '/26': ('소식', '공지 게시판입니다.'),
    '/27': ('일반 활동', '게시판입니다.'),
    '/57': ('예산 모니터링', '게시판입니다. 활동 &gt; 예산감시의 글이 여기 올라가 있습니다.'),
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
  <a href="/issue/"%(a_issue)s>이슈</a>
  <b>활동</b>
  <a href="/49"%(a_local)s>지자체 감시</a>
  <a href="/act-power"%(a_power)s>권력감시</a>
  <a href="/act-budget"%(a_budget)s>예산감시</a>
  <a href="/51"%(a_pb51)s>참여예산</a>
  <a href="/dok-history"%(a_dok)s>밑빠진 독상</a>
  <b>이슈</b>
  <a href="/pb/"%(a_pb)s>참여예산 상담소</a>
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
    '/': '홈', '/69': '홈', '/issue/': '이슈', '/issue': '이슈',
    '/49': '활동 > 지자체 감시', '/act-power': '활동 > 권력감시',
    '/act-budget': '활동 > 예산감시', '/dok-history': '활동 > 밑빠진 독상',
    '/pb/': '이슈 > 참여예산 상담소', '/pb': '이슈 > 참여예산 상담소',
    '/library': '자료실', '/library/': '자료실',
}

MIME = {
    '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.webp': 'image/webp',
    '.woff': 'font/woff', '.woff2': 'font/woff2', '.ico': 'image/x-icon',
    '.txt': 'text/plain; charset=utf-8',
}


def sibling_root(prefix):
    for p in SIBLINGS[prefix]:
        if os.path.isdir(p):
            return p
    return None


def wrap(path, body, title):
    marks = {
        'a_home': '', 'a_issue': '', 'a_local': '', 'a_power': '',
        'a_budget': '', 'a_pb51': '', 'a_dok': '', 'a_pb': '', 'a_dokorg': '',
        'a_lib': '',
    }
    key = {'/': 'a_home', '/69': 'a_home', '/issue/': 'a_issue', '/issue': 'a_issue',
           '/49': 'a_local', '/act-power': 'a_power', '/act-budget': 'a_budget',
           '/51': 'a_pb51', '/dok-history': 'a_dok',
           '/pb/': 'a_pb', '/pb': 'a_pb',
           '/library': 'a_lib', '/library/': 'a_lib'}.get(path)
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
            body = io.open(f, encoding='utf-8').read()
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
