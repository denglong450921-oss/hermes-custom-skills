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
      '通用逻辑框架完整':all(x in h for x in ['id="framework"','槽位','适用边界','跨主题']),
      '错误选项类型完整':all(x in h for x in ['id="distractors"','识别信号','错误机制','反制动作','最小对比']),
      '两大核心模块视觉突出':h.count('class="core-module"') >= 2 and h.count('★ 高频迁移核心') >= 2,
      '主动提取交互存在':h.count('class="recall-reveal"') >= 4 and '想好后揭晓' in h,
      '穿透洞见形成分析主线':h.count('class="insight"') >= 5 and h.count('穿透洞见') >= 5 and m.count('穿透洞见') >= 5,
      '间隔复习计划存在':all(x in h for x in ['10 分钟','1 天','3 天','7 天']),
      'Markdown含核心结构':all(x in m for x in ['正确答案','题目设计分析','概念理解','十一、这类题目的通用逻辑框架','十二、错误选项的通用类型','练习题']),
    }
    failed=[k for k,v in checks.items() if not v]
    for k,v in checks.items(): print(('PASS' if v else 'FAIL')+' '+k)
    raise SystemExit(1 if failed else 0)
if __name__=='__main__': main()
