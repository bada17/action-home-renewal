# -*- coding: utf-8 -*-
"""활동 페이지 세 장을 한 틀에서 찍어낸다.

    python tools/build-activity.py

만드는 파일
    activity-local.html    활동 > 지자체 감시 (지방정부 · 지방의회)
    activity-power.html    활동 > 권력감시   (중앙정부 · 국회)
    activity-budget.html   활동 > 예산감시   (나라살림 · 지방재정)

왜 손으로 안 쓰고 찍어내나
    세 장이 "같은 단체가 만든 것"으로 보여야 합니다. 손으로 세 번 쓰면
    여백이나 글씨 크기가 조금씩 어긋나고, 한 장만 고치는 일이 반드시 생깁니다.
    틀은 한 곳(TEMPLATE)에만 있고, 페이지마다 다른 것은 아래 PAGES 의 값뿐입니다.

    ★ 화면을 고치려면 이 파일의 TEMPLATE 을 고치고 다시 돌리세요.
      만들어진 .html 을 직접 고치면 다음에 돌릴 때 지워집니다.

색·글꼴·모양은 DESIGN.md 의 값을 그대로 씁니다. 여기 값을 바꾸면
DESIGN.md 와 다른 네 화면도 같이 고쳐야 합니다.
"""

import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ══════════════════════════════════════════════════════════════════
#  틀
# ══════════════════════════════════════════════════════════════════
TEMPLATE = u'''<style>
/* ═══════════════════════════════════════════════════════════════
   활동 > {title}

   ⚠️ 이 파일은 tools/build-activity.py 가 만듭니다. 직접 고치지 마세요.
      화면을 고치려면 그 파일의 TEMPLATE 을, 내용을 고치려면 PAGES 를 고치고
      다시 돌리세요.  →  python tools/build-activity.py

   구성 : 히어로 → 숫자 셋 → 지금 → 결과 → 글 → 자료 → 연락
   말투 : 참여연대 방식. 섹션 제목이 분류명이 아니라 말을 겁니다
          ("무엇을 보고 있나", "무엇이 달라졌나"). 그 밑에 한 줄만 답니다.
   색·글꼴·모양 : DESIGN.md 의 한 벌. 다른 네 화면과 같은 값입니다.

   '결과'를 글이 아니라 **사건** 단위로 두는 이유:
   감시 활동은 글 하나로 안 끝납니다. 문제제기·감사청구·감사결과·후속이 각각
   다른 글이라, 글을 늘어놓으면 시민행동이 뭘 해서 나온 결과인지 안 보입니다.
   그래서 사건 하나에 [무엇을 했나 → 무엇이 바뀌었나] 두 줄로 적고 근거 글을 답니다.
   자동으로 못 채웁니다. 사람이 분기에 한 번 정리하면 됩니다(몇 건 안 됩니다).
   ═══════════════════════════════════════════════════════════════ */

@font-face{{font-family:'GmarketSans';src:url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansBold.woff') format('woff');font-weight:700;font-display:swap}}

#act{{
  /* ── DESIGN.md 의 한 벌. 다섯 화면이 같은 값을 씁니다 ── */
  --brand:#00afec; --deep:#0079a6; --tint:#e2f5fd; --band:#eef7fb; --navy:#062330;
  --ink:#0b1e28; --soft:#4a6473; --faint:#7d95a3; --line:#d5e4eb; --paper:#f1f6f8;
  --flag:#9a5c06; --flag-bg:#fff4e1; --flag-line:#ecd3a2;

  position:relative; left:50%; width:100vw; margin-left:-50vw;
  background:#fff; color:var(--ink);
  font-family:'Pretendard Variable',Pretendard,'Noto Sans KR',-apple-system,sans-serif;
  font-size:16px; line-height:1.7; word-break:keep-all; -webkit-font-smoothing:antialiased;
}}
#act *{{box-sizing:border-box}}
#act h1,#act h2,#act h3{{font-family:GmarketSans,'Pretendard Variable',sans-serif; letter-spacing:-.022em; margin:0}}
#act p{{margin:0}}
#act ul{{list-style:none; margin:0; padding:0}}
#act a{{color:inherit; text-decoration:none}}
#act :focus-visible{{outline:2.5px solid var(--brand); outline-offset:3px}}

#act .wrap{{width:min(880px,calc(100% - 44px)); margin:0 auto}}
#act .sec{{padding:clamp(38px,4.6vw,64px) 0; border-top:1px solid var(--line)}}
#act .sec:first-of-type{{border-top:none}}

/* 섹션 머리 — 말 거는 제목 + 한 줄. 참여연대 방식입니다. */
#act .sh{{margin-bottom:clamp(20px,2.4vw,30px)}}
#act .sh .eyebrow{{
  display:block; font-size:11.5px; font-weight:700; letter-spacing:.14em;
  color:var(--deep); margin-bottom:9px
}}
#act .sh h2{{font-size:clamp(20px,2.3vw,27px); font-weight:700; line-height:1.4}}
#act .sh p{{margin-top:8px; font-size:14.5px; color:var(--soft); line-height:1.65; max-width:60ch}}

/* 확인 안 된 값 표시. 공개 전에 이 딱지가 화면에 하나도 없어야 합니다. */
#act .tbd{{background:var(--flag-bg); color:var(--flag); border:1px dashed var(--flag-line);
  border-radius:999px; padding:1px 8px; font-size:.8em; font-weight:700; white-space:nowrap}}

/* ───── 빵부스러기 ───── */
#act .crumb{{padding:16px 0 0; font-size:12.5px; font-weight:600; color:var(--deep)}}
#act .crumb span{{opacity:.45; margin:0 6px}}
#act .crumb a:hover{{text-decoration:underline; text-underline-offset:3px}}

/* ───── 히어로 ───── */
#act .hero{{background:var(--navy); color:#fff; padding:clamp(44px,5.4vw,76px) 0}}
#act .hero .crumb{{padding:0 0 clamp(22px,2.6vw,34px); color:#7fb7ce}}
#act .hero .crumb a{{color:#7fb7ce}}
#act .hero .who{{
  display:inline-block; border:1.5px solid rgba(255,255,255,.42); border-radius:999px;
  padding:5px 14px; font-size:12.5px; font-weight:700; color:#cfe8f4; margin-bottom:16px
}}
#act .hero h1{{font-size:clamp(27px,4.4vw,44px); font-weight:700; line-height:1.28; text-wrap:balance}}
#act .hero .by{{margin-top:15px; font-size:clamp(14.5px,1.2vw,16.5px); color:#a8cddc; max-width:52ch; line-height:1.7}}

/* ───── 숫자 셋 ─────
   "이 활동이 얼마나 오래, 얼마나 많이" 를 한 줄로 보여 줍니다.
   ⚠️ 확인 안 된 숫자는 올리지 말고 딱지를 붙이세요. */
#act .nums{{display:grid; grid-template-columns:repeat(3,1fr); background:var(--band)}}
#act .num{{padding:clamp(20px,2.4vw,30px) 18px; text-align:center; border-left:1px solid var(--line)}}
#act .num:first-child{{border-left:none}}
#act .num b{{
  display:block; font-family:GmarketSans,sans-serif; font-weight:700; line-height:1.1;
  font-size:clamp(24px,3vw,38px); color:var(--deep); letter-spacing:-.03em
}}
#act .num b i{{font-style:normal; font-size:.52em; margin-left:2px}}
#act .num span{{display:block; margin-top:6px; font-size:12.5px; font-weight:600; color:var(--soft)}}

/* ───── 지금 (진행 중) ───── */
#act .now{{border-top:2px solid var(--ink)}}
#act .now li{{border-bottom:1px solid var(--line)}}
#act .now a{{display:block; padding:17px 2px}}
#act .now a:hover .t{{color:var(--deep); text-decoration:underline; text-underline-offset:3px}}
#act .now .t{{font-family:GmarketSans,sans-serif; font-weight:700; font-size:16px; line-height:1.5}}
#act .now .m{{display:flex; align-items:center; gap:8px; margin-top:6px; font-size:12.5px; color:var(--faint)}}
/* 마감이 있는 것에만 붙는 표시. 이슈로 옮길지 판단하는 기준이기도 합니다. */
#act .due{{background:var(--tint); color:var(--deep); border-radius:999px; padding:2px 10px; font-weight:700}}

/* ───── 결과 (사건 단위) ───── */
#act .res{{display:grid; gap:14px}}
#act .case{{background:#fff; border:1px solid var(--line); border-left:3px solid var(--brand); padding:22px 24px}}
#act .case h3{{font-size:17px; font-weight:700; line-height:1.45}}
#act .case .did{{margin-top:10px; font-size:14.5px; color:var(--soft); line-height:1.7}}
/* 화살표 줄이 '무엇이 바뀌었나' — 이 페이지에서 제일 중요한 한 줄입니다. */
#act .case .got{{margin-top:8px; padding-left:18px; position:relative; font-size:15px; font-weight:700; line-height:1.65}}
#act .case .got::before{{content:"→"; position:absolute; left:0; color:var(--brand)}}
#act .case .src{{display:flex; flex-wrap:wrap; gap:6px; margin-top:15px}}
#act .case .src a{{border:1px solid var(--line); border-radius:999px; padding:5px 12px; font-size:12.5px; color:var(--soft)}}
#act .case .src a:hover{{border-color:var(--brand); color:var(--deep)}}
#act .case .when{{margin-top:12px; font-size:12.5px; color:var(--faint)}}

/* ───── 글 목록 ───── */
#act .rows{{border-top:2px solid var(--ink)}}
#act .row{{display:flex; justify-content:space-between; gap:16px; align-items:baseline;
  padding:15px 2px; border-bottom:1px solid var(--line)}}
#act .row:hover .t{{color:var(--deep); text-decoration:underline; text-underline-offset:3px}}
#act .row .t{{font-family:GmarketSans,sans-serif; font-weight:700; font-size:15.5px; line-height:1.5}}
#act .row .meta{{font-size:12.5px; color:var(--faint); white-space:nowrap}}
#act .more{{display:inline-block; margin-top:18px; font-size:14px; font-weight:700; color:var(--deep)}}
#act .more:hover{{text-decoration:underline; text-underline-offset:3px}}

/* ───── 자료 ─────
   활동하면서 나온 보고서로 바로 가는 칸입니다.
   ⚠️ 지금은 셋 다 발행물(/23)로 갑니다. 활동별로 따로 모여 있다면 그 주소로 바꾸세요. */
#act .docs{{display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px}}
#act .doc{{
  display:flex; align-items:center; justify-content:space-between; gap:12px;
  border:1px solid var(--line); background:#fff; padding:16px 18px;
  font-size:14.5px; font-weight:700; line-height:1.4; transition:.16s
}}
#act .doc:hover{{border-color:var(--brand); color:var(--deep); transform:translateY(-2px)}}
#act .doc small{{display:block; margin-top:3px; font-size:12px; font-weight:600; color:var(--faint)}}
#act .doc .go{{flex:none; color:var(--brand)}}

/* ───── 현장 사진 ─────
   ⚠️ 사진이 한 장도 없으면 이 칸은 **아예 안 만들어집니다**(빌드에서 통째로 빠짐).
      점선 빈 자리를 두면 그 화면만 미완성으로 보이기 때문입니다.
      사진이 생기면 build-activity.py 의 PAGES[...]['photos'] 에 줄만 늘리세요.

   가로로 미는 줄인 이유: 활동 사진은 몇 장 될지 모릅니다. 격자로 두면
   3장일 때 한 칸이 비고 7장일 때 두 줄째가 어정쩡해집니다. 줄이면 몇 장이든 됩니다. */
#act .shots{{margin:0 calc(50% - 50vw); padding:0}}
#act .shots-rail{{
  display:flex; gap:12px; overflow-x:auto; scroll-snap-type:x proximity;
  padding:0 max(22px,calc((100vw - 880px) / 2)) 4px; scrollbar-width:none
}}
#act .shots-rail::-webkit-scrollbar{{display:none}}
#act .shot{{flex:0 0 clamp(230px,30vw,320px); scroll-snap-align:start}}
#act .shot figure{{margin:0}}
#act .shot .ph{{
  position:relative; aspect-ratio:4/3; overflow:hidden; background:var(--paper);
  border:1px solid var(--line)
}}
#act .shot .ph img{{position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block;
  transition:transform .5s}}
#act .shot:hover .ph img{{transform:scale(1.04)}}
#act .shot figcaption{{margin-top:9px; font-size:13px; color:var(--soft); line-height:1.55}}
#act .shot figcaption b{{display:block; font-family:GmarketSans,sans-serif; font-size:13.5px; color:var(--ink)}}
/* 줄 끝에 빈 칸 — 마지막 사진이 화면 끝에 딱 붙지 않게 */
#act .shots-rail::after{{content:""; flex:0 0 max(6px,calc((100vw - 880px) / 2))}}

/* ───── 다른 활동으로 ─────
   다섯 활동이 서로 이어져 있다는 것을 보여 주는 칸입니다.
   상단 메뉴로 다시 올라가지 않고 옆으로 건너갈 수 있게 합니다. */
#act .sibs{{display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:8px}}
#act .sib{{border:1px solid var(--line); padding:14px 16px; font-size:14.5px; font-weight:700; transition:.16s}}
#act .sib small{{display:block; margin-top:3px; font-size:11.5px; font-weight:600; color:var(--faint)}}
#act .sib:hover{{border-color:var(--brand); background:var(--tint); color:var(--deep)}}

/* ───── 연락 ───── */
#act .contact{{display:flex; gap:26px; flex-wrap:wrap; font-size:14.5px; color:var(--soft)}}
#act .contact b{{font-family:GmarketSans,sans-serif; color:var(--ink); display:block; font-size:13px}}
#act .contact a{{color:var(--deep)}}
#act .contact a:hover{{text-decoration:underline; text-underline-offset:3px}}

/* 스크롤로 들어올 때 살짝 올라오기.
   숨기는 상태는 스크립트가 붙입니다 — 막히면 그냥 다 보입니다. */
#act .rv.is-armed{{opacity:0; transform:translateY(12px)}}
#act .rv.is-in{{opacity:1; transform:none; transition:opacity .5s ease,transform .5s cubic-bezier(.22,.61,.36,1)}}

@media(max-width:640px){{
  #act{{font-size:15.5px}}
  #act .hero{{padding:34px 0}}
  #act .sec{{padding:34px 0}}
  #act .nums{{grid-template-columns:1fr}}
  #act .num{{border-left:none; border-top:1px solid var(--line); text-align:left; display:flex;
    align-items:baseline; gap:10px; padding:15px 20px}}
  #act .num:first-child{{border-top:none}}
  #act .num span{{margin-top:0}}
  #act .case{{padding:18px 18px}}
  /* 제목과 날짜가 서로 밀지 않게 아래위로 */
  #act .row{{flex-direction:column; gap:5px}}
  #act .contact{{gap:16px}}
}}
@media(prefers-reduced-motion:reduce){{
  #act *{{transition:none!important; animation:none!important}}
  #act .rv.is-armed{{opacity:1; transform:none}}
}}
</style>

<div id="act" aria-label="{title}">

  <!-- ───────── 히어로 ─────────
       ⚠️ 제목과 한 줄은 초안입니다. 실제 표현으로 바꿔 주세요. -->
  <section class="hero"><div class="wrap">
    <nav class="crumb"><a href="/69?preview_mode=1">홈</a><span>&rsaquo;</span><a href="/52">활동</a><span>&rsaquo;</span>{title}</nav>
    <span class="who">{who}</span>
    <h1>{headline}</h1>
    <p class="by">{lede}</p>
  </div></section>

  <!-- ───────── 숫자 셋 ─────────
       ⚠️ 확인된 값만 올립니다. 모르면 딱지를 붙이고 비워 두세요. -->
  <section class="nums">
{nums}
  </section>

  <div class="wrap">

    <!-- ───────── 지금 ───────── -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">NOW</span>
      <h2>지금 무엇을 보고 있나</h2>
      <p>끝나는 날짜가 붙은 일이 늘어나면 그건 '활동'이 아니라 '이슈'로 올립니다.</p>
    </div>
      <ul class="now">
{now}
      </ul>
    </section>

    <!-- ───────── 결과 ─────────
         사건 하나에 [무엇을 했나] + [무엇이 바뀌었나] 두 줄. 근거 글을 아래에 답니다.
         ⚠️ 확인된 사실만 적었습니다. 후속 조치나 성과 수치는 확인 전까지 쓰지 마세요. -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">RESULT</span>
      <h2>무엇이 달라졌나</h2>
      <p>글이 아니라 사건으로 적습니다. 무엇을 했고, 그래서 무엇이 바뀌었는지 두 줄입니다.</p>
    </div>
      <div class="res">
{result}
      </div>
    </section>

    <!-- ───────── 글 ─────────
         ⚠️ 코드에 박아 둔 목록이라 새 글이 자동으로 올라오지 않습니다.
            캠페이너스 기본 게시판 위젯으로 바꿀 자리입니다. -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">POSTS</span>
      <h2>최근에 쓴 글</h2>
      <p>{posts_note}</p>
    </div>
      <div class="rows">
{posts}
      </div>
      <a class="more" href="{board}">글 전체보기 →</a>
    </section>

    <!-- ───────── 자료 ─────────
         활동하면서 나온 보고서로 바로 가는 칸입니다.
         ⚠️ 셋 다 발행물(/23)로 걸어 뒀습니다. 활동별 자료 주소가 따로 있으면 바꾸세요. -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">LIBRARY</span>
      <h2>더 깊이 보려면</h2>
      <p>이 활동에서 나온 보고서와 자료를 모아 둔 곳입니다. <span class="tbd">주소 확인 필요</span></p>
    </div>
      <div class="docs">
        <a class="doc" href="/23">발행물<small>보고서 · 이슈페이퍼</small><span class="go" aria-hidden="true">→</span></a>
        <a class="doc" href="/24">뉴스룸<small>보도자료 · 언론보도</small><span class="go" aria-hidden="true">→</span></a>
        <a class="doc" href="{board}">게시판<small>{title} 글 전체</small><span class="go" aria-hidden="true">→</span></a>
      </div>
    </section>

{photos}
    <!-- ───────── 다른 활동 ───────── -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">OTHERS</span>
      <h2>시민행동이 하는 다른 일</h2>
    </div>
      <div class="sibs">
{sibs}
      </div>
    </section>

    <!-- ───────── 연락 ───────── -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">CONTACT</span>
      <h2>알려 주실 것이 있나요</h2>
    </div>
      <div class="contact">
        <p><b>제보 · 문의</b><a href="mailto:action@action.or.kr">action@action.or.kr</a></p>
        <p><b>전화</b><a href="tel:02-921-4709">02-921-4709</a></p>
        <p><b>소식</b><a href="/25">뉴스레터 받아보기</a></p>
        <p><b>함께하기</b><a href="https://donate.action.or.kr/">후원</a></p>
      </div>
    </section>

  </div>
</div>

<script>
/* 스크롤로 들어올 때 살짝 올라오기.
   숨기는 상태(.is-armed)를 스크립트가 직접 붙입니다. 그래서 스크립트가 막히면
   아무것도 안 숨겨지고 내용이 그냥 다 보입니다.
   ⚠️ 캠페이너스 코드 위젯이 <script> 를 실행하는지는 /69 에서 확인해야 합니다. */
(function () {{
  var items = document.querySelectorAll('#act .rv');
  if (!items.length || !('IntersectionObserver' in window)) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var io = new IntersectionObserver(function (es) {{
    es.forEach(function (e) {{
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      io.unobserve(e.target);
    }});
  }}, {{ rootMargin: '0px 0px -10% 0px' }});

  Array.prototype.forEach.call(items, function (el, i) {{
    el.classList.add('is-armed');
    el.style.transitionDelay = Math.min(i, 4) * 60 + 'ms';
    io.observe(el);
  }});
}})();
</script>
'''


# ══════════════════════════════════════════════════════════════════
#  활동 다섯 — 서로를 가리키는 데 씁니다
# ══════════════════════════════════════════════════════════════════
ALL = [
    ('local',  '지자체 감시',  '지방정부 · 지방의회', '/49'),
    ('power',  '권력감시',     '중앙정부 · 국회',     '/act-power'),
    ('budget', '예산감시',     '나라살림 · 지방재정', '/act-budget'),
    ('pb',     '시민참여',     '참여예산 제도 개선 · 시민 교육', '/51'),
    ('dok',    '밑빠진 독상',  '역대 기록 · 지도',    '/dok-history'),
]


# ══════════════════════════════════════════════════════════════════
#  페이지마다 다른 것
#
#  ⚠️ 지어낸 값을 넣지 마세요. 확인 안 된 것은 tbd=True 로 두면
#     화면에 '확인 필요' 딱지가 붙습니다.
# ══════════════════════════════════════════════════════════════════
PAGES = {
    'local': dict(
        # 현장 사진 — (주소, 대체글, 제목, 한 줄).
        # 비어 있으면 사진 칸이 화면에 아예 안 나옵니다.
        photos=[],
        headline='지방의회, 지켜보고 있습니다',
        lede='우리 동네 예산과 조례가 어떻게 정해지는지, 의회가 제 역할을 하는지 기록합니다.',
        board='/49',
        posts_note='⚠️ 아래 글은 실제 글이지만 예산 모니터링(/57)·일반 활동(/27) 게시판에 올라가 있습니다. 게시판이 정해지면 옮겨 주세요.',
        nums=[('27', '년', '1999년 창립 이후'),
              (None, None, '감시한 지자체 수'),
              (None, None, '올해 낸 의견서')],
        now=[('2026년 서울시 추가경정예산 심사 모니터링', '9월 심사', True, '#'),
             ('기초의회 의정비 인상안 전수 조사', None, True, '#')],
        result=[
            dict(t='한강버스 사업 경제성 검증', tbd=False,
                 did='경제성 근거가 공개되지 않은 채 추진되던 사업을 짚고, 감사 결과가 나온 뒤 쟁점을 정리해 알렸습니다.',
                 got='감사원 감사에서 경제성 B/C 0.17이 확인됐습니다.',
                 src=[('감사 결과 정리', '/27/?idx=172916152&amp;bmode=view'),
                      ('보류된 한강 개발 사업', '/57/?idx=171787220&amp;bmode=view')],
                 when='2026.06 – 2026.08'),
            dict(t='2026 지방선거 공약 검증', tbd=True,
                 did='서울시장 후보자들이 내놓은 예산·재정 공약을 모아 비교할 수 있게 정리했습니다.',
                 got='무엇이 달라졌는지는 아직 정리되지 않았습니다.',
                 src=[('후보자별 공약모음', '/57/?idx=171511879&amp;bmode=view'),
                      ('선거 결과와 그 이후', '/57/?idx=171642696&amp;bmode=view')],
                 when='2026.05 – 2026.06'),
        ],
        posts=[('그놈의 업무추진비, 축구협회와 양궁협회의 사정', '2026.07.03', '/57/?idx=172188605&amp;bmode=view'),
               ('오세훈의 한강사랑, 보류 중인 한강 개발 사업', '2026.06.12', '/57/?idx=171787220&amp;bmode=view'),
               ('6·3 지방선거 결과와 그 이후', '2026.06.12', '/57/?idx=171642696&amp;bmode=view')],
    ),

    'power': dict(
        # 현장 사진 — (주소, 대체글, 제목, 한 줄).
        # 비어 있으면 사진 칸이 화면에 아예 안 나옵니다.
        photos=[],
        headline='정부와 국회에,<br>시민의 이름으로 묻습니다',
        lede='중앙정부와 국회가 시민에게 설명하지 않고 넘어가려는 결정을 붙잡아 묻습니다.',
        board='/27',
        posts_note='⚠️ 이 활동은 2026-08-26 에 새로 만든 칸이라 전용 게시판이 아직 없습니다. 아래는 일반 활동(/27)·예산 모니터링(/57)에 올라간 실제 글 중 중앙정부·국회에 해당하는 것입니다.',
        nums=[('1999', '년', '창립'),
              (None, None, '올해 낸 논평 · 성명'),
              (None, None, '정보공개 청구 건수')],
        now=[('추가세수 100조 쓰임에 대한 시민 의견 수렴', '8월 31일', False,
              '/27/?idx=173013295&amp;bmode=view'),
             ('국민과 함께하는 지출구조조정 논의 대응', None, True, '#')],
        result=[
            dict(t='정부 예산요구서 공개 소송', tbd=True,
                 did='각 부처가 기획재정부에 낸 예산요구서를 공개하라고 요구하고, 거부되자 소송으로 다퉜습니다.',
                 got='대법원에서 승소해 예산요구서가 처음으로 공개됐습니다.',
                 src=[],
                 when='연도 확인 필요'),
            dict(t='미래대응기금 신설 논의', tbd=True,
                 did='충분한 사전 논의 없이 추진되던 기금 신설에 논평을 내고 쟁점을 정리했습니다.',
                 got='무엇이 달라졌는지는 아직 정리되지 않았습니다.',
                 src=[('논평 전문', '/27/?idx=172690687&amp;bmode=view')],
                 when='2026.07'),
        ],
        posts=[('[논평] 미래대응기금, 빠른 추진보다 충분한 사전논의가 먼저다.', '2026.07.27', '/27/?idx=172690687&amp;bmode=view'),
               ('국민과 함께하는 지출구조조정 토론회 쟁점, 질문 정리', '2026.06.18', '/57/?idx=171879037&amp;bmode=view'),
               ('그놈의 업무추진비, 축구협회와 양궁협회의 사정', '2026.07.03', '/57/?idx=172188605&amp;bmode=view')],
    ),

    'budget': dict(
        # 현장 사진 — (주소, 대체글, 제목, 한 줄).
        # 비어 있으면 사진 칸이 화면에 아예 안 나옵니다.
        photos=[],
        headline='세금이 어디로 갔는지<br>끝까지 따라갑니다',
        lede='나라살림과 지방재정을 들여다보고, 새는 곳을 찾아 기록하고 공개합니다.',
        board='/57',
        posts_note='예산 모니터링(/57) 게시판의 최근 글입니다.',
        nums=[('27', '년', '이어온 예산감시'),
              ('0', '원', '정부 · 기업 지원금'),
              (None, None, '올해 살펴본 사업 수')],
        now=[('2027년도 정부 예산안 분석', '9월 국회 제출', True, '#'),
             ('지자체 재정 투명성 점검', None, True, '#')],
        result=[
            dict(t='한강 개발 사업 재검토', tbd=True,
                 did='경제성 근거가 부족한 채 추진되던 한강 관련 사업들을 모아 쟁점을 정리했습니다.',
                 got='일부 사업이 보류됐습니다.',
                 src=[('보류 중인 한강 개발 사업', '/57/?idx=171787220&amp;bmode=view')],
                 when='2026.06'),
            dict(t='업무추진비 사용 실태 점검', tbd=True,
                 did='공공기관 업무추진비 집행 내역을 받아 쓰임을 확인했습니다.',
                 got='무엇이 달라졌는지는 아직 정리되지 않았습니다.',
                 src=[('축구협회와 양궁협회의 사정', '/57/?idx=172188605&amp;bmode=view')],
                 when='2026.07'),
        ],
        posts=[('활동가 수첩_농어촌소득에 재정의 3대 기능이?', '2026.07.23', '/57/?idx=172603339&amp;bmode=view'),
               ('그놈의 업무추진비, 축구협회와 양궁협회의 사정', '2026.07.03', '/57/?idx=172188605&amp;bmode=view'),
               ('국민과 함께하는 지출구조조정 토론회 쟁점, 질문 정리', '2026.06.18', '/57/?idx=171879037&amp;bmode=view')],
    ),
}


# ══════════════════════════════════════════════════════════════════
#  조각 만들기
# ══════════════════════════════════════════════════════════════════
def build_nums(rows):
    out = []
    for value, unit, label in rows:
        if value is None:
            body = u'<b><span class="tbd">확인 필요</span></b>'
        else:
            body = u'<b>%s<i>%s</i></b>' % (value, unit)
        out.append(u'    <div class="num">%s<span>%s</span></div>' % (body, label))
    return u'\n'.join(out)


def build_now(rows):
    out = []
    for title, due, tbd, href in rows:
        marks = []
        if due:
            marks.append(u'<span class="due">%s</span>' % due)
        if tbd:
            marks.append(u'<span class="tbd">확인 필요</span>')
        out.append(u'''        <li><a href="%s">
          <span class="t">%s</span>
          <span class="m">%s</span>
        </a></li>''' % (href, title, u''.join(marks)))
    return u'\n'.join(out)


def build_result(cases):
    out = []
    for c in cases:
        flag = u' <span class="tbd">확인 필요</span>' if c['tbd'] else u''
        src = u''
        if c['src']:
            links = u''.join(u'<a href="%s">%s →</a>' % (h, t) for t, h in c['src'])
            src = u'\n          <div class="src">%s</div>' % links
        out.append(u'''        <article class="case rv">
          <h3>%s%s</h3>
          <p class="did">%s</p>
          <p class="got">%s</p>%s
          <p class="when">%s</p>
        </article>''' % (c['t'], flag, c['did'], c['got'], src, c['when']))
    return u'\n'.join(out)


def build_posts(rows):
    return u'\n'.join(
        u'''        <a class="row" href="%s">
          <span class="t">%s</span>
          <span class="meta">%s</span>
        </a>''' % (href, title, when) for title, when, href in rows)


def build_photos(rows):
    """사진이 없으면 빈 문자열을 돌려줘 칸 자체가 안 만들어지게 합니다."""
    if not rows:
        return u''
    shots = u'\n'.join(
        u'''          <div class="shot"><figure>
            <span class="ph"><img src="%s" alt="%s" loading="lazy"></span>
            <figcaption><b>%s</b>%s</figcaption>
          </figure></div>''' % (src, alt, title, note)
        for src, alt, title, note in rows)
    return u'''
    <!-- ───────── 현장 사진 ─────────
         사진이 없으면 이 칸은 아예 안 나옵니다(build-activity.py 의 build_photos).
         사진을 늘리려면 PAGES[...]['photos'] 에 (주소, 대체글, 제목, 설명) 을 더하세요. -->
    <section class="sec"><div class="sh">
      <span class="eyebrow">FIELD</span>
      <h2>현장에서는 이런 일이 있었습니다</h2>
    </div></section>
    <div class="shots"><div class="shots-rail">
%s
    </div></div>
''' % shots


def build_sibs(me):
    out = []
    for key, name, who, href in ALL:
        if key == me:
            continue
        out.append(u'        <a class="sib" href="%s">%s<small>%s</small></a>' % (href, name, who))
    return u'\n'.join(out)


def main():
    for key, name, who, href in ALL:
        if key not in PAGES:
            continue
        d = PAGES[key]
        html = TEMPLATE.format(
            title=name,
            who=who,
            headline=d['headline'],
            lede=d['lede'],
            board=d['board'],
            posts_note=d['posts_note'],
            nums=build_nums(d['nums']),
            now=build_now(d['now']),
            result=build_result(d['result']),
            posts=build_posts(d['posts']),
            photos=build_photos(d.get('photos', [])),
            sibs=build_sibs(key),
        )
        out = os.path.join(ROOT, 'activity-%s.html' % key)
        io.open(out, 'w', encoding='utf-8').write(html)
        print(u'  %-24s %6d 바이트' % (os.path.basename(out), len(html.encode('utf-8'))))


if __name__ == '__main__':
    main()
