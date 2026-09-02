# -*- coding: utf-8 -*-
"""페이지 코드에서 공통 상단·하단을 빼고 붙여넣기 범위를 정리합니다.

왜 이렇게 하는가
----------------
2026-09-01 사용자 결정으로 상단과 하단을 모두 페이지 코드에서 분리했습니다.
캠페이너스에서는 공통 상단·하단 코드 위젯을 페이지 맨 아래의 반복 섹션에
각각 한 번만 두고, 각 페이지 코드 위젯에는 본문만 붙입니다. 공통 상단은
코드가 화면 맨 위로 고정하고, 빈자리만 실제 본문 앞으로 옮깁니다.

이 스크립트는 예전에 페이지마다 들어 있던 아래 블록을 제거합니다.

    <!-- PART:header --> ... <!-- /PART:header -->
    <!-- PART:footer --> ... <!-- /PART:footer -->

그리고 각 파일의 CAMPAIGNERS:PAGE-CODE START/END 표시를 다시 맞춥니다.

쓰는 법
-------
    python tools/build-parts.py            # 전부 다시 심기
    python tools/build-parts.py --check    # 안 고치고 어긋난 곳만 알려 주기
"""

import io
import os
import re
import sys

# 윈도우 콘솔은 기본이 cp949 라 한글·기호가 섞이면 print 에서 터집니다.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HEADER_PART = os.path.join(HERE, 'parts', 'header.html')
FOOTER_PART = os.path.join(HERE, 'parts', 'footer.html')
HBEGIN = '<!-- PART:header -->'
HEND = '<!-- /PART:header -->'
PBEGIN_RE = re.compile(r'<!-- CAMPAIGNERS:PAGE-CODE START .*?-->\s*')
PEND_RE = re.compile(r'\s*<!-- CAMPAIGNERS:PAGE-CODE END -->')
# 파일 맨 위 안내문. 다시 돌려도 쌓이지 않도록, 아래 두 머리말 중 하나로 시작하는
# 주석은 지우고 다시 답니다. 새 안내문을 만들면 이 정규식에도 머리말을 더하세요.
PNOTE_RE = re.compile(
    r'<!-- (?:이 파일 전체를 해당 페이지의 코드 위젯 하나에 붙입니다'
    r'|미리보기용 전체 파일입니다)\..*?-->\s*', re.S)
PNOTE = ('<!-- 이 파일 전체를 해당 페이지의 코드 위젯 하나에 붙입니다. '
         '공통 상단은 tools/parts/header.html, 공통 하단은 tools/parts/footer.html이 '
         '각각 따로 맡습니다. -->')
# 파일마다 다른 안내문. 2026-09-02 지자체 감시(/49)는 기본 게시판 위젯을 살리려고
# 앞 코드(activity-local-before-board.html)와 게시판을 따로 두기 때문에,
# 미리보기용 전체 파일을 그대로 붙이면 안 됩니다.
PNOTES = {
    'activity-local.html':
        '<!-- 미리보기용 전체 파일입니다. 캠페이너스 /49에는 이 파일 전체를 붙이지 말고 '
        'activity-local-before-board.html 다음에 기본 게시판 위젯을 배치합니다. -->',
}

# 2026-09-01 사용자 결정:
# 공통 상단·하단은 각 페이지 파일에 복사하지 않습니다. 아래 표시는 예전에
# 페이지마다 들어 있던 블록을 찾아 제거하기 위해서만 남깁니다.
FBEGIN = '<!-- PART:footer -->'
FEND = '<!-- /PART:footer -->'

PAGES = [
    'index.html',
    'activity-local.html',
    'activity-power.html',
    'activity-budget.html',
    'activity-civic.html',
    'dok-history.html',
    'issue.html',
    'pb.html',
    'library.html',
    'sign.html',
]


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def remove_legacy_part(text, begin, end, label):
    """예전에 페이지마다 복사해 둔 공통 블록 하나를 제거합니다."""
    if begin in text and end in text:
        pat = re.compile(re.escape(begin) + '.*?' + re.escape(end), re.S)
        return pat.sub('', text, count=1).rstrip() + '\n', label + '-removed'
    return text, 'unchanged'


def mark_page_code(text, name):
    """캠페이너스에서 파일별로 잘라 붙이는 범위를 파일 자체에 표시합니다."""
    text = PBEGIN_RE.sub('', text, count=1)
    text = PEND_RE.sub('', text, count=1)
    text = PNOTE_RE.sub('', text, count=1)
    begin = '<!-- CAMPAIGNERS:PAGE-CODE START file=%s -->' % name
    return '%s\n%s\n%s\n<!-- CAMPAIGNERS:PAGE-CODE END -->\n' % (
        begin, PNOTES.get(name, PNOTE), text.strip())


def main():
    check = '--check' in sys.argv
    for part in (HEADER_PART, FOOTER_PART):
        if not os.path.exists(part):
            print('원본이 없습니다: %s' % part)
            return 1

    changed, problems = [], []
    for name in PAGES:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            # pb.html 처럼 아직 안 만든 화면은 조용히 건너뜁니다.
            print('  - %-22s 없음 (건너뜀)' % name)
            continue

        old = read(path)
        new, how_h = remove_legacy_part(old, HBEGIN, HEND, 'header')
        new, how_f = remove_legacy_part(new, FBEGIN, FEND, 'footer')

        new = mark_page_code(new, name)

        if '<header id="ah-nav"' in new:
            problems.append('%s: 페이지 코드에 공통 헤더가 남아 있습니다' % name)
            continue
        if 'id="ah-foot"' in new:
            problems.append('%s: 페이지 코드에 공통 하단이 남아 있습니다' % name)
            continue

        if new == old:
            print('  = %-22s 그대로' % name)
            continue

        changed.append(name)
        how = how_h if how_h != 'unchanged' else how_f
        if how == 'unchanged':
            how = 'markers'
        if check:
            print('  ! %-22s 어긋남 (%s)' % (name, how))
        else:
            write(path, new)
            print('  * %-22s 상단·하단 분리 / 범위 표시 정리' % name)

    for p in problems:
        print('  ⚠ %s' % p)

    if check and changed:
        print('\n%d 개 화면이 원본과 다릅니다. python tools/build-parts.py 를 돌리세요.' % len(changed))
        return 1
    if problems:
        return 1
    print('\n캠페이너스에 따로 붙이는 공통 원본:')
    print('  공통 상단 tools/parts/header.html   (페이지 맨 아래 반복 섹션, 화면에서는 고정 상단)')
    print('  공통 하단 tools/parts/footer.html   (하단 반복 섹션의 코드 위젯에 한 번)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
