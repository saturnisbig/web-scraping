#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2

def download(url, retries=0):
    print 'Downloading %s' % url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                print 'Retry downloading'
                return download(url, retries-1)
    return html


if __name__ == "__main__":
    #url = 'https://www.douban.com'
    #print download(url, retries=1)
    retry_url = 'http://httpstat.us/503'
    print download(retry_url, 3)
