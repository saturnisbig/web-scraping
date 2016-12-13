#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re

def download(url, user_agent=None, retries=0):
    print 'Downloading %s' % url
    headers = {'User-Agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    #request = urllib2.Request(url)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                print 'Retry downloading'
                return download(url, retries-1)
    return html


def link_crawler(url_pattern, seed_url):
    """
    从某个页面开始，遍历页面中找到的符合需求的页面
    """
    pass

def sitemap_crawler(sitemap_url):
    html = download(sitemap_url)
    links = re.findall(r'<loc>(.*?)</loc>', html)
    return links

def id_crawler(base_url, max_depth=-1):
    import itertools
    #for i in itertools.count(1):
    for i in itertools.count(250): # test max_depth
        link = '%s/%d' % (base_url, i)
        html = download(link)
        if not html:
            if max_depth > 0:
                max_depth = max_depth - 1
            else:
                # return NOT FOUND error
                print 'Maybe all webpage crawled...'
                break
        #links.append(link)
    #return links



if __name__ == "__main__":
    ## Test first download
    #url = 'https://www.douban.com'
    #print download(url)
    ## download with retry
    #retry_url = 'http://httpstat.us/503'
    #print download(retry_url, 3)
    ## download with headers setted.
    #url = 'http://www.meetup.com'
    #print download(url, user_agent='wswp')
    ## sitemap crawler
    #url = 'http://example.webscraping.com/sitemap.xml'
    #print sitemap_crawler(url)
    ## id crawler
    url = 'http://example.webscraping.com/view'
    id_crawler(url, max_depth=3)
