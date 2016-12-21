#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import re
import urlparse
import robotparser
import datetime
import time

def download(url, headers, proxy, num_retries):
    print 'Downloading %s' % url
    request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()
    #request = urllib2.Request(url)
    # 添加代理
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        resp = opener.open(request)
        html = resp.read()
        code = resp.code
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code < 600:
                print 'Retry downloading'
                return download(url, headers, proxy, num_retries-1)
        else:
            code = None
    return html


def link_crawler(seed_url, link_regex=None, delay=5, headers=None, user_agent='wswp', proxy=None, num_retries=1, max_depth=-1):
    """
    从某个页面开始，遍历页面中找到的符合需求的页面
    """
    link_queue = [seed_url]
    link_seen = {}
    headers = headers or {}
    rp = get_robotparser(seed_url)
    throttle = Throttle(delay)
    while link_queue:
        url = link_queue.pop()
        throttle.wait(url)
        if rp.can_fetch(user_agent, url):
            html = download(url, headers, proxy, num_retries)
            depth = link_seen.get(url, 0)
            if depth != max_depth:
                for link in get_links(html):
                    if re.match(link_regex, link):
                        link = urlparse.urljoin(seed_url, link)
                        if link not in link_seen:
                            link_seen[link] = depth + 1
                            link_queue.append(link)
        else:
            print 'Blocked by robots.txt', url
        print link_seen


def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

def get_robotparser(url):
    """
    初始化某个域名的robots文件
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, 'robots.txt'))
    rp.read()
    return rp

class Throttle:
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        # update the last accessed time
        self.domains[domain] = datetime.datetime.now()

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
