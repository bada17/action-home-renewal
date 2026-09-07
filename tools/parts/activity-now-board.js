/* ═══════════════════════════════════════════════════════════════
   지금 무엇을 보고 있나 — 이 화면이 앉은 게시판의 **최신 글 둘**을 올립니다.
   (2026-09-07 사용자 지시. build-activity.py 가 TEMPLATE 의 {nowboard} 에 끼웁니다.)

   게시판 번호는 #act 의 data-board 에 적혀 있습니다(활동마다 다릅니다).
   action.or.kr/rss 를 받아, 글 주소가 그 게시판인 것만 위에서부터 둘 씁니다.

   ★ 못 받거나 그 게시판 글이 아직 없으면 아무것도 하지 않습니다 —
     HTML 에 적힌 씨앗이 그대로 남습니다('켜는 것만 스크립트가 한다' 원칙).
   ⚠ AH_DATA 스크립트보다 뒤에 그립니다(받아오는 데 시간이 걸립니다).
     둘 다 값이 있으면 게시판 쪽이 이깁니다 — 그게 최신입니다.
   ⚠ 사진은 RSS 의 media:content 를 씁니다. 없으면 빈 액자로 둡니다 —
     글자 무늬(data-mark)는 사람이 고른 말이라 여기서 지어내지 않습니다.
   ═══════════════════════════════════════════════════════════════ */
(function () {
  var box = document.getElementById('act');
  var list = document.getElementById('act-now');
  if (!box || !list) return;

  var board = String(box.getAttribute('data-board') || '').replace(/\/+$/, '');
  if (!board) return;

  function esc(v) {
    var d = document.createElement('div');
    d.textContent = (v === null || v === undefined) ? '' : String(v);
    return d.innerHTML;
  }
  function nodeText(node, tag) {
    var el = node.getElementsByTagName(tag)[0];
    return el ? String(el.textContent || '').trim() : '';
  }
  function boardPath(link) {
    try { return new URL(link, window.location.href).pathname.replace(/\/+$/, ''); }
    catch (e) { return ''; }
  }
  function ymd(raw) {
    var t = Date.parse(raw);
    if (isNaN(t)) return '';
    var d = new Date(t);
    function p(n) { return (n < 10 ? '0' : '') + n; }
    return d.getFullYear() + '.' + p(d.getMonth() + 1) + '.' + p(d.getDate());
  }

  fetch('/rss', { credentials: 'same-origin' })
    .then(function (res) {
      if (!res.ok) throw new Error('RSS ' + res.status);
      return res.text();
    })
    .then(function (xmlText) {
      var xml = new DOMParser().parseFromString(xmlText, 'application/xml');
      if (xml.getElementsByTagName('parsererror').length) throw new Error('RSS XML');

      var rows = [];
      Array.prototype.forEach.call(xml.getElementsByTagName('item'), function (item) {
        if (rows.length >= 2) return;
        var url = nodeText(item, 'link');
        if (boardPath(url) !== board) return;
        var media = item.getElementsByTagName('media:content')[0];
        rows.push({
          t: nodeText(item, 'title'),
          url: url,
          img: media ? (media.getAttribute('url') || '') : '',
          date: ymd(nodeText(item, 'pubDate'))
        });
      });
      if (!rows.length) return;

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
    })
    .catch(function () { /* 못 받으면 씨앗을 그대로 보여 줍니다. */ });
})();
