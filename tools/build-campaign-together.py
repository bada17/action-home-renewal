# -*- coding: utf-8 -*-
"""함께하기(/77) 페이지 코드를 캠페이너스용 두 조각으로 나눕니다.

원본은 저장소의 ``issue.html`` 한 곳입니다. 원본을 고친 뒤 이 스크립트를 실행하면
아래 두 파일이 갱신됩니다.

    campaign-together-layout.html   첫 번째 코드 위젯: CSS + 화면 HTML
    campaign-together-scripts.html  두 번째 코드 위젯: 게시판 연결 + 탭 동작

두 코드 위젯 사이에는 캠페이너스 게시판 위젯을 넣지 않습니다. /81·/82 게시판은
두 번째 조각이 /rss에서 읽으며, 페이지에는 캠페인 카드로 표시됩니다.

사용법:
    python tools/build-campaign-together.py
    python tools/build-campaign-together.py --check
"""

import io
import os
import re
import sys


try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOURCE = os.path.join(ROOT, 'issue.html')
LAYOUT_OUT = os.path.join(ROOT, 'campaign-together-layout.html')
SCRIPTS_OUT = os.path.join(ROOT, 'campaign-together-scripts.html')

PAGE_BEGIN_RE = re.compile(r'^<!-- CAMPAIGNERS:PAGE-CODE START .*?-->\s*', re.S)
PAGE_END_RE = re.compile(r'\s*<!-- CAMPAIGNERS:PAGE-CODE END -->\s*$', re.S)
PAGE_NOTE_RE = re.compile(
    r'^<!-- 이 파일 전체를 해당 페이지의 코드 위젯 하나에 붙입니다\..*?-->\s*',
    re.S,
)


def read(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def write(path, value):
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(value)


def build_parts(source):
    body = PAGE_BEGIN_RE.sub('', source, count=1)
    body = PAGE_NOTE_RE.sub('', body, count=1)
    body = PAGE_END_RE.sub('', body, count=1).strip()

    # #iss 화면을 닫은 뒤 처음 나오는 script부터 두 번째 위젯으로 보냅니다.
    close_at = body.find('</div>')
    split_at = body.find('<script>', close_at)
    if close_at < 0 or split_at < 0:
        raise ValueError('issue.html에서 화면 끝 또는 script 시작을 찾지 못했습니다.')

    layout_body = body[:split_at].rstrip()
    scripts_body = body[split_at:].strip()

    if '<div id="iss"' not in layout_body or '</style>' not in layout_body:
        raise ValueError('첫 조각에 #iss 화면 또는 CSS가 없습니다.')
    if "fetch('/rss'" not in scripts_body or 'issuesDone' not in scripts_body:
        raise ValueError('두 번째 조각에 /81·/82 게시판 연결 코드가 없습니다.')

    layout = '''<!-- CAMPAIGNERS:CAMPAIGN-TOGETHER-LAYOUT START -->
<!-- /77 함께하기: 첫 번째 코드 위젯. 바로 다음에 scripts 조각을 둡니다. -->
<!-- 원본은 issue.html입니다. 이 생성 파일을 직접 고치지 마세요. -->
{body}
<!-- CAMPAIGNERS:CAMPAIGN-TOGETHER-LAYOUT END -->
'''.format(body=layout_body)

    scripts = '''<!-- CAMPAIGNERS:CAMPAIGN-TOGETHER-SCRIPTS START -->
<!-- /77 함께하기: 두 번째 코드 위젯. layout 조각 바로 다음에 둡니다. -->
<!-- /81·/82 기본 게시판 위젯을 이 사이에 넣지 않습니다. -->
<!-- 원본은 issue.html입니다. 이 생성 파일을 직접 고치지 마세요. -->
{body}
<!-- CAMPAIGNERS:CAMPAIGN-TOGETHER-SCRIPTS END -->
'''.format(body=scripts_body)

    return layout, scripts


def main():
    check = '--check' in sys.argv
    layout, scripts = build_parts(read(SOURCE))
    outputs = ((LAYOUT_OUT, layout), (SCRIPTS_OUT, scripts))
    changed = []

    for path, value in outputs:
        name = os.path.basename(path)
        current = read(path) if os.path.exists(path) else None
        if current == value:
            print('  = %-34s 그대로' % name)
            continue
        changed.append(name)
        if check:
            print('  ! %-34s 다시 생성 필요' % name)
        else:
            write(path, value)
            print('  * %-34s %6d 바이트' % (name, len(value.encode('utf-8'))))

    if check and changed:
        print('\n%s' % ' · '.join(changed))
        print('python tools/build-campaign-together.py 를 실행하세요.')
        return 1

    print('\n캠페이너스 /77 배치 순서:')
    print('  1. campaign-together-layout.html')
    print('  2. campaign-together-scripts.html')
    print('  두 조각 사이에 게시판 위젯을 넣지 않습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
