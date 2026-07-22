#!/usr/bin/env python3
import argparse
from pathlib import Path

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--html',required=True); ap.add_argument('--markdown',required=True); a=ap.parse_args()
    h=Path(a.html).read_text(encoding='utf-8'); m=Path(a.markdown).read_text(encoding='utf-8')
    checks={
      'HTML为中文页面':'lang="zh-CN"' in h,
      '左侧目录存在':'<aside>' in h and '<nav>' in h,
      '交互答题存在':'class="submit"' in h and 'input type="radio"' in h,
      '答案提交前隐藏':'id="analysis-wrap"' in h and '#analysis-wrap{display:none}' in h,
      '重构练习存在':'重构练习' in h,
      '重点高亮支持':'<mark>' in h or 'mark{' in h,
      'Markdown含核心结构':all(x in m for x in ['正确答案','题目设计分析','概念理解','练习题']),
    }
    failed=[k for k,v in checks.items() if not v]
    for k,v in checks.items(): print(('PASS' if v else 'FAIL')+' '+k)
    raise SystemExit(1 if failed else 0)
if __name__=='__main__': main()
