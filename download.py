import urllib2
import re

def download(url, user_agent='wswp', num_retries=2):
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Downloading error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                return download(url, user_agent, num_retries-1)
    return html


def crawl_sitemap(url):
    sitemap = download(url)
    links = re.findall(r'<loc>(.*?)</loc>', sitemap)
    for link in links:
        html = download(link)

################
# Link Crawler
################
import urlparse
def link_crawler(seed_url, link_regex):
    crawl_queue = [seed_url]
    seen = set(crawl_queue)
    while crawl_queue:
        url = crawl_queue.pop()
        html = download(url)
        for link in get_links(html):
            if re.match(link_regex, link):
                link = urlparse.urljoin(seed_url, link)
                if link not in seen:
                    seen.add(link)
                    crawl_queue.append(link)

def get_links(html):
    webpage_regex = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


if __name__ == "__main__":
    #url = 'http://httpstat.us/500'
    #url = 'http://www.meetup.com'
    #print(download(url))
    #sitemap_url = 'http://example.webscraping.com/sitemap.xml'
    #crawl_sitemap(sitemap_url)
    seed_url = 'http://example.webscraping.com'
    link_crawler(seed_url, '/(index|view)/')

