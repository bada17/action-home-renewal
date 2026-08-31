/**
 * 서명 접수 — 구글 시트에 쌓기 (Google Apps Script)
 *
 * 이 파일은 이 저장소에서 돌아가지 않습니다. 구글 스프레드시트에 붙여 넣는 코드입니다.
 * 켜는 순서는 SIGN.md 에 있습니다. 여기서는 무엇을 하는 코드인지만 적습니다.
 *
 *   POST /exec                          서명 접수 → 시트에 한 줄, { ok:true, count:n }
 *   GET  /exec?action=count&c=<캠페인>   지금까지 몇 명  → { count:n }
 *   GET  /exec?action=recent&c=<캠페인>  최근 서명 (이름을 가려서)  ※ 꺼져 있음
 *
 * 서명이 들어오면 이어서 하는 일 셋
 *   1. 시트에 적기
 *   2. **접수 확인 메일 보내기** — 안 보내면 "된 건가?" 하고 또 누르고,
 *      이메일 오타를 아무도 못 잡습니다(나중에 결과를 알릴 주소가 죽어 있습니다)
 *   3. 소식 받기에 동의했으면 **스티비 주소록에 넣기** — 손으로 옮기면 반드시 빠뜨립니다
 *
 * ⚠️ 이 시트에는 이름·이메일·전화번호가 쌓입니다. 개인정보입니다.
 *    · 시트를 '링크가 있는 모든 사용자'로 공유하지 마세요. 담당자만 여세요.
 *    · 내려받은 파일(엑셀·CSV)도 같은 개인정보입니다. 아무 폴더에나 두지 마세요.
 *    · 보유기간이 지나면 지워야 합니다. 기간은 단체가 정해 동의문에 적은 값입니다.
 *
 * ⚠️ 이 파일을 고친 뒤에는 '배포 › 배포 관리 › 수정 › 버전: 새 버전' 으로 다시
 *    배포해야 반영됩니다. 주소(/exec)는 그대로 유지됩니다.
 */

/* ── 고쳐 쓰는 값 ─────────────────────────────────────── */

/* 동의문을 고칠 때마다 이 날짜를 올리세요.
   누가 어느 판의 동의문에 동의했는지 남아야 나중에 증명이 됩니다. */
var CONSENT_VERSION = '2026-08-31';

/* 접수 확인 메일. 끄려면 false. */
var MAIL_ON    = true;
var MAIL_FROM  = '함께하는 시민행동';
var MAIL_REPLY = 'action@action.or.kr';

/* 소식 받기에 동의한 사람을 스티비 주소록에 넣습니다.
   ⚠️ 아래 주소는 **홈페이지 뉴스레터 폼이 쓰는 것과 같은 주소록**입니다
      (index.html 의 스티비 폼에서 그대로 가져왔습니다). 랜딩은 다른 주소록을
      쓰고 있어 명단이 갈려 있습니다 — 통일하면 여기도 같이 고치세요.
   API 키가 필요 없습니다. 홈페이지 구독 폼이 보내는 그 자리로 보냅니다. */
var STIBEE_ON  = true;
var STIBEE_URL = 'https://stibee.com/api/v1.0/lists/EST3etdzzIoaxOorm4dT1dmlXqA=/public/subscribers';

/* 최근 서명한 사람을 화면에 흘릴지.
   이름을 가려도(김○○) 사람 이름이 화면에 뜨는 일이라 **꺼 두었습니다.**
   켜려면 true 로 바꾸고, 화면 쪽 sign.html 의 data-recent 도 "on" 으로 두세요. */
var RECENT_ON  = false;
var RECENT_MAX = 5;

var SHEET_NAME = '서명';
var HEADERS = ['접수시각', '캠페인', '이름', '이메일', '전화',
               '개인정보동의', '소식받기', '동의문판', '들어온 곳', '확인메일', '스티비'];

var LIMITS = { name: 60, email: 200, phone: 40, c: 60 };

/* 사람이 폼을 채우는 데 걸리는 최소 시간(밀리초).
   이보다 빨리 오면 자동 프로그램으로 봅니다. */
var MIN_FILL_MS = 2500;


/* ── 들어오는 문 ─────────────────────────────────────── */

function doPost(e) {
  try {
    var body = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    return out_(accept_(body), e);
  } catch (err) {
    return out_({ ok: false, error: '보내 주신 내용을 읽지 못했습니다.' }, e);
  }
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  var c = clip_(p.c || 'default', LIMITS.c);
  if (p.action === 'count')  return out_({ ok: true, count: count_(c) }, e);
  if (p.action === 'recent') return out_({ ok: true, recent: recent_(c) }, e);
  return out_({ ok: true, alive: true }, e);
}


/* ── 접수 ────────────────────────────────────────────── */

function accept_(b) {
  var c     = clip_(b.c || 'default', LIMITS.c);
  var name  = clip_(b.name, LIMITS.name);
  var email = clip_(b.email, LIMITS.email).toLowerCase();
  var phone = clip_(b.phone, LIMITS.phone);
  var news  = b.news ? 1 : 0;

  /* 사람이 아닌 것 거르기 — 조용히 성공한 척합니다.
     "막혔다"고 알려 주면 만든 쪽이 방법을 바꿉니다. */
  if (clip_(b.website, 100)) return { ok: true, count: count_(c) };
  if (typeof b.ms === 'number' && b.ms >= 0 && b.ms < MIN_FILL_MS) return { ok: true, count: count_(c) };

  if (name.length < 2)    return { ok: false, error: '이름을 적어 주세요.' };
  if (!looksMail_(email)) return { ok: false, error: '이메일 주소를 다시 봐 주세요.' };
  if (phone.length < 8)   return { ok: false, error: '전화번호를 적어 주세요.' };

  /* 두 사람이 같은 순간에 넣어도 줄이 엉키지 않게 잠급니다. */
  var lock = LockService.getScriptLock();
  try { lock.waitLock(15000); } catch (err) {
    return { ok: false, error: '지금 사람이 몰렸습니다. 잠시 뒤 다시 눌러 주세요.' };
  }

  var row;
  try {
    var sh = sheet_();
    if (has_(sh, c, email)) {
      /* 이미 한 서명입니다. 실패로 두면 "안 된다"고 또 누르게 됩니다. */
      return { ok: true, count: count_(c), again: true };
    }
    sh.appendRow([
      new Date(), c, name, email,
      "'" + phone,                 // 앞의 0 이 사라지지 않게 글자로 넣습니다
      '동의(' + CONSENT_VERSION + ')',
      news ? '받기' : '',
      CONSENT_VERSION,
      clip_(b.from, 300),
      '', ''                       // 확인메일 · 스티비 — 아래에서 채웁니다
    ]);
    row = sh.getLastRow();
    CacheService.getScriptCache().remove('n:' + c);
  } finally {
    lock.releaseLock();
  }

  /* 여기서부터는 실패해도 서명은 이미 됐습니다.
     그래서 통째로 감싸고, 결과만 시트에 적어 둡니다(나중에 눈으로 확인하려고). */
  var sh2 = sheet_();
  try { sh2.getRange(row, 10).setValue(mail_(name, email, c) ? '보냄' : '끔'); } catch (e1) {
    try { sh2.getRange(row, 10).setValue('실패: ' + e1); } catch (e2) {}
  }
  if (news) {
    try { sh2.getRange(row, 11).setValue(stibee_(name, email)); } catch (e3) {
      try { sh2.getRange(row, 11).setValue('실패: ' + e3); } catch (e4) {}
    }
  }

  return { ok: true, count: count_(c) };
}


/* ── 접수 확인 메일 ──────────────────────────────────── */

function mail_(name, email, c) {
  if (!MAIL_ON) return false;
  var subject = '[함께하는 시민행동] 서명이 접수되었습니다';
  var body =
    name + ' 님, 서명해 주셔서 고맙습니다.\n\n' +
    '서명이 잘 접수되었습니다. 모인 서명은 요구안과 함께 전달하고,\n' +
    '전달한 날과 그 결과를 이 주소로 알려 드리겠습니다.\n\n' +
    '한 사람이 더 함께하면 그만큼 무게가 실립니다.\n' +
    '주변에 알려 주세요.\n\n' +
    '― 함께하는 시민행동\n' +
    'action@action.or.kr / 02-921-4709\n\n' +
    '이 메일은 서명 접수를 알리려고 한 번만 보냅니다.\n' +
    '문의는 이 메일에 그대로 답장하시면 됩니다.';
  MailApp.sendEmail({
    to: email, subject: subject, body: body,
    name: MAIL_FROM, replyTo: MAIL_REPLY
  });
  return true;
}


/* ── 스티비 주소록 ──────────────────────────────────── */

/* 홈페이지 구독 폼이 보내는 그 자리로 보냅니다. API 키가 필요 없습니다.
   ⚠️ 소식 받기에 **동의한 사람만** 넣습니다. 동의 없이 넣으면 안 됩니다. */
function stibee_(name, email) {
  if (!STIBEE_ON || !STIBEE_URL) return '끔';
  var res = UrlFetchApp.fetch(STIBEE_URL, {
    method: 'post',
    payload: { email: email, name: name },
    muteHttpExceptions: true
  });
  var code = res.getResponseCode();
  return (code >= 200 && code < 400) ? '넣음' : ('안 됨(' + code + ')');
}


/* ── 시트 ────────────────────────────────────────────── */

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(HEADERS);
    sh.setFrozenRows(1);
    sh.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
  }
  return sh;
}

/* 같은 캠페인에 같은 이메일이 이미 있는지 */
function has_(sh, c, email) {
  var last = sh.getLastRow();
  if (last < 2) return false;
  var rows = sh.getRange(2, 2, last - 1, 3).getValues();   // 캠페인 · 이름 · 이메일
  for (var i = 0; i < rows.length; i++) {
    if (String(rows[i][0]) === c && String(rows[i][2]).toLowerCase() === email) return true;
  }
  return false;
}

/* 캠페인별 서명 수. 30초 동안은 셈한 값을 그대로 씁니다
   (사람이 올 때마다 시트를 다 읽으면 느립니다). */
function count_(c) {
  var cache = CacheService.getScriptCache();
  var key = 'n:' + c;
  var hit = cache.get(key);
  if (hit !== null) return parseInt(hit, 10);

  var sh = sheet_();
  var last = sh.getLastRow();
  var n = 0;
  if (last >= 2) {
    var col = sh.getRange(2, 2, last - 1, 1).getValues();
    for (var i = 0; i < col.length; i++) if (String(col[i][0]) === c) n++;
  }
  cache.put(key, String(n), 30);
  return n;
}

/* 최근 서명 — 가린 이름과 며칠 전인지만 돌려줍니다.
   이메일·전화는 절대 나가지 않습니다. */
function recent_(c) {
  if (!RECENT_ON) return [];
  var sh = sheet_();
  var last = sh.getLastRow();
  if (last < 2) return [];
  var from = Math.max(2, last - 200);
  var rows = sh.getRange(from, 1, last - from + 1, 3).getValues();  // 시각 · 캠페인 · 이름
  var out = [];
  for (var i = rows.length - 1; i >= 0 && out.length < RECENT_MAX; i--) {
    if (String(rows[i][1]) !== c) continue;
    out.push({ name: mask_(String(rows[i][2])), ago: ago_(rows[i][0]) });
  }
  return out;
}

/* 김하늘 → 김○○ / 이름이 두 자면 김○ */
function mask_(s) {
  if (!s) return '';
  if (s.length <= 1) return s;
  var out = s.charAt(0), i;
  for (i = 1; i < s.length; i++) out += '○';
  return out;
}

function ago_(t) {
  var ms = new Date().getTime() - new Date(t).getTime();
  var m = Math.floor(ms / 60000);
  if (m < 1)  return '방금';
  if (m < 60) return m + '분 전';
  var h = Math.floor(m / 60);
  if (h < 24) return h + '시간 전';
  return Math.floor(h / 24) + '일 전';
}


/* ── 잔손 ────────────────────────────────────────────── */

function clip_(v, max) {
  return String(v === undefined || v === null ? '' : v).trim().slice(0, max);
}

function looksMail_(s) {
  var at = s.indexOf('@'), dot = s.lastIndexOf('.');
  return at > 0 && dot > at + 1 && dot < s.length - 1 && s.indexOf(' ') < 0;
}

/* 답을 돌려주는 곳.
   ?callback= 이 오면 옛 방식(JSONP)으로도 답합니다 — 브라우저가 막을 때를 위한 뒷문입니다. */
function out_(obj, e) {
  var body = JSON.stringify(obj);
  var cb = e && e.parameter && e.parameter.callback;
  if (cb && /^[A-Za-z_$][A-Za-z0-9_$]*$/.test(cb)) {
    return ContentService.createTextOutput(cb + '(' + body + ')')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(body)
    .setMimeType(ContentService.MimeType.JSON);
}
