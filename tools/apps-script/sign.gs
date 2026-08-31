/**
 * 서명 접수 — 구글 시트에 쌓기 (Google Apps Script)
 *
 * 이 파일은 이 저장소에서 돌아가지 않습니다. 구글 스프레드시트에 붙여 넣는 코드입니다.
 * 켜는 순서는 SIGN.md 에 있습니다. 여기서는 무엇을 하는 코드인지만 적습니다.
 *
 *   POST /exec   서명 접수  → 시트에 한 줄 적고 { ok:true, count:n } 을 돌려줍니다
 *   GET  /exec?action=count&c=<캠페인>   지금까지 몇 명인지  → { count:n }
 *
 * ⚠️ 이 시트에는 이름·이메일·전화번호가 쌓입니다. 개인정보입니다.
 *    · 시트를 '링크가 있는 모든 사용자'로 공유하지 마세요. 담당자만 여세요.
 *    · 내려받은 파일(엑셀·CSV)도 같은 개인정보입니다. 아무 폴더에나 두지 마세요.
 *    · 보유기간이 지나면 지워야 합니다. 기간은 단체가 정해 동의문에 적은 값입니다.
 *
 * ⚠️ 웹 앱을 다시 배포할 때 '새 버전'으로 배포하지 않으면 고친 것이 반영되지 않습니다.
 *    주소(/exec)는 그대로 유지됩니다.
 */

/* 동의문을 고칠 때마다 이 날짜를 올리세요.
   누가 어느 판의 동의문에 동의했는지 남아야 나중에 증명이 됩니다. */
var CONSENT_VERSION = '2026-08-31';

var SHEET_NAME = '서명';
var HEADERS = ['접수시각', '캠페인', '이름', '이메일', '전화', '개인정보동의', '소식받기', '동의문판', '들어온 곳'];

/* 같은 사람이 연타로 넣는 것을 막습니다. 한 캠페인에 같은 이메일은 한 번뿐입니다. */
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
  if (p.action === 'count') {
    return out_({ ok: true, count: count_(clip_(p.c || 'default', LIMITS.c)) }, e);
  }
  return out_({ ok: true, alive: true }, e);
}


/* ── 접수 ────────────────────────────────────────────── */

function accept_(b) {
  var c     = clip_(b.c || 'default', LIMITS.c);
  var name  = clip_(b.name, LIMITS.name);
  var email = clip_(b.email, LIMITS.email).toLowerCase();
  var phone = clip_(b.phone, LIMITS.phone);

  /* 사람이 아닌 것 거르기 — 조용히 성공한 척합니다.
     "막혔다"고 알려 주면 만든 쪽이 방법을 바꿉니다. */
  if (clip_(b.website, 100)) return { ok: true, count: count_(c) };
  if (typeof b.ms === 'number' && b.ms >= 0 && b.ms < MIN_FILL_MS) return { ok: true, count: count_(c) };

  if (name.length < 2)      return { ok: false, error: '이름을 적어 주세요.' };
  if (!looksMail_(email))   return { ok: false, error: '이메일 주소를 다시 봐 주세요.' };
  if (phone.length < 8)     return { ok: false, error: '전화번호를 적어 주세요.' };

  /* 두 사람이 같은 순간에 넣어도 줄이 엉키지 않게 잠급니다. */
  var lock = LockService.getScriptLock();
  try { lock.waitLock(15000); } catch (err) {
    return { ok: false, error: '지금 사람이 몰렸습니다. 잠시 뒤 다시 눌러 주세요.' };
  }

  try {
    var sh = sheet_();
    if (has_(sh, c, email)) {
      /* 이미 한 서명입니다. 실패로 두면 "안 된다"고 또 누르게 됩니다. */
      return { ok: true, count: count_(c), again: true };
    }
    sh.appendRow([
      new Date(),
      c,
      name,
      email,
      "'" + phone,                 // 앞의 0 이 사라지지 않게 글자로 넣습니다
      '동의(' + CONSENT_VERSION + ')',
      b.news ? '받기' : '',
      CONSENT_VERSION,
      clip_(b.from, 300)
    ]);
    CacheService.getScriptCache().remove('n:' + c);
    return { ok: true, count: count_(c) };
  } finally {
    lock.releaseLock();
  }
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
