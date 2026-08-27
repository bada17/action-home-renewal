# -*- coding: utf-8 -*-
"""활동 페이지 네 장을 한 틀에서 찍어낸다.

    python tools/build-activity.py

만드는 파일
    activity-local.html    활동 > 지자체 감시 (지방정부 · 지방의회)
    activity-power.html    활동 > 권력감시   (중앙정부 · 국회)
    activity-budget.html   활동 > 예산감시   (나라살림 · 지방재정)
    activity-civic.html    활동 > 시민참여   (참여예산 제도 개선 · 시민 교육)

왜 손으로 안 쓰고 찍어내나
    네 장이 "같은 단체가 만든 것"으로 보여야 합니다. 손으로 네 번 쓰면
    여백이나 글씨 크기가 조금씩 어긋나고, 한 장만 고치는 일이 반드시 생깁니다.
    틀은 한 곳(TEMPLATE)에만 있고, 페이지마다 다른 것은 아래 PAGES 의 값뿐입니다.

    ★ 화면을 고치려면 이 파일의 TEMPLATE 을 고치고 다시 돌리세요.
      만들어진 .html 을 직접 고치면 다음에 돌릴 때 지워집니다.

색·글꼴·모양은 DESIGN.md 의 값을 그대로 씁니다. 여기 값을 바꾸면
DESIGN.md 와 다른 네 화면도 같이 고쳐야 합니다.
"""

import datetime
import io
import os
import sys

# 윈도우 콘솔은 기본이 cp949 라 한글·기호가 섞이면 print 에서 터집니다.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

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

  margin-left:calc(50% - 50vw + var(--ah-sb, 0px) / 2);margin-right:calc(50% - 50vw + var(--ah-sb, 0px) / 2);
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
#act .sh h2{{font-size:clamp(20px,2.3vw,27px); font-weight:700; line-height:1.4}}
#act .sh p{{margin-top:8px; font-size:14.5px; color:var(--soft); line-height:1.65; max-width:60ch}}

/* 확인 안 된 값 표시. 공개 전에 이 딱지가 화면에 하나도 없어야 합니다. */
#act .tbd{{background:var(--flag-bg); color:var(--flag); border:1px dashed var(--flag-line);
  border-radius:999px; padding:1px 8px; font-size:.8em; font-weight:700; white-space:nowrap}}

/* ───── 빵부스러기 ───── */
#act .crumb{{padding:16px 0 0; font-size:12.5px; font-weight:600; color:var(--deep)}}
#act .crumb span{{opacity:.45; margin:0 6px}}
#act .crumb a:hover{{text-decoration:underline; text-underline-offset:3px}}

/* ───── 맨 위 ─────  (2026-08-27 다시 짬)
   사용자 지적: 활동 페이지에 들어가면 **띠가 겹겹이** 쌓여 있어 마음에 안 든다.

   예전에는 짙은 남색 띠(히어로) 밑에 하늘색 띠(숫자 셋)가 또 있었습니다.
   색면 둘이 위아래로 붙어 제목이 그 안에 갇히고, 본문까지 내려가는 데
   화면 하나를 다 썼습니다.

   이제 색면을 아예 안 씁니다. 흰 바탕 위에
     빵부스러기 → 감시 대상 → 큰 제목 → 한 줄 → 숫자 셋
   이 한 흐름으로 이어지고, 굵은 선 하나로 본문과 갈립니다.
   띠가 사라지니 제목이 갇히지 않고 본문도 훨씬 빨리 나옵니다.

   ★ 활동 넷이 이 틀을 그대로 씁니다. 페이지마다 다르게 만들지 않습니다.
     구별은 아래 '이 활동만의 칸'이 합니다(지역 태그 / 물음과 답 / 달력 / 문). */
#act .top{{padding:clamp(20px,2.4vw,30px) 0 0; border-bottom:2px solid var(--ink)}}
#act .top .crumb{{padding:0}}
/* 감시 대상 — 활동 다섯이 '감시'라는 같은 말을 써서 이름만으로는 안 갈립니다.
   그래서 제목 위에 무엇을 보는 활동인지 먼저 말합니다. */
#act .top .who{{
  display:inline-block; margin-top:clamp(18px,2vw,26px);
  background:var(--tint); color:var(--deep); border-radius:999px;
  padding:5px 14px; font-size:12.5px; font-weight:700
}}
#act .top h1{{
  margin-top:12px;
  font-size:clamp(28px,4.4vw,46px); font-weight:700; line-height:1.24;
  letter-spacing:-.03em; text-wrap:balance
}}
#act .top .by{{
  margin-top:14px; font-size:clamp(14.5px,1.2vw,16.5px);
  color:var(--soft); max-width:52ch; line-height:1.7
}}

/* ───── 숫자 셋 ─────
   "이 활동이 얼마나 오래, 얼마나 많이" 를 한 줄로 보여 줍니다.
   맨 위 덩이의 마지막 줄입니다 — 예전처럼 따로 색 띠를 두르지 않습니다.
   왼쪽 정렬입니다. 가운데로 놓으면 위의 제목과 축이 어긋나 또 따로 노는 칸이 됩니다.
   ⚠️ 확인 안 된 숫자는 올리지 말고 딱지를 붙이세요. */
#act .nums{{
  display:grid; grid-auto-flow:column; grid-auto-columns:1fr;
  margin-top:clamp(26px,3vw,40px); border-top:1px solid var(--line)
}}
#act .num{{padding:clamp(16px,1.8vw,22px) 0; border-left:1px solid var(--line); padding-left:clamp(14px,1.6vw,20px)}}
#act .num:first-child{{border-left:none; padding-left:0}}
#act .num b{{
  display:block; font-family:GmarketSans,sans-serif; font-weight:700; line-height:1.1;
  font-size:clamp(24px,3vw,38px); color:var(--deep); letter-spacing:-.03em
}}
#act .num b i{{font-style:normal; font-size:.52em; margin-left:2px}}
/* 숫자 자리에 딱지가 오면 숫자 크기(최대 38px)를 물려받아 칸을 꽉 채웁니다.
   딱지는 값이 아니라 표시이므로 본문 크기로 되돌립니다. */
#act .num b .tbd{{display:inline-block; font-size:13.5px; letter-spacing:0; padding:4px 12px}}
#act .num span{{display:block; margin-top:6px; font-size:12.5px; font-weight:600; color:var(--soft)}}

/* ═════ 이 활동만의 칸 (2026-08-27) ═════
   활동 셋이 한 틀에서 나오다 보니 글자만 다르고 그림이 똑같다는 문제가 있었습니다.
   무늬를 아무거나 깔아 구별하는 대신, **활동마다 답하는 질문이 다르다**는 데서
   모양을 끌어냈습니다.

     지자체 감시 → "어디가 어떤가"      → 지역 이름을 늘어놓는다  (.sig-where)
     권력감시   → "누가 답을 안 하나"   → 물음과 답을 나란히 둔다 (.sig-ask)
     예산감시   → "언제 무엇이 정해지나" → 한 해 위에 오늘을 찍는다 (.sig-cal)

   셋 다 안 쓰는 활동에는 sig=None 을 주면 칸이 아예 안 만들어집니다. */

/* ───── 지자체 감시 — 올해 들여다본 곳 ───── */
#act .sig-where .tagbox{{display:flex; flex-wrap:wrap; gap:8px}}
#act .sig-where .tag{{
  border:1.5px solid var(--line); border-radius:999px; padding:7px 15px;
  font-size:14px; font-weight:700; color:var(--ink); background:#fff
}}
/* 여러 번 들여다본 곳은 진하게 — 어디에 힘이 실렸는지가 한눈에 보입니다. */
#act .sig-where .tag.is-hot{{border-color:var(--brand); background:var(--tint); color:var(--deep)}}
#act .sig-where .tag i{{font-style:normal; margin-left:6px; font-size:12px; opacity:.7}}
#act .sig-where .tagbox .tag.is-more{{border-style:dashed; color:var(--soft); font-weight:600}}

/* ───── 권력감시 — 물었는데, 아직 ─────
   "답 없음"이 화면에 계속 남아 있는 것 자체가 권력감시의 압박 방식입니다.
   그래서 답변 여부를 지우지 않고 오른쪽에 붙박이로 답니다. */
#act .sig-ask .asks{{border-top:2px solid var(--ink)}}
#act .sig-ask .ask{{
  display:flex; align-items:flex-start; justify-content:space-between; gap:16px;
  padding:15px 2px; border-bottom:1px solid var(--line)
}}
#act .sig-ask .ask .q{{font-size:15px; font-weight:700; line-height:1.55}}
#act .sig-ask .ask .to{{margin-top:4px; font-size:12.5px; color:var(--faint)}}
#act .sig-ask .st{{
  flex:none; border-radius:999px; padding:4px 12px;
  font-size:12.5px; font-weight:700; white-space:nowrap
}}
/* 네 가지 상태. 색이 곧 뜻이라 순서가 중요합니다 — 답 없음이 제일 눈에 띄어야 합니다. */
#act .sig-ask .st-none{{background:#fdecec; color:#a32020; border:1px solid #f3c9c9}}  /* 답변 없음 */
#act .sig-ask .st-deny{{background:var(--flag-bg); color:var(--flag); border:1px solid var(--flag-line)}}  /* 거부 */
#act .sig-ask .st-open{{background:var(--tint); color:var(--deep); border:1px solid #b8e2f5}}  /* 공개됨 */
#act .sig-ask .st-win{{background:var(--brand); color:#fff; border:1px solid var(--brand)}}   /* 소송 승소 */

/* ───── 예산감시 — 예산 한 해 ─────
   예산은 매년 같은 순서로 굴러가고 날짜가 법에 박혀 있습니다.
   그래서 이 칸만은 지어낸 값이 하나도 없습니다.
     국회 제출 = 회계연도 개시 120일 전 (국가재정법 제33조)  → 9월 2일
     국회 의결 = 회계연도 개시  30일 전 (헌법 제54조 2항)   → 12월 2일
   '오늘' 표시는 빌드할 때 한 번 찍고, 화면이 뜰 때 스크립트가 다시 맞춥니다. */
#act .sig-cal .cal{{position:relative; padding:34px 0 0}}
#act .sig-cal .bar{{position:relative; height:8px; background:var(--band); border-radius:999px}}
/* 지나온 구간을 브랜드색으로 채웁니다. */
#act .sig-cal .bar .done{{position:absolute; left:0; top:0; bottom:0; background:var(--brand); border-radius:999px}}
#act .sig-cal .marks{{position:relative; height:0}}
#act .sig-cal .mk{{position:absolute; top:-4px; width:2px; height:16px; background:var(--line); transform:translateX(-1px)}}
#act .sig-cal .mk.is-law{{background:var(--deep); width:3px}}
/* 오늘 — 위쪽에 뾰족한 표시와 날짜 */
#act .sig-cal .today{{position:absolute; top:-34px; transform:translateX(-50%); text-align:center; white-space:nowrap}}
#act .sig-cal .today b{{
  display:inline-block; background:var(--ink); color:#fff; border-radius:999px;
  padding:3px 11px; font-size:12px; font-weight:700; font-family:inherit
}}
#act .sig-cal .today::after{{
  content:""; display:block; margin:2px auto 0; width:0; height:0;
  border-left:5px solid transparent; border-right:5px solid transparent; border-top:6px solid var(--ink)
}}
/* 아래 단계 이름들 */
/* 칸 너비를 날짜 비율대로 줍니다(빌드할 때 flex 값을 찍습니다).
   균등하게 나누면 '국회 제출' 이름과 눈금이 서로 다른 자리에 서서, 보는 사람이
   9월 2일을 한 해의 3분의 1 지점으로 잘못 읽습니다. */
#act .sig-cal .steps{{display:flex; margin-top:14px}}
#act .sig-cal .step{{min-width:0; border-left:1px solid var(--line); padding:0 8px 0 10px}}
#act .sig-cal .step:first-child{{border-left:none; padding-left:0}}
#act .sig-cal .step b{{display:block; font-size:13.5px; font-weight:700; line-height:1.4}}
#act .sig-cal .step span{{display:block; margin-top:3px; font-size:11.5px; color:var(--faint); line-height:1.45}}
/* 지금 어느 단계인지 */
#act .sig-cal .step.is-now b{{color:var(--deep)}}
#act .sig-cal .step.is-now{{border-left-color:var(--brand)}}
#act .sig-cal .step.is-now b::before{{content:"● "; color:var(--brand); font-size:9px; vertical-align:2px}}
#act .sig-cal .law{{margin-top:16px; font-size:12.5px; color:var(--faint); line-height:1.6}}
#act .sig-cal .law b{{color:var(--soft)}}

/* ───── 시민참여 — 시민이 들어오는 문 ─────
   다른 넷은 "우리가 무엇을 보는가"를 말합니다. 이 활동만은 "시민이 무엇을 할 수
   있는가"를 말해야 해서, 감시 대상 대신 들어오는 문을 늘어놓습니다.
   그래서 이 칸의 줄은 읽는 것이 아니라 **누르는 것**입니다 — 카드가 아니라 문입니다. */
#act .sig-way .ways{{display:grid; grid-template-columns:1fr 1fr; gap:10px}}
#act .sig-way .way{{
  display:flex; flex-direction:column; gap:5px;
  border:1px solid var(--line); border-left:3px solid var(--brand);
  padding:16px 18px; background:#fff; transition:.15s
}}
#act .sig-way .way:hover{{border-color:var(--brand); background:var(--tint)}}
#act .sig-way .way:hover .wt{{color:var(--deep)}}
#act .sig-way .wt{{font-family:GmarketSans,sans-serif; font-weight:700; font-size:16px; line-height:1.4}}
#act .sig-way .wd{{font-size:13.5px; color:var(--soft); line-height:1.6}}
#act .sig-way .wm{{display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:5px}}
#act .sig-way .when{{font-size:12.5px; color:var(--faint)}}
/* 상태 알약 — 권력감시의 것과 같은 부품입니다. 색이 곧 뜻입니다. */
#act .sig-way .st{{
  border-radius:999px; padding:3px 11px;
  font-size:12px; font-weight:700; white-space:nowrap
}}
#act .sig-way .st-open{{background:var(--brand); color:#fff}}
#act .sig-way .st-soon{{background:var(--flag-bg); color:var(--flag); border:1px solid var(--flag-line)}}
#act .sig-way .st-closed{{background:var(--band); color:var(--faint)}}
@media(max-width:640px){{
  #act .sig-way .ways{{grid-template-columns:1fr}}
}}

/* ───── 지금 (진행 중) ─────
   사진 한 장 + 그 밑에 제목. 목록이 아니라 카드입니다.

   사진이 아직 없는 칸은 점선 빈 상자로 두지 않습니다 — 그 카드만 미완성으로
   보이기 때문입니다(DESIGN.md). 대신 브랜드 계열 색 타일에 제목에서 딴 큰 글자를
   깔아, 사진이 있는 카드와 무게가 같아지게 합니다. */
/* 카드 폭에 위아래를 둡니다(240~330px). 위가 없으면 칸이 둘일 때 사진만 커져
   화면을 다 잡아먹고, 아래가 없으면 좁은 화면에서 글자가 접힙니다. */
#act .now{{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,330px));
  justify-content:start;
  gap:clamp(14px,1.8vw,22px);
}}
@media(max-width:560px){{
  #act .now{{grid-template-columns:1fr}}
}}
#act .now li{{min-width:0}}
#act .now a{{display:flex; flex-direction:column; height:100%}}
#act .now a:hover .t{{color:var(--deep)}}
#act .now a:hover .shot{{transform:translateY(-2px)}}
#act .now a:hover .shot img{{transform:scale(1.04)}}

/* 액자 — 모든 카드가 똑같은 비율·똑같은 테두리를 씁니다. */
#act .now .shot{{
  position:relative; display:block; aspect-ratio:4/3; overflow:hidden;
  border:1px solid var(--line); background:var(--band);
  transition:transform .18s;
}}
#act .now .shot img{{
  position:absolute; inset:0; width:100%; height:100%;
  object-fit:cover; transition:transform .35s;
}}
/* 사진이 없을 때 깔리는 큰 글자. 읽으라고 둔 글자가 아니라 무늬입니다. */
#act .now .shot[data-mark]::before{{
  content:attr(data-mark);
  position:absolute; inset:0;
  display:flex; align-items:center; justify-content:center;
  font-family:GmarketSans,sans-serif; font-weight:700;
  font-size:clamp(38px,6vw,58px); letter-spacing:-.04em;
  color:var(--brand); opacity:.16;
}}
/* data-mark 는 사진이 없는 칸에만 붙습니다(build_now). 그래서 :has() 없이도
   사진이 있는 카드에는 글자 무늬가 깔리지 않습니다 — 옛 브라우저에서도 같습니다. */
#act .now .shot[data-mark]{{background:var(--tint)}}

#act .now .t{{
  display:block; margin-top:12px;
  font-family:GmarketSans,sans-serif; font-weight:700; font-size:15.5px;
  line-height:1.5; word-break:keep-all; transition:color .14s;
}}
#act .now .m{{display:flex; flex-wrap:wrap; align-items:center; gap:6px; margin-top:8px; font-size:12.5px; color:var(--faint)}}
#act .now .m:empty{{display:none}}
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
  #act .top{{padding-top:16px}}
  #act .sec{{padding:34px 0}}
  /* 좁은 화면에서는 숫자 셋을 세로로 눕힙니다. 셋을 가로로 두면 한 칸이 100px 밑으로
     떨어져 '감시한 지자체 수' 같은 이름이 석 줄로 접힙니다. */
  #act .nums{{grid-auto-flow:row; grid-auto-columns:auto; grid-template-columns:1fr}}
  #act .num{{border-left:none; border-top:1px solid var(--line); display:flex;
    align-items:baseline; gap:10px; padding:13px 0}}
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

<!-- PART:header -->
<!-- /PART:header -->

<div id="act" aria-label="{title}">

  <!-- ───────── 맨 위 ─────────
       빵부스러기 → 감시 대상 → 제목 → 한 줄 → 숫자 셋이 한 덩이입니다.
       ⚠️ 색 띠를 두르지 마세요. 띠를 겹치면 제목이 갇히고 본문이 밀립니다.
       ⚠️ 제목과 한 줄은 초안입니다. 실제 표현으로 바꿔 주세요.
       ⚠️ 숫자는 확인된 값만 올립니다. 모르면 딱지를 붙이고 비워 두세요. -->
  <section class="top"><div class="wrap">
    <nav class="crumb"><a href="/69?preview_mode=1">홈</a><span>&rsaquo;</span>활동<span>&rsaquo;</span>{title}</nav>
    <span class="who">{who}</span>
    <h1>{headline}</h1>
    <p class="by">{lede}</p>
    <div class="nums">
{nums}
    </div>
  </div></section>

  <div class="wrap">
{signature}
    <!-- ───────── 지금 ───────── -->
    <section class="sec"><div class="sh">
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
      <h2>시민행동이 하는 다른 일</h2>
    </div>
      <div class="sibs">
{sibs}
      </div>
    </section>

    <!-- ───────── 연락 ───────── -->
    <section class="sec"><div class="sh">
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
    ('civic',  '시민참여',     '참여예산 제도 개선 · 시민 교육', '/51'),
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

        # ── 이 활동만의 칸 ──
        # 지자체 감시는 "어디가 어떤가"에 답하는 활동이라, 들여다본 곳을 늘어놓습니다.
        # (이름, 건수 또는 None, 여러 번 본 곳인지)
        #
        # ⚠️ 아래는 이 페이지에 이미 근거가 있는 것만 적었습니다(한강버스·공약검증 →
        #    서울시 / 의정비 전수조사 → 전국 기초의회). 지어낸 지역은 하나도 없습니다.
        #    올해 실제로 들여다본 지자체 목록으로 바꿔 주세요. 개수가 곧 활동량입니다.
        #    지도로 안 그리는 이유: 활동 메뉴 안에 이미 밑빠진 독상 지도가 있어서
        #    지도가 둘이면 둘 다 흐려집니다.
        sig=dict(
            kind='where',
            title='올해 들여다본 곳',
            lead='한 곳을 오래 보는 것보다, 여러 곳을 같은 잣대로 보는 것이 지자체 감시입니다.',
            tbd=True,
            tags=[('서울특별시', 3, True),
                  ('전국 기초의회', None, True)],
            more='올해 들여다본 지자체를 여기에',
        ),
        headline='지방의회, 지켜보고 있습니다',
        lede='우리 동네 예산과 조례가 어떻게 정해지는지, 의회가 제 역할을 하는지 기록합니다.',
        board='/49',
        posts_note='⚠️ 아래 글은 실제 글이지만 예산 모니터링(/57)·일반 활동(/27) 게시판에 올라가 있습니다. 게시판이 정해지면 옮겨 주세요.',
        nums=[(None, None, '감시한 지자체 수'),
              (None, None, '올해 낸 의견서')],
        # 사진이 오면 img='주소', alt='설명' 을 더하면 됩니다.
        # mark 는 사진이 없는 동안 타일에 깔리는 큰 글자입니다(제목의 줄임말).
        now=[dict(t='2026년 서울시 추가경정예산 심사 모니터링', due='9월 심사',
                  tbd=True, href='#', mark='추경'),
             dict(t='기초의회 의정비 인상안 전수 조사',
                  tbd=True, href='#', mark='의정비')],
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

        # ── 이 활동만의 칸 ──
        # 권력감시는 "누가 답을 안 하나"에 답하는 활동입니다.
        # 답이 없는 물음을 화면에서 지우지 않고 계속 남겨 두는 것 자체가 압박입니다.
        # (물음, 받는 곳, 상태키, 한 줄)
        #   상태키 — none: 답변 없음 / deny: 거부 / open: 공개됨 / win: 소송 승소
        #
        # ⚠️ 아래 둘은 이 페이지 '결과' 칸에 이미 있는 사실입니다. 새로 지어낸 것이 없습니다.
        #    정보공개 청구·질의 목록을 받으면 여기에 줄을 늘려 주세요. 이 칸은
        #    줄이 많을수록 세집니다.
        sig=dict(
            kind='ask',
            title='물었는데, 아직',
            lead='시민을 대신해 물은 것과, 돌아온 답을 그대로 적습니다. 답이 없으면 없는 채로 남겨 둡니다.',
            tbd=True,
            asks=[('부처별 예산요구서를 공개하라', '기획재정부', 'win',
                   '거부 → 소송 → 대법원 승소. 예산요구서가 처음으로 공개됐습니다.'),
                  ('미래대응기금 신설의 산출 근거를 밝혀라', '기획재정부 · 국회', 'none',
                   '논평으로 쟁점을 냈지만 근거는 아직 제시되지 않았습니다.')],
        ),
        headline='정부와 국회에,<br>시민의 이름으로 묻습니다',
        lede='중앙정부와 국회가 시민에게 설명하지 않고 넘어가려는 결정을 붙잡아 묻습니다.',
        board='/27',
        posts_note='⚠️ 이 활동은 2026-08-26 에 새로 만든 칸이라 전용 게시판이 아직 없습니다. 아래는 일반 활동(/27)·예산 모니터링(/57)에 올라간 실제 글 중 중앙정부·국회에 해당하는 것입니다.',
        nums=[(None, None, '올해 낸 논평 · 성명'),
              (None, None, '정보공개 청구 건수')],
        now=[dict(t='추가세수 100조 쓰임에 대한 시민 의견 수렴', due='8월 31일',
                  href='/27/?idx=173013295&amp;bmode=view', mark='100조'),
             dict(t='국민과 함께하는 지출구조조정 논의 대응',
                  tbd=True, href='#', mark='지출')],
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

        # ── 이 활동만의 칸 ──
        # 예산감시는 "언제 무엇이 정해지나"에 답하는 활동입니다.
        # 예산은 매년 같은 순서로 굴러가고 날짜가 법에 박혀 있어서,
        # **이 칸에는 확인이 필요한 값이 하나도 없습니다.** 그래서 딱지도 안 붙습니다.
        # 시민에게 "지금이 의견 낼 때"를 알려 주는 것이 이 칸의 쓸모입니다.
        sig=dict(
            kind='cal',
            title='지금 예산은 여기쯤',
            lead='나라 예산은 해마다 같은 순서로 정해집니다. 의견을 낼 수 있는 때도 정해져 있습니다.',
            tbd=False,
        ),
        headline='세금이 어디로 갔는지<br>끝까지 따라갑니다',
        lede='나라살림과 지방재정을 들여다보고, 새는 곳을 찾아 기록하고 공개합니다.',
        board='/57',
        posts_note='예산 모니터링(/57) 게시판의 최근 글입니다.',
        nums=[('27', '년', '이어온 예산감시'),
              ('0', '원', '정부 · 기업 지원금'),
              (None, None, '올해 살펴본 사업 수')],
        now=[dict(t='2027년도 정부 예산안 분석', due='9월 국회 제출',
                  tbd=True, href='#', mark='예산안'),
             dict(t='지자체 재정 투명성 점검',
                  tbd=True, href='#', mark='재정')],
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

    'civic': dict(
        # 현장 사진 — (주소, 대체글, 제목, 한 줄).
        # 비어 있으면 사진 칸이 화면에 아예 안 나옵니다.
        photos=[],

        # ── 이 활동만의 칸 ──
        # 시민참여는 "시민이 어디로 들어오나"에 답하는 활동입니다.
        # 다른 넷은 우리가 무엇을 보는지를 말하지만, 이 활동은 **시민이 할 수 있는 것**을
        # 말해야 합니다. 그래서 감시 대상이 아니라 '들어오는 문'을 늘어놓습니다.
        #
        # ⚠️ 아래 넷은 이미 근거가 있는 것만 적었습니다(상담소·고민대회는 이슈 목록에,
        #    10만원 편성은 vote.action.or.kr 에, 주민참여예산은 /51 게시판에 있습니다).
        #    '지금 열려 있나'가 확인 안 된 것은 tbd=True 로 두었습니다.
        sig=dict(
            kind='way',
            title='시민이 들어오는 문',
            lead='예산은 전문가만 다루는 것이 아닙니다. 지금 열려 있는 문이 어디인지 알려 드립니다.',
            tbd=True,
            ways=[
                ('참여예산 상담소',
                 '참여예산위원으로 활동하다 막히는 것을 물어보는 곳입니다.',
                 '/pb/', 'open', '상시'),
                ('10만원 예산편성',
                 '내 몫의 예산 10만원을 어디에 쓸지 직접 편성해 봅니다.',
                 'https://vote.action.or.kr/', 'open', '기간 확인 필요'),
                ('1회 참여예산 고민대회',
                 '참여예산위원들이 현장에서 부딪히는 고민을 모아 함께 풉니다.',
                 '#', 'soon', '주소 · 기간 확인 필요'),
                ('주민참여예산 게시판',
                 '제도가 어디까지 왔는지, 무엇을 요구하고 있는지 모아 둔 곳입니다.',
                 '/51', 'open', '상시'),
            ],
        ),
        headline='예산을 정하는 자리에<br>시민이 앉아야 합니다',
        lede='주민참여예산 제도가 이름만 남지 않도록 따지고, 시민이 실제로 결정할 수 있게 바꿉니다.',
        board='/51',
        posts_note='주민참여예산(/51) 게시판의 최근 글입니다.',
        nums=[(None, None, '올해 연 상담 · 교육'),
              (None, None, '제도 개선 의견서')],
        now=[dict(t='주민참여예산 3조원 확대, 주민 권한 확보 요구', due='정부안 발표 뒤',
                  tbd=True, href='/51/?idx=172917373&amp;bmode=view', mark='3조'),
             dict(t='지방재정법 개정안 입법 대응',
                  tbd=True, href='/51/?idx=170491595&amp;bmode=view', mark='입법')],
        result=[
            dict(t='주민참여예산 제도 개선 입법 요구', tbd=True,
                 did='주민참여예산제도를 활성화하는 지방재정법 개정안을 정리해 알렸습니다.',
                 got='무엇이 달라졌는지는 아직 정리되지 않았습니다.',
                 src=[('지방재정법 개정안', '/51/?idx=170491595&amp;bmode=view')],
                 when='2026.03'),
            dict(t='주민결정권 강화 요구', tbd=True,
                 did='주민참여예산의 주민결정권을 실질적으로 강화할 방안을 요구하는 논평을 냈습니다.',
                 got='무엇이 달라졌는지는 아직 정리되지 않았습니다.',
                 src=[('논평 전문', '/27/?idx=170224688&amp;bmode=view')],
                 when='2026.03'),
        ],
        posts=[("주민참여예산 3조원 확대, 규모보다 ‘주민 권한’이 먼저다", '2026.08.06', '/51/?idx=172917373&amp;bmode=view'),
               ('[입법활동] 주민참여예산제도 활성화를 위한 지방재정법 개정안', '2026.03.22', '/51/?idx=170491595&amp;bmode=view'),
               ('[논평] 주민참여예산의 주민결정권을 강화하기 위한 실질적인 제도 추진 방안이 마련되어야 한다.', '2026.03.02', '/27/?idx=170224688&amp;bmode=view')],
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
    """'지금 무엇을 보고 있나' — 사진 한 장 + 그 밑에 제목.

    한 줄은 dict 입니다.
        t     제목 (필수)
        href  누르면 갈 곳 (필수)
        due   마감 표시. 없으면 안 붙습니다
        tbd   확인 안 된 값이면 True → '확인 필요' 딱지
        img   사진 주소. 없으면 색 타일이 대신 들어갑니다
        alt   사진 설명 (img 가 있을 때만 씁니다)
        mark  사진이 없을 때 타일에 깔 큰 글자. 제목에서 딴 두세 글자.
              지어낸 말이 아니라 제목의 줄임말이어야 합니다.
    """
    out = []
    for r in rows:
        marks = []
        if r.get('due'):
            marks.append(u'<span class="due">%s</span>' % r['due'])
        if r.get('tbd'):
            marks.append(u'<span class="tbd">확인 필요</span>')

        if r.get('img'):
            # 사진이 있으면 data-mark 를 붙이지 않습니다 — 글자 무늬가 사진을 덮습니다.
            shot = u'<span class="shot"><img src="%s" alt="%s" loading="lazy"></span>' % (
                r['img'], r.get('alt', u''))
        else:
            shot = u'<span class="shot" data-mark="%s" aria-hidden="true"></span>' % r.get('mark', u'')

        out.append(u'''        <li><a href="%s">
          %s
          <span class="t">%s</span>
          <span class="m">%s</span>
        </a></li>''' % (r['href'], shot, r['t'], u''.join(marks)))
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
      <h2>현장에서는 이런 일이 있었습니다</h2>
    </div></section>
    <div class="shots"><div class="shots-rail">
%s
    </div></div>
''' % shots


# ══════════════════════════════════════════════════════════════════
#  이 활동만의 칸 (2026-08-27)
#
#  왜 있나: 활동 셋이 한 틀에서 나와 글자만 다르고 그림이 똑같았습니다.
#  무늬로 구별하는 대신 **활동마다 답하는 질문이 다르다**는 데서 모양을 끌어냈습니다.
#
#      지자체 감시 → "어디가 어떤가"       → 지역 이름을 늘어놓는다  (where)
#      권력감시   → "누가 답을 안 하나"    → 물음과 답을 나란히 둔다 (ask)
#      예산감시   → "언제 무엇이 정해지나" → 한 해 위에 오늘을 찍는다 (cal)
#
#  sig 가 없는 활동은 빈 문자열이 돌아가 칸 자체가 안 만들어집니다.
# ══════════════════════════════════════════════════════════════════

# 나라 예산 한 해. 날짜가 법에 박혀 있어 해마다 같습니다.
#   국회 제출 = 회계연도 개시 120일 전 (국가재정법 제33조)  → 9월 2일
#   국회 의결 = 회계연도 개시  30일 전 (헌법 제54조 2항)   → 12월 2일
#
# 띠의 끝을 12월 31일이 아니라 **12월 2일(의결)** 로 잡은 이유:
# 이 그림이 보여 주려는 것은 '예산이 정해지는 과정'이고, 그 과정은 의결로 끝납니다.
# 집행·결산은 그 뒤의 다른 이야기라 띠 밑에 한 줄로 적습니다.
#
# 단계 경계를 균등하게 벌리지 않습니다. '9월 2일이 실제로 한 해의 3분의 2 지점'
# 이라는 게 이 그림이 알려 주려는 사실이기 때문입니다.
# 그래서 아래 칸 너비도 날짜 비율 그대로 잡습니다 — 눈금과 이름이 어긋나면 안 됩니다.
CAL_END = (12, 2)
BUDGET_STEPS = [
    ((1, 1), (6, 1),  u'부처 요구', u'각 부처가 필요한 돈을 적어 냅니다<br>~5월 31일'),
    ((6, 1), (9, 2),  u'정부 편성', u'기획재정부가 정부안을 짭니다<br>6~8월'),
    ((9, 2), CAL_END, u'국회 심사', u'상임위·예결위가 따집니다<br>9월 2일 제출 → 12월 2일 의결'),
]


def _cal_pct(year, month, day):
    """그 날짜가 '예산이 정해지는 한 해'의 몇 %쯤인지 (1월 1일 = 0, 12월 2일 = 100)."""
    import datetime as _dt
    start = _dt.date(year, 1, 1)
    span = float((_dt.date(year, CAL_END[0], CAL_END[1]) - start).days) or 1.0
    at = (_dt.date(year, month, day) - start).days / span * 100.0
    return max(0.0, min(100.0, at))


def _cal_now(today):
    """오늘이 몇 번째 단계인지. 의결이 지났으면 마지막 단계로 둡니다."""
    idx = 0
    for i, (begin, _, _, _) in enumerate(BUDGET_STEPS):
        if (today.month, today.day) >= begin:
            idx = i
    return idx


def build_sig(d):
    """활동마다 하나씩 있는 고유한 칸. sig 가 없으면 빈 문자열."""
    sig = d.get('sig')
    if not sig:
        return u''

    NL = u'\n'
    flag = u' <span class="tbd">채울 값 있음</span>' if sig.get('tbd') else u''
    kind = sig['kind']

    head = (
        u'    <!-- ───────── 이 활동만의 칸 ───────── -->' + NL +
        u'    <section class="sec sig sig-%s"><div class="sh">' % kind + NL +
        u'      <h2>%s%s</h2>' % (sig['title'], flag) + NL +
        u'      <p>%s</p>' % sig['lead'] + NL +
        u'    </div>' + NL
    )

    # ── 지자체 감시 — 들여다본 곳을 늘어놓기 ──
    if kind == 'where':
        tags = []
        for name, n, hot in sig['tags']:
            cnt = u'<i>%d건</i>' % n if n else u''
            cls = u' is-hot' if hot else u''
            tags.append(u'<span class="tag%s">%s%s</span>' % (cls, name, cnt))
        if sig.get('more'):
            tags.append(u'<span class="tag is-more">＋ %s</span>' % sig['more'])
        body = u'      <div class="tagbox rv">%s</div>' % u''.join(tags) + NL

    # ── 권력감시 — 물음과 돌아온 답 ──
    elif kind == 'ask':
        names = {'none': u'답변 없음', 'deny': u'거부',
                 'open': u'공개됨', 'win': u'소송 승소'}
        rows = []
        for q, to, st, note in sig['asks']:
            rows.append(
                u'        <li class="ask rv">' + NL +
                u'          <span>' + NL +
                u'            <span class="q">%s</span>' % q + NL +
                u'            <span class="to">%s · %s</span>' % (to, note) + NL +
                u'          </span>' + NL +
                u'          <span class="st st-%s">%s</span>' % (st, names[st]) + NL +
                u'        </li>'
            )
        body = (u'      <ul class="asks">' + NL + NL.join(rows) + NL +
                u'      </ul>' + NL)

    # ── 예산감시 — 한 해 흐름 위에 오늘 찍기 ──
    elif kind == 'cal':
        today = datetime.date.today()
        y = today.year
        pct = _cal_pct(y, today.month, today.day)
        now_idx = _cal_now(today)
        done = (today.month, today.day) > CAL_END

        marks, steps = [], []
        for i, (begin, end, name, note) in enumerate(BUDGET_STEPS):
            left = _cal_pct(y, begin[0], begin[1])
            right = _cal_pct(y, end[0], end[1])
            # 칸 너비 = 그 단계가 실제로 차지하는 날짜 비율. 눈금과 정확히 맞습니다.
            law = u' is-law' if begin == (9, 2) else u''
            marks.append(u'<span class="mk%s" style="left:%.2f%%"></span>' % (law, left))
            steps.append(
                u'          <div class="step%s" style="flex:0 0 %.2f%%"><b>%s</b><span>%s</span></div>'
                % (u' is-now' if i == now_idx else u'', right - left, name, note))
        # 마지막 눈금 — 12월 2일 의결
        marks.append(u'<span class="mk is-law" style="left:100%"></span>')

        body = (
            u'      <div class="cal rv">' + NL +
            u'        <div class="today" style="left:%.2f%%"><b>오늘 %d월 %d일</b></div>'
            % (pct, today.month, today.day) + NL +
            u'        <div class="bar"><span class="done" style="width:%.2f%%"></span></div>'
            % pct + NL +
            u'        <div class="marks">%s</div>' % u''.join(marks) + NL +
            u'        <div class="steps">' + NL +
            NL.join(steps) + NL +
            u'        </div>' + NL +
            u'      </div>' + NL +
            u'      <p class="law">' + NL +
            u'        띠는 <b>예산이 정해지는 과정</b>입니다. 의결된 예산은 이듬해에 집행하고, ' +
            u'그 이듬해에 결산합니다.' + (u' 올해 몫은 이미 확정됐습니다.' if done else u'') + NL +
            u'        <br><b>국회 제출 9월 2일</b>은 국가재정법 제33조(회계연도 개시 120일 전), ' + NL +
            u'        <b>국회 의결 12월 2일</b>은 헌법 제54조 2항(회계연도 개시 30일 전)이 정한 날입니다. ' + NL +
            u'        이 칸에는 확인이 필요한 값이 없습니다 — 날짜가 법에 박혀 있기 때문입니다.' + NL +
            u'      </p>' + NL
        )

    # ── 시민참여 — 시민이 들어오는 문 ──
    #    다른 넷은 "우리가 무엇을 보는가"를 말합니다. 이 활동만은
    #    "시민이 무엇을 할 수 있는가"를 말해야 해서, 감시 대상이 아니라 문을 늘어놓습니다.
    elif kind == 'way':
        names = {'open': u'지금 열림', 'soon': u'준비 중', 'closed': u'닫힘'}
        rows = []
        for name, note, href, st, when in sig['ways']:
            flag = u' <span class="tbd">확인 필요</span>' if u'확인 필요' in when else u''
            shown = when.replace(u' 확인 필요', u'') if flag else when
            rows.append(
                u'        <a class="way rv" href="%s">' % href + NL +
                u'          <span class="wt">%s</span>' % name + NL +
                u'          <span class="wd">%s</span>' % note + NL +
                u'          <span class="wm">' + NL +
                u'            <span class="st st-%s">%s</span>' % (st, names[st]) + NL +
                u'            <span class="when">%s%s</span>' % (shown, flag) + NL +
                u'          </span>' + NL +
                u'        </a>'
            )
        body = (u'      <div class="ways">' + NL + NL.join(rows) + NL +
                u'      </div>' + NL)

    else:
        raise ValueError(u'모르는 칸 종류: %s' % kind)

    return NL + head + body + u'    </section>' + NL


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
            signature=build_sig(d),
        )
        out = os.path.join(ROOT, 'activity-%s.html' % key)
        io.open(out, 'w', encoding='utf-8', newline='\n').write(html)
        print(u'  %-24s %6d 바이트' % (os.path.basename(out), len(html.encode('utf-8'))))

    # 방금 찍어낸 네 장에는 헤더 자리가 비어 있습니다. 공통 헤더를 이어서 심습니다.
    # (따로 돌리는 걸 잊으면 활동 페이지에만 목차가 없어집니다.)
    print(u'\n  공통 헤더 심기 —')
    import subprocess
    subprocess.call([sys.executable, os.path.join(HERE, 'build-parts.py')])


if __name__ == '__main__':
    main()
