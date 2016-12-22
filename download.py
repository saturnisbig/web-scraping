import urllib2
import re
import datetime, time
import csv
import lxml.html

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


class Throttle:
    """Add a delay between downloads to the same domain
    """
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
        self.domains[domain] = datetime.datetime.now()

################
# Link Crawler
################
import urlparse
from collections import defaultdict
import Queue

def link_crawler(seed_url, link_regex, delay=5, max_depth=-1, max_urls=-1, num_retries=1, scrape_callback=None):
    crawl_queue = Queue.deque([seed_url])
    seen = defaultdict(int)
    num_urls = 0
    throttle = Throttle(delay)
    while crawl_queue:
        url = crawl_queue.pop()
        throttle.wait(url)
        html = download(url, num_retries=num_retries)
        links = []
        if scrape_callback:
            links.extend(scrape_callback(url, html) or [])

        depth = seen[url]
        if depth != max_depth:
            if link_regex:
                links.extend(link for link in get_links(html) if re.match(link_regex, link))

            for link in links:
                link = urlparse.urljoin(seed_url, link)
                if link not in seen:
                    seen[link] = depth + 1
                    crawl_queue.append(link)
        print crawl_queue
        num_urls += 1
        if num_urls == max_urls:
            break

def get_links(html):
    webpage_regex = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)


class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('national_flag', 'area', 'population', 'iso', 'country', 'capital',
                       'continent', 'tld', 'currency_code', 'currency_name', 'phone', 
                       'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        #print 'here', url
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            #print row
            self.writer.writerow(row)

if __name__ == "__main__":
    #url = 'http://httpstat.us/500'
    #url = 'http://www.meetup.com'
    #print(download(url))
    #sitemap_url = 'http://example.webscraping.com/sitemap.xml'
    #crawl_sitemap(sitemap_url)
    seed_url = 'http://example.webscraping.com'
    link_crawler(seed_url, '/(index|view)/', delay=1, max_depth=-1, scrape_callback=ScrapeCallback())
    #link_crawler(seed_url, '/(index|view)/', delay=0, max_depth=1, scrape_callback=ScrapeCallback())

