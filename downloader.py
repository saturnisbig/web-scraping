#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random
import urllib2
import urlparse
import datetime, time
import os
import pickle


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
        print 'Dowloading ', url
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
        self.cache_dir = cache_dir

    def url_to_path(self, url):
        component = urlparse.urlparse(url)
        path = component.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
                path += 'index.html'
        filename = component.netloc + path
        # 文件名规则正则需改进
        filename = re.sub(r'[^/0-9a-zA-Z.,;_\-]', '_', filename)
        filename = '/'.join(segment[:255] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, url):
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fd:
                return pickle.load(fd)
        else:
            raise KeyError(url + ' not cached yet.')

    def __setitem__(self, url, value):
        path = self.url_to_path(url)
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        with open(path, 'wb') as fd:
            fd.write(pickle.dumps(value))


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
            time2sleep = self.delays - (datetime.datetime.now() - last_accessed).seconds
            if time2sleep > 0:
                time.sleep(time2sleep)
        self.domains[component.netloc] = datetime.datetime.now()


if __name__ == "__main__":
    url = "http://www.baidu.com"
    D = Downloader(url)
    print D(url)
