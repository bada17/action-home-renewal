# 시민참여 상담소 — 개편 작업에 넘기는 인계 문서 (2026-09-08)

이 저장소 안의 **`pb.html`** 에 대한 것입니다. 개편 홈을 만지는 사람이
**이것만 알면** 상담소를 망가뜨리지 않습니다.

---

## 1. 이름과 주소가 바뀌었습니다 — README 의 옛 기록을 믿지 마세요

| | 옛 기록(틀림) | **지금(맞음)** |
|---|---|---|
| 이름 | 참여예산 상담소 | **시민참여 상담소** |
| 주소 | `pb-action-site.pages.dev` | **`https://pb.action.or.kr`** |
| 어디서 서비스 | Cloudflare Pages | **GitHub Pages** (`bada17/pb-action-site`) |

- HTTPS 됐습니다. `http://` 로 와도 자동으로 넘어갑니다.
- 검색도 열었습니다(`robots.txt` 를 `Allow: /` 로).
- **Cloudflare Pages 는 안 씁니다.** `*.pages.dev` 주소를 어디에도 걸지 마세요.
  push 로 갱신되지 않아서 "왜 반영이 안 되냐"로 시간을 버린 적이 있습니다.

**개편 홈에서 상담소로 거는 링크는 전부 `https://pb.action.or.kr` 입니다.**
(캠페이너스 `/80` 자리에 걸던 링크가 이것입니다. 새 탭으로 엽니다.)

---

## 2. ⚠️ `pb.html` 은 개편 홈의 한 페이지가 아닙니다

이 저장소에 **원본이** 있지만, 나가는 곳은 **딴 사이트**입니다.
그래서 여기서 `pb.html` 만 고치고 push 하면 **사는 화면은 그대로입니다.**

고쳤으면 이 세 걸음을 끝까지 밟아야 합니다.

```
1) 이 저장소에서 pb.html 을 고친다
2) 상담소 저장소에서 다시 굽는다
     cd C:/Users/dbqke/participatory-budget
     PB_SOURCE=<이 저장소>/pb.html \
     PB_FOOTER=<이 저장소>/tools/parts/footer.html \
     python build.py
   → participatory-budget/index.html 이 새로 써집니다
3) 그 index.html 을 배포 저장소에 복사해 push
     <OneDrive…>/pb-action-site/index.html
   → GitHub Pages 가 1분 안에 반영합니다
```

⚠️ `PB_SOURCE` · `PB_FOOTER` 를 **꼭 주세요.** 안 주면 기본값
`C:\Users\dbqke\action-home-renewal` 을 보는데, 개편 저장소는 거기 없습니다.
⚠️ `PB_FOOTER` 는 `footer.html` 이 아니라 **`tools/parts/footer.html`** 입니다.

---

## 3. 하단(footer)을 고치면 상담소도 다시 구워야 합니다

상담소 화면의 하단은 **이 저장소의 `tools/parts/footer.html` 에서 구워 넣습니다.**
개편 홈의 하단을 바꾸면 상담소 하단은 **옛것 그대로 남습니다.**
하단을 손댔으면 위 2번을 한 번 돌려 주세요.

---

## 4. 위원 사진 파일 이름 규칙

`img/p1.webp` … `img/p5.webp` 입니다. **실명으로 짓지 마세요.**
파일 주소가 화면에 그대로 드러나서, 실명이면 이름만 검색해도 걸립니다.
(2026-09-08 에 `kimmincheol.webp` 같은 옛 이름에서 바꿨습니다.)

- **다음 위원은 `p6`** 입니다.
- 사진 다듬는 법은 `participatory-budget/make-photo.py` 머리말에 있습니다.
- ⚠️ **사진 파일과 고친 화면은 반드시 한 커밋으로 함께 올리세요.**
  따로 올리면 그 사이 화면이 옛 이름을 가리켜 사진이 다 깨집니다.

---

## 5. 손대면 안 되는 것

- **`.cyc` 다섯 딱지**(정보를 안다 → … → 다시 제도 개선에 참여한다) —
  꾸밈이 아니라 이 위원회가 말하는 '참여'의 정의입니다. 차례를 지키세요.
- **걸어온 길 맺음말 `.snote-claim` 의 세 마디** — 앞의 둘('그치지 않고')을
  딛고 셋째('실질적인 제도의 변화까지')로 올라섭니다. 앞 둘을 지우면 구호가 됩니다.
- **문답·전문위원의 글을 불러오는 접수처 주소**(Apps Script). `build.py` 가 넣습니다.

## 6. 개인정보처리방침

상담소 것은 **`PRIVACY-pb.md`** 입니다. 홈(`PRIVACY.md`)·밑빠진 독상(`PRIVACY-dok.md`)과
**각각 완전체**로 두기로 했습니다. 합치지 마세요.

---

## 지금 상태 (2026-09-08 기준)

| 저장소 | 커밋 |
|---|---|
| 개편(이 저장소) `pb.html` | `8f02617` |
| 상담소 `bada17/participatory-budget` | `7477abf` |
| 배포 `bada17/pb-action-site` | `8c8ba39` |

셋 다 푸시됨. 사는 화면이 구운 파일과 같습니다.
사람이 채울 내용(전문위원 글 올리기, 질문에 답 달기)만 남았고,
그 방법은 `participatory-budget/TODO.md` 에 있습니다.
