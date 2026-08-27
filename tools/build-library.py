# -*- coding: utf-8 -*-
"""자료실 화면을 만든다.

    python tools/build-library.py            저장해 둔 글 목록으로 만든다
    python tools/build-library.py --fetch    action.or.kr/rss 를 먼저 새로 받는다

만드는 파일
    library.html    자료실 (미리보기 /library)

왜 손으로 안 쓰고 찍어내나
    자료실은 글 목록입니다. 손으로 적으면 그 순간 낡고, 무엇보다
    **지어낸 글이 섞일 위험**이 있습니다. 그래서 실제 action.or.kr 의 글만
    씁니다. 여기 나오는 제목·날짜·주소는 전부 그 사이트에서 받은 값입니다.

분류를 어떻게 정했나
    두 축 다 **확인할 수 있는 것**만 씁니다.

      종류 — 제목의 말머리로 가릅니다.  [논평] · 뉴스 브리핑 - · [안건 N] 처럼
             글쓴이가 스스로 붙인 말머리입니다. 우리가 판단한 게 아닙니다.
             말머리가 없는 글은 '글' 로 둡니다. 억지로 끼워 넣지 않습니다.
      게시판 — 주소의 번호입니다. 사이트가 그 글을 어디에 넣었는지 그대로입니다.

    ⚠️ '활동 다섯(지자체·권력·예산·시민참여·밑빠진 독상)'으로 묶는 분류는
       여기서 안 합니다. 게시판과 활동이 일대일이 아니라서, 자동으로 묶으면
       반드시 틀린 글이 섞입니다. 사람이 정해야 합니다. 화면에도 그렇게 적어 뒀습니다.

색·글꼴·모양은 DESIGN.md 의 값을 그대로 씁니다.
"""

import io
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FEED = os.path.join(HERE, 'data', 'action-rss.xml')
OUT = os.path.join(ROOT, 'library.html')

RSS_URL = 'https://action.or.kr/rss'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


# ══════════════════════════════════════════════════════════════════
#  분류
# ══════════════════════════════════════════════════════════════════

# 종류 — 위에서부터 차례로 맞춰 보고 처음 걸리는 것으로 정합니다.
# 그래서 순서가 곧 규칙입니다. 좁은 것을 위에, 넓은 것을 아래에 두세요.
KINDS = [
    ('brief',   '뉴스 브리핑',      r'^뉴스\s*브리핑'),
    ('letter',  '뉴스레터',         r'^밑빠진 독상 - 시민의 세금'),
    ('comment', '논평 · 성명',      r'^\[논평\]|규탄한다|요구한다'),
    ('meeting', '총회 자료',        r'^\[안건\s*\d+\]'),
    ('law',     '입법 활동',        r'^\[입법활동\]'),
    ('sign',    '서명 · 감사청구',  r'^\[서명|감사청구'),
    ('pledge',  '공약 자료',        r'공약모음|공약_'),
    ('note',    '활동가 수첩',      r'^활동가 수첩'),
    ('report',  '보고서 · 분석',    r'분석 보고서|현황 정리|쟁점, 질문 정리|평가·배분체계'),
    ('press',   '기자회견 · 간담회', r'기자회견|간담회'),
]
KIND_ETC = ('etc', '글')

# 게시판 — 주소 번호 그대로입니다.
# 이름은 현재 action.or.kr 메뉴에서 가져왔습니다. 35 만은 메뉴에 없어서
# 그 게시판 글([안건 N] … 회원 총회)을 보고 붙였습니다.
BOARDS = {
    '23': '발행물',
    '24': '뉴스룸',
    '26': '공지',
    '27': '일반 활동',
    '31': '운영 자료',
    '35': '회원 총회',
    '46': '지역 예산 감시 사례',
    '51': '시민참여',
    '54': '연대 활동',
    '57': '예산 모니터링',
}

MONTHS = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
          'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}


def fetch():
    """rss 를 새로 받아 저장해 둡니다. WebFetch 는 403 이라 UA 를 줘야 통과합니다."""
    try:
        from urllib.request import Request, urlopen
    except ImportError:
        from urllib2 import Request, urlopen
    req = Request(RSS_URL, headers={'User-Agent': UA})
    data = urlopen(req, timeout=20).read()
    if b'<item>' not in data:
        raise SystemExit('받아온 내용에 글이 없습니다. 주소나 차단을 확인하세요.')
    with open(FEED, 'wb') as f:
        f.write(data)
    print('  받음: %s (%d바이트)' % (RSS_URL, len(data)))


def kind_of(title):
    for key, label, pat in KINDS:
        if re.search(pat, title):
            return key, label
    return KIND_ETC


def parse():
    """저장해 둔 rss 를 (제목, 주소, 날짜, 게시판, 종류) 줄로 바꿉니다."""
    root = ET.parse(FEED).getroot()
    rows = []
    for it in root.findall('.//item'):
        title = (it.findtext('title') or '').strip()
        link = (it.findtext('link') or '').strip()
        pub = (it.findtext('pubDate') or '').strip()
        if not title or not link:
            continue

        # 'Tue, 25 Aug 2026 17:05:00 +0900' → (2026, 8, 25)
        m = re.search(r'(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})', pub)
        if not m:
            continue
        day, mon, year = int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))

        b = re.search(r'action\.or\.kr/(\d+)', link)
        board = b.group(1) if b else ''

        key, label = kind_of(title)
        rows.append(dict(
            title=title, link=link,
            y=year, m=mon, d=day,
            ymd='%04d-%02d-%02d' % (year, mon, day),
            board=board, board_name=BOARDS.get(board, '기타'),
            kind=key, kind_name=label,
        ))
    rows.sort(key=lambda r: r['ymd'], reverse=True)
    return rows


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;')
             .replace('>', '&gt;').replace('"', '&quot;'))


# ══════════════════════════════════════════════════════════════════
#  화면
# ══════════════════════════════════════════════════════════════════

TEMPLATE = u'''<style>
/* ═══════════════════════════════════════════════════════════════
   자료실

   ⚠️ 이 파일은 tools/build-library.py 가 만듭니다. 직접 고치지 마세요.
      화면을 고치려면 그 파일의 TEMPLATE 을 고치고 다시 돌리세요.
      →  python tools/build-library.py

   자료실은 "모든 결과물이 들어가는 곳"입니다. 그래서 가장 중요한 것은
   **찾을 수 있게 하는 것**이고, 분류가 곧 화면입니다.

   왼쪽에 분류를 붙박이로 두고 오른쪽에 목록을 둡니다. 분류를 고르면 목록만
   바뀌고 분류는 자리에 그대로 있습니다 — 어디를 보고 있는지 잃지 않습니다.

   설계 원칙(DESIGN.md) : 켜는 것만 스크립트가 합니다.
   스크립트가 막히면 거르는 단추가 아예 안 나오고, 글은 {n}건 모두 그냥 보입니다.
   ═══════════════════════════════════════════════════════════════ */

@font-face{{font-family:'GmarketSans';src:url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff');font-weight:700;font-display:swap}}

#lib{{
  /* ── DESIGN.md 의 한 벌 ── */
  --brand:#00afec; --deep:#0079a6; --tint:#e2f5fd; --band:#eef7fb; --navy:#062330;
  --ink:#0b1e28; --soft:#4a6473; --faint:#7d95a3; --line:#d5e4eb; --paper:#f1f6f8;
  --flag:#9a5c06; --flag-bg:#fff4e1; --flag-line:#ecd3a2;

  margin-left:calc(50% - 50vw + var(--ah-sb, 0px) / 2);margin-right:calc(50% - 50vw + var(--ah-sb, 0px) / 2);
  background:#fff; color:var(--ink); line-height:1.65;
  font-family:'Pretendard Variable',Pretendard,'Noto Sans KR',-apple-system,sans-serif;
  word-break:keep-all; -webkit-font-smoothing:antialiased;
}}
#lib *{{box-sizing:border-box}}
#lib h1,#lib h2,#lib h3{{margin:0; letter-spacing:-.022em; font-family:GmarketSans,'Pretendard Variable',sans-serif}}
#lib p{{margin:0}}
#lib a{{color:inherit; text-decoration:none}}
#lib ul{{list-style:none; margin:0; padding:0}}
#lib :focus-visible{{outline:2.5px solid var(--brand); outline-offset:3px}}
#lib .wrap{{width:min(1120px,calc(100% - 48px)); margin:0 auto}}
#lib .tbd{{background:var(--flag-bg); color:var(--flag); border:1px dashed var(--flag-line);
  border-radius:999px; padding:1px 8px; font-size:.78em; font-weight:700; white-space:nowrap}}

/* ───── 맨 위 ─────  (2026-08-27 다시 짬)
   활동·이슈와 같은 틀입니다. 예전에는 짙은 남색 띠였는데, 활동 페이지에서
   "띠가 겹겹이 쌓여 마음에 안 든다"는 지적을 받아 색면을 걷어냈습니다.
   여기만 남색으로 두면 이번엔 자료실만 다른 사이트로 보입니다. */
#lib .top{{padding:clamp(20px,2.4vw,30px) 0 0; border-bottom:2px solid var(--ink)}}
#lib .crumb{{font-size:12.5px; font-weight:600; color:var(--deep)}}
#lib .crumb a{{color:var(--deep)}}
#lib .crumb a:hover{{text-decoration:underline; text-underline-offset:3px}}
#lib .crumb span{{opacity:.45; margin:0 6px}}
#lib .top h1{{
  margin-top:clamp(18px,2vw,26px);
  font-size:clamp(28px,4.4vw,46px); font-weight:700; line-height:1.24;
  letter-spacing:-.03em; text-wrap:balance
}}
#lib .top h1 em{{display:block; font-style:normal; color:var(--deep)}}
#lib .top .by{{
  margin-top:14px; font-size:clamp(14.5px,1.2vw,16.5px);
  color:var(--soft); max-width:56ch; line-height:1.7
}}

/* 숫자 셋 — 이 자료실이 무엇을 얼마나 담고 있는지 한 줄로.
   맨 위 덩이의 마지막 줄입니다. 활동 페이지의 숫자 셋과 같은 모양입니다. */
#lib .facts{{
  display:grid; grid-template-columns:repeat(3,1fr);
  margin-top:clamp(26px,3vw,40px); border-top:1px solid var(--line)
}}
#lib .fact{{padding:clamp(16px,1.8vw,22px) 0 clamp(16px,1.8vw,22px) clamp(14px,1.6vw,20px);
  border-left:1px solid var(--line)}}
#lib .fact:first-child{{border-left:none; padding-left:0}}
#lib .fact b{{display:block; font-family:GmarketSans,sans-serif; font-size:clamp(21px,2.4vw,30px);
  font-weight:700; line-height:1.15; color:var(--deep); letter-spacing:-.03em}}
#lib .fact span{{display:block; margin-top:5px; font-size:12.5px; font-weight:600; color:var(--soft)}}

/* ───── 본문 두 칸 ─────
   왼쪽 분류는 붙박이(sticky)입니다. 목록을 한참 내려가도 분류가 따라옵니다. */
#lib .body{{display:grid; grid-template-columns:minmax(212px,244px) minmax(0,1fr);
  gap:clamp(22px,3vw,44px); padding:clamp(30px,3.6vw,50px) 0 clamp(50px,6vw,90px)}}
#lib .side{{position:sticky; top:96px; align-self:start; max-height:calc(100vh - 120px); overflow-y:auto}}

#lib .fgroup + .fgroup{{margin-top:26px}}
#lib .fgroup h2{{font-size:13px; font-weight:700; color:var(--soft); margin-bottom:10px}}
#lib .fgroup ul{{display:flex; flex-direction:column; gap:2px}}
/* 거르는 단추. 스크립트가 .is-on 을 붙여야 보입니다 — 아래 '스크립트 없을 때'를 보세요. */
#lib .fbtn{{
  display:flex; align-items:center; justify-content:space-between; gap:10px; width:100%;
  border:none; background:none; cursor:pointer; text-align:left;
  padding:8px 11px; border-radius:999px;
  font-family:inherit; font-size:14px; font-weight:600; color:var(--ink); transition:.14s
}}
#lib .fbtn:hover{{background:var(--band); color:var(--deep)}}
#lib .fbtn .n{{font-size:12px; font-weight:700; color:var(--faint); font-variant-numeric:tabular-nums}}
#lib .fbtn[aria-pressed="true"]{{background:var(--brand); color:#fff}}
#lib .fbtn[aria-pressed="true"] .n{{color:rgba(255,255,255,.8)}}

/* ───── 찾기 줄 ───── */
#lib .seek{{display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:18px}}
#lib .seek-box{{position:relative; flex:1 1 240px; min-width:0}}
#lib .seek input{{
  width:100%; border:1.5px solid var(--line); border-radius:999px;
  padding:11px 16px 11px 40px; font-family:inherit; font-size:14.5px; color:var(--ink); background:#fff
}}
#lib .seek input:focus{{border-color:var(--brand); outline:none}}
#lib .seek-box::before{{content:"⌕"; position:absolute; left:15px; top:50%; transform:translateY(-50%);
  font-size:17px; color:var(--faint); pointer-events:none}}
#lib .seek-at{{font-size:13.5px; font-weight:700; color:var(--soft); font-variant-numeric:tabular-nums}}
#lib .seek-at b{{color:var(--deep)}}
#lib .seek-clear{{
  border:1.5px solid var(--line); background:#fff; border-radius:999px; padding:9px 15px;
  font-family:inherit; font-size:13px; font-weight:700; color:var(--soft); cursor:pointer
}}
#lib .seek-clear:hover{{border-color:var(--brand); color:var(--deep)}}

/* ───── 목록 ─────
   자료실은 훑어 내려가며 찾는 곳이라 카드가 아니라 줄입니다.
   줄마다 [종류] 제목 / 날짜 · 게시판. 종류가 왼쪽에 모여 있어 눈으로 걸러집니다. */
#lib .rows{{border-top:2px solid var(--ink)}}
#lib .row{{display:block; padding:15px 4px; border-bottom:1px solid var(--line); transition:background .13s}}
#lib .row:hover{{background:var(--paper)}}
#lib .row:hover .rt{{color:var(--deep); text-decoration:underline; text-underline-offset:3px}}
#lib .rk{{
  display:inline-block; border-radius:999px; padding:3px 11px; margin-bottom:7px;
  font-size:11.5px; font-weight:700; background:var(--tint); color:var(--deep)
}}
/* 종류마다 다른 색을 주지 않습니다 — 열 가지 색이 섞이면 목록이 시끄러워집니다.
   대신 '뉴스 브리핑'처럼 수가 많아 배경이 되는 것만 옅게 눕힙니다. */
#lib .rk[data-k="brief"],#lib .rk[data-k="etc"]{{background:var(--paper); color:var(--soft)}}
#lib .rt{{display:block; font-size:15.5px; font-weight:700; line-height:1.5; transition:color .13s}}
#lib .rm{{display:flex; align-items:center; gap:8px; margin-top:5px; font-size:12.5px; color:var(--faint)}}
#lib .rm i{{font-style:normal; opacity:.5}}
#lib .row[hidden]{{display:none}}

/* 아무것도 안 걸렸을 때 */
#lib .none{{border:1px dashed var(--line); padding:56px 20px; text-align:center;
  color:var(--faint); font-size:14.5px}}

/* ───── 사람이 정해야 하는 것 ─────
   자동으로 묶으면 틀린 글이 섞이는 자리라, 비워 두고 그렇다고 적어 둡니다. */
#lib .todo{{
  margin-top:26px; background:var(--flag-bg); border:1px dashed var(--flag-line);
  padding:18px 20px; font-size:13.5px; line-height:1.7; color:#6b4304
}}
#lib .todo b{{display:block; font-size:14.5px; color:var(--flag); margin-bottom:5px}}

/* ───── 스크립트가 막혔을 때 ─────
   거르는 단추와 찾기 줄은 스크립트가 있어야 뜻이 있습니다. 그래서 기본은 숨김이고
   스크립트가 .is-on 을 붙여야 나옵니다. 글 {n}건은 어느 쪽이든 다 보입니다. */
#lib .side,#lib .seek{{display:none}}
#lib .is-on.side{{display:block}}
#lib .is-on.seek{{display:flex}}
#lib .body:not(:has(.is-on)){{grid-template-columns:minmax(0,1fr)}}

@media(max-width:900px){{
  /* 좁은 화면 — 분류를 위로 올려 가로로 눕힙니다. 붙박이는 풀어 줍니다. */
  #lib .body{{grid-template-columns:minmax(0,1fr)}}
  #lib .side{{position:static; max-height:none; overflow:visible;
    border-bottom:1px solid var(--line); padding-bottom:18px; margin-bottom:6px}}
  #lib .fgroup + .fgroup{{margin-top:16px}}
  #lib .fgroup ul{{flex-direction:row; flex-wrap:wrap; gap:6px}}
  #lib .fbtn{{width:auto; border:1.5px solid var(--line); padding:7px 13px}}
}}
@media(max-width:560px){{
  #lib .wrap{{width:min(100% - 32px,1120px)}}
  #lib .top{{padding-top:16px}}
  /* 좁은 화면에서는 숫자 셋을 세로로 눕힙니다. */
  #lib .facts{{grid-template-columns:1fr}}
  #lib .fact{{border-left:none; border-top:1px solid var(--line); padding:13px 0}}
  #lib .fact:first-child{{border-top:none}}
}}
@media(prefers-reduced-motion:reduce){{
  #lib *{{transition:none!important; animation:none!important}}
}}
</style>

<!-- PART:header -->
<!-- /PART:header -->

<div id="lib">

  <!-- ───────── 맨 위 ─────────
       ⚠️ 색 띠를 두르지 마세요. 활동·이슈와 같은 틀이어야 한 사이트로 읽힙니다. -->
  <section class="top">
    <div class="wrap">
      <p class="crumb"><a href="/69?preview_mode=1">홈</a><span>›</span>자료실</p>
      <h1>우리가 만든 것은<em>모두 여기에 있습니다</em></h1>
      <p class="by">논평과 보고서, 뉴스 브리핑, 총회 자료까지 —
        함께하는 시민행동이 내놓은 결과물을 한자리에 모았습니다.
        종류나 게시판으로 걸러 보거나, 제목으로 찾을 수 있습니다.</p>

      <div class="facts">
        <div class="fact"><b>{n}건</b><span>지금 담긴 글</span></div>
        <div class="fact"><b>{kinds}가지</b><span>종류</span></div>
        <div class="fact"><b>{span}</b><span>담긴 기간</span></div>
      </div>
    </div>
  </section>

  <div class="wrap">
    <div class="body" id="lib-body">

      <!-- 왼쪽 분류. 단추는 스크립트가 켭니다. -->
      <aside class="side" id="lib-side" aria-label="자료 거르기">
        <div class="fgroup">
          <h2>종류</h2>
          <ul>
{kind_btns}
          </ul>
        </div>
        <div class="fgroup">
          <h2>게시판</h2>
          <ul>
{board_btns}
          </ul>
        </div>
      </aside>

      <div>
        <div class="seek" id="lib-seek">
          <span class="seek-box">
            <input type="search" id="lib-q" placeholder="제목으로 찾기" aria-label="제목으로 찾기">
          </span>
          <span class="seek-at" id="lib-at"><b>{n}</b>건</span>
          <button type="button" class="seek-clear" id="lib-clear">거른 것 지우기</button>
        </div>

        <!-- ⚠️ 아래 줄은 tools/build-library.py 가 action.or.kr/rss 에서 받아 찍은
             **실제 글**입니다. 손으로 줄을 넣지 마세요 — 다음 빌드에 지워집니다.
             글을 더 담으려면 그 스크립트를 --fetch 로 다시 돌리세요. -->
        <div class="rows" id="lib-rows">
{rows}
        </div>

        <p class="none" id="lib-none" hidden>걸린 글이 없습니다. 거른 것을 지워 보세요.</p>

        <div class="todo">
          <b>사람이 정해야 하는 것 — 활동 다섯으로 묶기</b>
          지금 분류는 <b style="display:inline">종류</b>(제목 말머리)와
          <b style="display:inline">게시판</b>(주소 번호) 둘뿐입니다. 둘 다 사이트에 이미
          있는 값이라 저절로 갈립니다.
          하지만 <b style="display:inline">활동 다섯</b>(지자체 감시 · 권력감시 · 예산감시 ·
          시민참여 · 밑빠진 독상)으로 묶는 것은 게시판과 일대일이 아닙니다.
          예를 들어 '일반 활동'({b27}건) 안에는 권력감시 글도 예산감시 글도 섞여 있습니다.
          자동으로 나누면 반드시 틀린 글이 들어가므로 <span class="tbd">확인 필요</span>
          로 비워 뒀습니다. 활동별로 나눌 기준을 정해 주시면 축을 하나 더 붙이겠습니다.
        </div>
      </div>

    </div>
  </div>

</div>

<script>
/* ═══════════════════════════════════════════════════════════════
   자료실 거르기

   설계 원칙(DESIGN.md): 켜는 것만 스크립트가 합니다.
   거르는 단추와 찾기 줄은 CSS 기본값이 '숨김'이고, 여기서 .is-on 을 붙여야 나옵니다.
   이 코드가 막히면 단추가 아예 안 뜨고 글 {n}건이 그냥 다 보입니다.
   ═══════════════════════════════════════════════════════════════ */
(function () {{
  'use strict';
  var root = document.getElementById('lib-body');
  if (!root) return;

  var side = document.getElementById('lib-side');
  var seek = document.getElementById('lib-seek');
  var rows = Array.prototype.slice.call(document.querySelectorAll('#lib-rows .row'));
  var none = document.getElementById('lib-none');
  var at = document.getElementById('lib-at');
  var q = document.getElementById('lib-q');
  if (!rows.length) return;

  side.classList.add('is-on');
  seek.classList.add('is-on');

  // 고른 것. 종류와 게시판은 각각 여럿 고를 수 있습니다.
  var picked = {{ kind: [], board: [] }};

  function toggle(kindOrBoard, value, btn) {{
    var list = picked[kindOrBoard];
    var i = list.indexOf(value);
    if (i < 0) {{ list.push(value); btn.setAttribute('aria-pressed', 'true'); }}
    else {{ list.splice(i, 1); btn.setAttribute('aria-pressed', 'false'); }}
    apply();
  }}

  function apply() {{
    var word = (q.value || '').trim().toLowerCase();
    var shown = 0;
    rows.forEach(function (r) {{
      var okKind = !picked.kind.length || picked.kind.indexOf(r.dataset.kind) >= 0;
      var okBoard = !picked.board.length || picked.board.indexOf(r.dataset.board) >= 0;
      var okWord = !word || (r.dataset.find || '').indexOf(word) >= 0;
      var on = okKind && okBoard && okWord;
      r.hidden = !on;
      if (on) shown++;
    }});
    at.innerHTML = '<b>' + shown + '</b>건';
    none.hidden = shown > 0;
  }}

  side.querySelectorAll('.fbtn').forEach(function (btn) {{
    btn.addEventListener('click', function () {{
      toggle(btn.dataset.axis, btn.dataset.value, btn);
    }});
  }});

  q.addEventListener('input', apply);

  document.getElementById('lib-clear').addEventListener('click', function () {{
    picked.kind = []; picked.board = [];
    side.querySelectorAll('.fbtn').forEach(function (b) {{
      b.setAttribute('aria-pressed', 'false');
    }});
    q.value = '';
    apply();
  }});

  apply();
}})();
</script>
'''


def build():
    rows = parse()
    if not rows:
        raise SystemExit('글을 하나도 못 읽었습니다. tools/data/action-rss.xml 을 확인하세요.')

    kc = Counter((r['kind'], r['kind_name']) for r in rows)
    bc = Counter((r['board'], r['board_name']) for r in rows)

    def btns(counter, axis):
        out = []
        for (val, name), cnt in counter.most_common():
            out.append(
                u'            <li><button type="button" class="fbtn" '
                u'data-axis="%s" data-value="%s" aria-pressed="false">'
                u'<span>%s</span><span class="n">%d</span></button></li>'
                % (axis, esc(val), esc(name), cnt))
        return u'\n'.join(out)

    row_html = []
    for r in rows:
        # data-find 는 찾기용으로 미리 소문자로 만들어 둔 글자입니다.
        # 화면에 안 보이므로 제목·종류·게시판을 다 넣어 뒀습니다.
        find = (r['title'] + ' ' + r['kind_name'] + ' ' + r['board_name']).lower()
        row_html.append(
            u'          <a class="row" href="%s" data-kind="%s" data-board="%s" data-find="%s">\n'
            u'            <span class="rk" data-k="%s">%s</span>\n'
            u'            <span class="rt">%s</span>\n'
            u'            <span class="rm">%s<i>·</i>%s</span>\n'
            u'          </a>'
            % (esc(r['link']), esc(r['kind']), esc(r['board']), esc(find),
               esc(r['kind']), esc(r['kind_name']), esc(r['title']),
               esc(r['ymd']), esc(r['board_name'])))

    first, last = rows[-1], rows[0]
    span = u'%d.%02d – %d.%02d' % (first['y'], first['m'], last['y'], last['m'])

    html = TEMPLATE.format(
        n=len(rows),
        kinds=len(kc),
        span=span,
        kind_btns=btns(kc, 'kind'),
        board_btns=btns(bc, 'board'),
        rows=u'\n'.join(row_html),
        b27=sum(1 for r in rows if r['board'] == '27'),
    )

    with io.open(OUT, 'w', encoding='utf-8', newline='') as f:
        f.write(html)

    print(u'  * library.html          글 %d건 / 종류 %d / 게시판 %d' % (len(rows), len(kc), len(bc)))
    print(u'')
    print(u'  종류별')
    for (k, name), c in kc.most_common():
        print(u'    %-14s %3d건' % (name, c))
    print(u'')
    print(u'  게시판별')
    for (b, name), c in bc.most_common():
        print(u'    %-14s %3d건  (/%s)' % (name, c, b))


def main():
    if '--fetch' in sys.argv:
        print(u'글 목록 새로 받기 —')
        fetch()
    if not os.path.exists(FEED):
        raise SystemExit('글 목록이 없습니다. --fetch 를 붙여 한 번 받아 주세요.')
    print(u'자료실 만들기 —')
    build()

    # 방금 찍어낸 화면에는 헤더 자리가 비어 있습니다. 공통 헤더를 이어서 심습니다.
    # (따로 돌리는 걸 잊으면 자료실에만 목차가 없어집니다.)
    print(u'')
    print(u'  공통 헤더 심기 —')
    import subprocess
    subprocess.call([sys.executable, os.path.join(HERE, 'build-parts.py')])


if __name__ == '__main__':
    main()
