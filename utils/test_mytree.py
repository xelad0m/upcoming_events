"""
Сравнение скорости парсинга HTML
# (pypy3) mytree to parse https://www.youtube.com/ etree 10 times takes 0.532 seconds (0.053 sec. in average)
# lxml etree (SAX) is the fastest, but due to profiler it do nothing (4-5 calls)"""


from . import mytree.TreeBuilder as tb
from bs4 import BeautifulSoup as bs
from lxml import etree as et



import html5lib

import requests
import time

from pympler import asizeof

N = 10
URLs = ['https://www.youtube.com/', 
        'https://wikipedia.org/',
        'https://9gag.com/']


def _bs(data):
    return bs(data, 'lxml')

parsers = {'bs4+lxml (DOM)': _bs, 'lxml etree (SAX)': et.HTML, 'html5lib (SAX?)': html5lib.parse, 'mytree (DOM)': tb}

def evaluate(report):
    for url in URLs:
        headers = {'Accept-Encoding': 'identity'}                   # to recieve not compressed html
        try:
            r = requests.get(url=url, headers=headers)
        except:
            print(url, ' - connection problems...')
        if r.status_code == 200:
            for name, parser in parsers.items():
                t = time.perf_counter()
                for i in range(N):
                    etree = parser(r.text)
                m = asizeof.asizeof(etree)
                ts = time.perf_counter()
                report.append({'url': url, 'name': name, 'total': ts - t, 'average': (ts - t) / N, 'memory': m / 1024})
        else:
            for name, parser in parsers.items():
                report.append({'url': url, 'name': name, 'total': 'n/a', 'average': 'n/a', 'memory': 'n/a'})    
        
    return report

def report(report):
    print('Number of parse loops per page: ', N)
    print("No   Parser                   Total time (s)    Avg time (s)     Memory for tree (Kb)")
    print('-'*80)   
    report_template = "{}   {:<20}      {:>10.3f}     {:>10.3f}     {:>10.1f}"
    # total sum
    for parser_name, parser in parsers.items():
        rep_slice = [x for x in report if x['name'] == parser_name]
        report.append({'url': 'Total', 'name': parser_name, 
                       'total': sum([x['total'] for x in rep_slice]), 
                       'average': sum([x['average'] for x in rep_slice]),                                                                          
                       'memory': sum([x['memory'] for x in rep_slice])                                                   
                       })
    # print cases
    for url in URLs:
        print(url)
        for pos, case in enumerate(sorted([x for x in report if x['url'] == url], 
                                          key=lambda x: x.get('total'))):
            print(report_template.format(pos+1, case['name'], case['total'], case['average'], case['memory']))
    # print total
    print('-'*80)
    print('Total:')
    for pos, case in enumerate(sorted([x for x in report if x['url'] == 'Total'], 
                                          key=lambda x: x.get('total'))):
            print(report_template.format(pos+1, case['name'], case['total'], case['average'], case['memory']))


if __name__ == '__main__':

    # Test code
    report(evaluate([]))

    # Profiling code
    
    # import cProfile, pstats, io
    # r = requests.get("https://www.youtube.com/").text
    # for name, parser in parsers.items():
    #     with cProfile.Profile() as pr:
    #         print(name)
    #         pr.enable()
    #         parser(r)
    #         pr.disable()
    #         s = io.StringIO()
    #         sortby = pstats.SortKey.CUMULATIVE  # CALLS PCALLS CUMULATIVE
    #         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    #         ps.print_stats(10)  # 10% списка
    #         print(s.getvalue())
