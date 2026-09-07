/* ═══════════════════════════════════════════════════════════════
   지금 무엇을 보고 있나 — 이 화면에 **같이 놓인 게시판**의 최신 글 둘을 올립니다.
   (2026-09-07 사용자 지시. build-activity.py 가 TEMPLATE 의 {nowboard} 에 끼웁니다.)

   ★ 왜 /rss 를 안 쓰나
     /rss 는 사이트 전체의 최근 글만 줍니다. /49 처럼 새 글이 뜸한 게시판은
     한 건도 안 걸려서, 코드에 적어 둔 씨앗(임시 제목 · 빈 링크)이 그대로 남았습니다.
     그래서 **화면에 실제로 그려진 게시판 DOM 을 직접 읽습니다.**

   ★ 화면에 놓이는 차례
       1) activity-*-before-board.html   ← 이 스크립트가 여기 들어 있습니다
       2) 캠페이너스 기본 게시판 위젯     ← 우리보다 **뒤에** 그려집니다
       3) activity-*-after-board.html
     그래서 바로 못 찾으면 MutationObserver 로 게시판이 생길 때까지 기다립니다.

   ★ 게시판 두 가지 꼴을 다 읽습니다
     - 글목록형(/49 · /51) : ul.li_body > a.list_text_title, 날짜는 li.time
     - 카드형(/27)         : .list-style-card > a.post_link_wrap,
                             제목은 .title-block, 날짜는 small.date,
                             사진은 .card-thumbnail-wrap 의 background-image
     둘 다 아니면 bmode=view 링크만 보고 최선을 다합니다.

   ★ 대표 사진이 목록에 없으면 글 주소를 같은 출처로 받아 og:image(없으면 본문 첫 사진)
     를 씁니다. 그래도 없으면 **빈 액자**로 둡니다 — 깨진 사진을 두지 않습니다.
     글자 무늬(data-mark)는 사람이 씨앗 제목에 맞춰 고른 말이라 여기서 쓰지 않습니다.

   ⚠ /rss 는 게시판 DOM 을 끝내 못 읽었을 때만 쓰는 **보조**입니다.
     게시판을 읽었으면 언제나 게시판이 이깁니다 — 그게 최신입니다.
   ⚠ 아무 데서도 못 얻으면 손대지 않습니다. HTML 씨앗이 그대로 남습니다.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  var box = document.getElementById('act');
  var list = document.getElementById('act-now');
  if (!box || !list) return;

  var board = String(box.getAttribute('data-board') || '').replace(/\/+$/, '');
  if (!board) return;

  var WAIT_MS = 12000;   // 게시판이 그려지기를 기다리는 시간
  var done = false;

  /* ───────── 잔손 ───────── */
  function esc(v) {
    var d = document.createElement('div');
    d.textContent = (v === null || v === undefined) ? '' : String(v);
    return d.innerHTML;
  }
  function txt(el) {
    return el ? String(el.textContent || '').replace(/\s+/g, ' ').trim() : '';
  }
  function abs(u) {
    try { return new URL(u, window.location.href).href; } catch (e) { return ''; }
  }
  function pathOf(u) {
    try { return new URL(u, window.location.href).pathname.replace(/\/+$/, ''); }
    catch (e) { return ''; }
  }
  function idxOf(u) {
    var m = String(u || '').match(/[?&]idx=([0-9]+)/);
    return m ? m[1] : '';
  }
  /* 2023-12-01 11:12 · 2023.12.01 · RSS 날짜 → 2023.12.01 */
  function ymd(raw) {
    var s = String(raw || '').trim();
    var m = s.match(/(\d{4})[-.\/]\s*(\d{1,2})[-.\/]\s*(\d{1,2})/);
    function p(n) { return (n < 10 ? '0' : '') + n; }
    if (m) return m[1] + '.' + p(+m[2]) + '.' + p(+m[3]);
    var t = Date.parse(s);
    if (isNaN(t)) return '';
    var d = new Date(t);
    return d.getFullYear() + '.' + p(d.getMonth() + 1) + '.' + p(d.getDate());
  }
  /* style 의 background-image:url(...) 에서 주소만 빼냅니다. */
  function bgUrl(el) {
    if (!el) return '';
    var s = '';
    try { s = el.style && el.style.backgroundImage ? el.style.backgroundImage : ''; }
    catch (e) { s = ''; }
    if (!s) s = String((el.getAttribute && el.getAttribute('style')) || '');
    var m = s.match(/url\((['"]?)([^'")]+)\1\)/i);
    if (!m) return '';
    var u = m[2].trim();
    if (!u || /^data:/i.test(u)) return '';
    return abs(u);
  }
  function imgUrl(el) {
    if (!el) return '';
    var u = el.getAttribute('src') || el.getAttribute('data-src') || '';
    u = String(u).trim();
    if (!u || /^data:/i.test(u)) return '';
    /* 아이콘 · 빈 그림은 거릅니다. */
    if (/\/(icon|blank|noimage|no_image|spacer)/i.test(u)) return '';
    return abs(u);
  }

  /* ───────── 게시판 DOM 읽기 ─────────
     글 하나로 볼 만한 덩이를 모읍니다. 겹치면 바깥쪽만 남깁니다. */
  var ROW_SEL = [
    'ul.li_body',                 // 글목록형 한 줄
    '.list-style-card',           // 카드형 한 칸
    '._card_wrap',
    '._post_item_wrap',
    '.ma-item'
  ].join(',');

  function boardRows() {
    var rows = [];
    var cand = document.querySelectorAll(ROW_SEL);
    Array.prototype.forEach.call(cand, function (el) {
      if (box.contains(el)) return;                    // 우리 칸 안은 게시판이 아닙니다
      if (!el.querySelector('a[href*="bmode=view"]')) return;
      for (var i = 0; i < rows.length; i++) {
        if (rows[i].contains(el)) return;              // 이미 담은 것의 안쪽이면 버립니다
      }
      rows.push(el);
    });
    return rows;
  }

  function readRow(el) {
    /* 글 주소 — 카테고리 링크가 아니라 bmode=view 인 것만 */
    var a = null;
    var links = el.querySelectorAll('a[href*="bmode=view"]');
    for (var i = 0; i < links.length; i++) {
      if (idxOf(links[i].getAttribute('href') || links[i].href)) { a = links[i]; break; }
    }
    if (!a) a = links[0];
    if (!a) return null;
    var href = abs(a.getAttribute('href') || a.href || '');
    if (!href) return null;

    /* 제목 */
    var t = txt(el.querySelector('a.list_text_title span'))
         || txt(el.querySelector('a.list_text_title'));
    if (!t) {
      var tb = el.querySelector('.title-block, .card-body .title, .title');
      if (tb) {
        var c = tb.cloneNode(true);
        /* 카테고리 · 공지 딱지는 제목이 아닙니다 */
        Array.prototype.forEach.call(c.querySelectorAll('em, span, i, small'), function (n) {
          n.parentNode.removeChild(n);
        });
        t = txt(c) || txt(tb);
      }
    }
    if (!t) t = txt(el.querySelector('li.tit')) || txt(a);
    if (!t) return null;

    /* 날짜 — title 속성(분까지)이 있으면 그것이 정확합니다 */
    var dEl = el.querySelector('li.time, small.date, .date, .time');
    var date = '';
    if (dEl) date = ymd(dEl.getAttribute('title') || '') || ymd(txt(dEl));

    /* 대표 사진 — 목록에 있는 것부터 */
    var img = bgUrl(el.querySelector('.card-thumbnail-wrap, ._img_wrap, .thumb, .card'));
    if (!img) {
      var imgs = el.querySelectorAll('img');
      for (var k = 0; k < imgs.length && !img; k++) img = imgUrl(imgs[k]);
    }
    if (!img) {
      var bgs = el.querySelectorAll('[style*="background-image"]');
      for (var j = 0; j < bgs.length && !img; j++) img = bgUrl(bgs[j]);
    }

    return { t: t, url: href, img: img, date: date, idx: idxOf(href) };
  }

  function pickFromBoard() {
    var all = [];
    var seen = {};
    boardRows().forEach(function (el) {
      var r = readRow(el);
      if (!r) return;
      var key = r.idx || r.url;
      if (seen[key]) return;
      seen[key] = 1;
      all.push(r);
    });
    if (!all.length) return [];
    /* 이 화면에 걸린 게시판 글만 — 다 다르면 거르지 않습니다.
       (게시판 위젯을 다른 페이지에 얹으면 글 주소가 그 페이지 주소로 나옵니다.) */
    var mine = all.filter(function (r) { return pathOf(r.url) === board; });
    return (mine.length ? mine : all).slice(0, 2);
  }

  /* ───────── 대표 사진을 글에서 찾아오기 ─────────
     목록에 사진이 없을 때만. 같은 출처라 fetch 가 됩니다. */
  function fillShot(row, li) {
    if (row.img || !li) return;
    fetch(row.url, { credentials: 'same-origin' })
      .then(function (res) { return res.ok ? res.text() : ''; })
      .then(function (html) {
        if (!html) return;
        var doc = new DOMParser().parseFromString(html, 'text/html');
        var og = doc.querySelector('meta[property="og:image"], meta[name="og:image"]');
        var u = og ? abs(String(og.getAttribute('content') || '').trim()) : '';
        if (!u) {
          var body = doc.querySelector('.post-body, ._post_content, .board_view, .content, article')
                  || doc.body;
          var imgs = body ? body.querySelectorAll('img') : [];
          for (var i = 0; i < imgs.length && !u; i++) u = imgUrl(imgs[i]);
        }
        if (!u) return;
        var shot = li.querySelector('.shot');
        if (!shot) return;
        var im = document.createElement('img');
        im.setAttribute('alt', '');
        im.setAttribute('loading', 'lazy');
        /* 못 받는 사진이면 빈 액자로 되돌립니다 — 깨진 사진을 두지 않습니다. */
        im.onerror = function () { if (im.parentNode) im.parentNode.removeChild(im); };
        im.src = u;
        shot.appendChild(im);
      })
      .catch(function () { /* 못 받으면 빈 액자 그대로 */ });
  }

  /* ───────── 그리기 ───────── */
  function draw(rows) {
    if (done || !rows || !rows.length) return false;
    done = true;
    var html = '';
    rows.forEach(function (r) {
      var shot = r.img
        ? '<span class="shot"><img src="' + esc(r.img) + '" alt="" loading="lazy"></span>'
        : '<span class="shot" aria-hidden="true"></span>';
      html += '<li><a href="' + esc(r.url) + '">' + shot
            +   '<span class="t">' + esc(r.t) + '</span>'
            +   '<span class="m">' + (r.date ? '<span>' + esc(r.date) + '</span>' : '') + '</span>'
            + '</a></li>';
    });
    list.innerHTML = html;
    var lis = list.getElementsByTagName('li');
    rows.forEach(function (r, i) { fillShot(r, lis[i]); });
    return true;
  }

  /* ───────── 보조: /rss ─────────
     게시판을 끝내 못 읽었을 때만 부릅니다. */
  function fromRss() {
    if (done) return;
    fetch('/rss', { credentials: 'same-origin' })
      .then(function (res) {
        if (!res.ok) throw new Error('RSS ' + res.status);
        return res.text();
      })
      .then(function (xmlText) {
        if (done) return;
        var xml = new DOMParser().parseFromString(xmlText, 'application/xml');
        if (xml.getElementsByTagName('parsererror').length) throw new Error('RSS XML');
        var rows = [];
        Array.prototype.forEach.call(xml.getElementsByTagName('item'), function (item) {
          if (rows.length >= 2) return;
          var link = item.getElementsByTagName('link')[0];
          var url = link ? String(link.textContent || '').trim() : '';
          if (pathOf(url) !== board) return;
          var media = item.getElementsByTagName('media:content')[0];
          var ti = item.getElementsByTagName('title')[0];
          var pd = item.getElementsByTagName('pubDate')[0];
          rows.push({
            t: ti ? String(ti.textContent || '').trim() : '',
            url: url,
            img: media ? (media.getAttribute('url') || '') : '',
            date: ymd(pd ? pd.textContent : '')
          });
        });
        draw(rows);
      })
      .catch(function () { /* 못 받으면 씨앗을 그대로 보여 줍니다. */ });
  }

  /* ───────── 게시판이 생기기를 기다립니다 ───────── */
  function tryNow() { return draw(pickFromBoard()); }

  if (tryNow()) return;

  var obs = null;
  function stop() { if (obs) { obs.disconnect(); obs = null; } }

  if (window.MutationObserver && document.body) {
    obs = new MutationObserver(function () { if (tryNow()) stop(); });
    obs.observe(document.body, { childList: true, subtree: true });
  }
  /* 창이 다 뜬 뒤 한 번 더 — 위젯이 한 번에 그려져 관찰을 놓칠 수 있습니다. */
  window.addEventListener('load', function () { if (tryNow()) stop(); });

  window.setTimeout(function () {
    stop();
    if (!tryNow()) fromRss();
  }, WAIT_MS);
})();
