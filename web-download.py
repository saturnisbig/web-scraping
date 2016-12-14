#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import urlparse
import robotparser

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


def link_crawler(seed_url, link_regex, user_agent='wswp', max_depth=-1):
    """
    从某个页面开始，遍历页面中找到的符合需求的页面
    """
    link_queue = [seed_url]
    link_seen = set(link_queue)
    rp = get_robotparser()
    while link_queue:
        url = link_queue.pop()
        if rp.can_fetch(user_agent, url):
            html = download(url)
            for link in get_links(html):
                if re.match(link_regex, link):
                    link = urlparse.urljoin(seed_url, link)
                    if link not in link_seen:
                        link_seen.add(link)
                        link_queue.append(link)
        else:
            print 'Blocked by robot.txt', url


def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

def get_robotparser():
    return robotparser.RobotFileParser()

def sitemap_crawler(sitemap_url):
    html = download(sitemap_url)
    links = re.findall(r'<loc>(.*?)</loc>', html)
    return links

def id_crawler(base_url, max_errors=5):
    import itertools
    #for i in itertools.count(1):
    number_errors = 0
    for i in itertools.count(250): # test max_depth
        link = '%s/%d' % (base_url, i)
        html = download(link)
        if not html:
            number_errors += 1
            if max_errors == number_errors:
                # return NOT FOUND error
                print 'Maybe all webpage crawled...'
                break
            else:
                number_errors = 0
        #links.append(link)
    #return links



if __name__ == "__main__":
    ## link crawler 
    url = 'http://example.webscraping.com'
    link_crawler(url, '/(index|view)/')
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
    #url = 'http://example.webscraping.com/view'
    #id_crawler(url, max_depth=3)
