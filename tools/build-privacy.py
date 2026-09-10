# -*- coding: utf-8 -*-
u"""개인정보처리방침 정본(md)을 각 사이트의 화면(html)으로 굽습니다.

    python tools/build-privacy.py            둘 다
    python tools/build-privacy.py dok        밑빠진 독상만
    python tools/build-privacy.py pb         시민참여 상담소만

읽는 것 : PRIVACY-dok.md · PRIVACY-pb.md      (이 저장소. 정본입니다)
          tools/parts/privacy-dok.html        (껍데기. 빈 자리 {{BODY}} 하나)
          tools/parts/privacy-pb.html
쓰는 것 : ../dokseong/public/privacy.html
          ../participatory-budget/privacy.html

★ 왜 스크립트인가
  방침 글 한 벌이 화면 둘로 갑니다. 손으로 옮기면 한쪽만 고친 채 잊습니다
  (실제로 2026-09-07 에 정본을 새로 썼는데 독상 화면은 옛 글로 남아 있었습니다).
  글은 md 에서만 고치고, 화면은 여기서 굽습니다.

★ 건드리지 않는 것
  겉모습. 색·글꼴·칸은 전부 껍데기 파일에 있습니다.
  ⚠️ 굽는 결과물(privacy.html)을 손으로 고치지 마세요 — 다음에 구울 때 사라집니다.

★ 상담소는 한 걸음이 더 있습니다
  구운 privacy.html 을 배포 저장소(pb-action-site/)로 복사해 push 해야
  사는 화면이 바뀝니다. HANDOFF_PB_2026-09-08.md 2장과 같은 순서입니다.

옮기는 문법은 마크다운 전부가 아니라 방침 글이 쓰는 것만입니다 —
제목(#, ##, ###) · 글줄 · 목록(-) · 표(|) · **굵게** · [글](주소) · 가로줄(---).
정본에 다른 문법을 새로 쓰면 여기에도 손을 대야 합니다(안 그러면 그대로 나옵니다).
"""
import io
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SIBLING = os.path.dirname(REPO)          # 저장소들이 나란히 있는 폴더

TARGETS = {
    'dok': {
        'name': u'밑빠진 독상',
        'src': os.path.join(REPO, 'PRIVACY-dok.md'),
        'tpl': os.path.join(HERE, 'parts', 'privacy-dok.html'),
        'out': os.environ.get('DOK_PRIVACY_OUT',
                              os.path.join(SIBLING, 'dokseong', 'public', 'privacy.html')),
        'cls': 'dok',
    },
    'pb': {
        'name': u'시민참여 상담소',
        'src': os.path.join(REPO, 'PRIVACY-pb.md'),
        'tpl': os.path.join(HERE, 'parts', 'privacy-pb.html'),
        'out': os.environ.get('PB_PRIVACY_OUT',
                              os.path.join(SIBLING, 'participatory-budget', 'privacy.html')),
        'cls': 'pbp',
    },
}

# 주소를 스스로 걸어 주는 것 셋. 표 안에 맨 글자로 적혀 있어서 눌러지지 않습니다.
MAIL = r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+'
SITE = r'(?:www\.)?[a-z][a-z0-9-]*(?:\.[a-z0-9-]+)*\.(?:kr|com|org|net)'
TEL = r'0\d{1,2}-\d{3,4}-\d{4}'
AUTO = re.compile(r'(%s)|(%s)|(%s)' % (MAIL, TEL, SITE))


def esc(s):
    return s.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')


def inline(s):
    u"""한 줄 안의 꾸밈을 옮깁니다. [글](주소) → 자리표 → 자동 링크 → 굵게 순서입니다.

    순서를 지키는 까닭 — 자동 링크가 먼저 돌면 이미 만든 <a> 의 주소 안까지
    또 링크를 겁니다.
    """
    keep = []

    def stash(html):
        keep.append(html)
        return u'\x00%d\x00' % (len(keep) - 1)

    s = esc(s)

    def md_link(m):
        return stash(u'<a href="%s">%s</a>' % (m.group(2), m.group(1)))

    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', md_link, s)

    def auto(m):
        mail, tel, site = m.group(1), m.group(2), m.group(3)
        if mail:
            return stash(u'<a href="mailto:%s">%s</a>' % (mail, mail))
        if tel:
            return stash(u'<a href="tel:%s">%s</a>' % (tel, tel))
        return stash(u'<a href="https://%s" target="_blank" rel="noopener">%s</a>'
                     % (site, site))

    s = AUTO.sub(auto, s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)

    for i, html in enumerate(keep):
        s = s.replace(u'\x00%d\x00' % i, html)
    return s


def body_of(md):
    u"""머리말(정본이라는 안내)을 떼고 방침 글만 돌려줍니다.

    머리말은 파일 맨 위 인용글이고, 그 끝은 홀로 선 `---` 줄입니다.
    본문에도 `---` 이 한 번 더 나오므로 **첫 번째 것에서만** 자릅니다.
    """
    parts = re.split(r'(?m)^---\s*$', md, maxsplit=1)
    if len(parts) != 2:
        raise SystemExit(u'  ! 머리말 끝의 --- 줄을 못 찾았습니다')
    return parts[1].strip('\n')


def render(md, cls):
    u"""방침 글(md)을 화면 조각(html)으로 옮깁니다. 목차는 ## 제목으로 만듭니다."""
    lines = body_of(md).split('\n')
    out = []
    toc = []
    i = 0
    n = 0                     # ## 몇 번째인가 (id=p1, p2 …)
    seen_h1 = False
    toc_at = None             # 목차를 끼울 자리

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        # 표 — | 로 시작하는 줄이 이어지는 동안
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells)
                i += 1
            if len(rows) >= 2 and set(''.join(rows[1])) <= set('-: '):
                head, data = rows[0], rows[2:]
            else:
                head, data = None, rows
            out.append(u'<div class="%s-table-scroll">' % cls)
            out.append(u'<table>')
            if head:
                out.append(u'<thead><tr>%s</tr></thead>'
                           % u''.join(u'<th>%s</th>' % inline(c) for c in head))
            out.append(u'<tbody>')
            for r in data:
                out.append(u'<tr>%s</tr>'
                           % u''.join(u'<td>%s</td>' % inline(c) for c in r))
            out.append(u'</tbody></table></div>')
            continue

        # 목록 — - 로 시작하는 줄이 이어지는 동안
        if line.startswith('- '):
            out.append(u'<ul>')
            while i < len(lines) and lines[i].strip().startswith('- '):
                out.append(u'  <li>%s</li>' % inline(lines[i].strip()[2:].strip()))
                i += 1
            out.append(u'</ul>')
            continue

        if line.startswith('### '):
            out.append(u'<h3>%s</h3>' % inline(line[4:].strip()))
            i += 1
            continue

        if line.startswith('## '):
            n += 1
            if n == 1:
                toc_at = len(out)      # 목차는 첫 항 바로 앞에 놓습니다
            text = line[3:].strip()
            # 목차에는 번호를 빼고 적습니다(제목에는 남깁니다)
            short = re.sub(r'^\d+\.\s*', '', text)
            toc.append((n, short))
            out.append(u'<h2 id="p%d">%s</h2>' % (n, inline(text)))
            i += 1
            continue

        if line.startswith('# '):
            out.append(u'<h1>%s</h1>' % inline(line[2:].strip()))
            seen_h1 = True
            i += 1
            continue

        if line.strip() == '---':
            out.append(u'<hr>')
            i += 1
            continue

        # 그 밖에는 글줄. h1 바로 다음 한 줄은 발행 정보라 작게 씁니다.
        if seen_h1 and not any(x.startswith(u'<p') for x in out):
            out.append(u'<p class="%s-meta">%s</p>' % (cls, inline(line.strip())))
        else:
            out.append(u'<p>%s</p>' % inline(line.strip()))
        i += 1

    nav = [u'<nav class="%s-toc">' % cls, u'  <ol>']
    for num, text in toc:
        nav.append(u'    <li><a href="#p%d">%s</a></li>' % (num, esc(text)))
    nav.append(u'  </ol>')
    nav.append(u'</nav>')

    if toc_at is None:
        toc_at = len(out)
    out[toc_at:toc_at] = nav
    return u'\n'.join(out) + u'\n'


def bake(key):
    t = TARGETS[key]
    print(u'%s' % t['name'])
    md = io.open(t['src'], encoding='utf-8').read()
    tpl = io.open(t['tpl'], encoding='utf-8').read()
    if u'{{BODY}}' not in tpl:
        print(u'  ! 껍데기에 {{BODY}} 가 없습니다: %s' % t['tpl'])
        return 1
    html = render(md, t['cls'])
    out = tpl.replace(u'{{BODY}}', html.strip())

    # 굽고 나서 한 번 봅니다 — 옮기지 못한 표시가 남아 있으면 화면에 그대로 나옵니다.
    live = re.sub(r'<!--.*?-->', '', out, flags=re.S)
    left = re.findall(r'(?m)^\s*(?:#{1,6} |\| |- )', live)
    if left:
        print(u'  ! 옮기지 못한 마크다운이 남았습니다(%d 곳). 문법이 새로 늘었는지 보세요.'
              % len(left))
        return 1
    if u'**' in live:
        print(u'  ! **굵게** 표시가 남았습니다. 별표 짝이 안 맞는 곳이 있습니다.')
        return 1

    outdir = os.path.dirname(t['out'])
    if not os.path.isdir(outdir):
        print(u'  ! 나갈 곳이 없습니다: %s' % outdir)
        return 1
    io.open(t['out'], 'w', encoding='utf-8', newline='\n').write(out)
    print(u'  읽음   %s' % t['src'])
    print(u'  씀     %s  (%d 바이트)' % (t['out'], len(out.encode('utf-8'))))
    return 0


def main():
    keys = sys.argv[1:] or ['dok', 'pb']
    bad = [k for k in keys if k not in TARGETS]
    if bad:
        print(u'모르는 이름: %s  (쓸 수 있는 것: dok, pb)' % ', '.join(bad))
        return 2
    rc = 0
    for k in keys:
        rc |= bake(k)
    if not rc and 'pb' in keys:
        print(u'\n※ 상담소는 구운 privacy.html 을 pb-action-site/ 로 복사해 push 해야')
        print(u'   사는 화면이 바뀝니다.')
    return rc


if __name__ == '__main__':
    sys.exit(main())
