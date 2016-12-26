#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random
import urllib2
import urlparse
import datetime, time

from web_download import Throttle

class Downloader:

    def __init__(self, delay=5, user_agent='wswp',
                 proxies=None, num_retries=0, cache=None, opener=None):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache
        self.opener = opener

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if self.num_retries > 0 and (500 < result['code'] < 600):
                    result = None
        if result is None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, proxy, self.num_retries, self.opener)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxy, num_retries, data=None):
        print 'Dowloading url: ', url
        request = urllib2.Request(url, headers=headers)
        opener = self.opener or urllib2.build_opener()
        if proxy:
            proxy_params = {urlparse.urlparse(url).scheme: proxy}
            self.opener.add_handler(urllib2.ProxyHandler(proxy_params))
        try:
            resp = opener.open(request)
            html = resp.read()
            code = resp.code
        except urllib2.URLError as e:
            print 'Download error: ', e.reason
            html = ''
            if hasattr(e, 'code'):
                if num_retries > 0 and 500 < e.code < 600:
                    # 服务器错误，重新下载
                    return self.download(url, headers, proxy, num_retries-1)
            else:
                code = None
        return {'html': html, 'code': code}


class DiskCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache

    def url_to_path(self, url):
        component = urlparse.urlparse(url)
        domain = component.netloc
        path = component.path
        if path:
            if path.ends_with('/'):
                path += 'index.html'
        else:
            path = '/index.html'
        filename = domain + path
        # 文件名规则正则需改进
        filename = re.sub(r'[^/0-9a-zA-Z;-]', '_', filename)
        filename = '/'.join(segment[:255] for segment in urlparse.urlsplit(filename))
        return filename

    def __getitem__(self, key):
        pass

    def __setitem__(self, key):
        pass


class Throttle:
    """
    如果正在抓取某个域名下的文件，则适当延迟，避免被封IP
    """
    def __init__(self, delays=5.0):
        self.delays = delays
        self.domains = {}

    def wait(self, url):
        """等待一段时间
        """
        component = urlparse.urlparse(url)
        last_accessed = self.domains.get(component.netloc)
        if last_accessed:
            time2sleep = self.delays - (datetime.datetime.now() - before).second
            if time2sleep > 0:
                time.sleep(time2sleep)
        self.domains[component.netloc] = datetime.datetime.now()


if __name__ == "__main__":
    url = "http://www.baidu.com"
    D = Downloader(url)
    print D(url)
