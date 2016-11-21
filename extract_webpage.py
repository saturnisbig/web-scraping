import re
from bs4 import BeautifulSoup
import lxml.html

from download import download

TAGS = ('national_flag', 'area', 'population', 'iso', 'country', 'capital', 
'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format',
'postal_code_regex', 'languages', 'neighbours')

def re_scraper(html):
    result = {}
    id = 'places_%s__row'
    for tag in TAGS:
        id_tag = id % tag
        pat = r'<tr id="%s">.*?<td class="w2p_fw">(.*?)</td>' % (id_tag)
        result[tag] = re.search(pat, html).groups()[0]
    return result


def soup_scraper(html):
    result = {}
    soup = BeautifulSoup(html, 'html.parser')
    for t in TAGS:
        result[t] = soup.find('table').find('tr', id='places_%s__row' % t).find('td', class_='w2p_fw').text
    return result



def lxml_scraper(html):
    result = {}
    tree = lxml.html.fromstring(html)
    for t in TAGS:
        result[t] = tree.cssselect('table > tr#places_%s__row > td.w2p_fw' % t)[0].text_content()
    return result

if __name__ == "__main__":
    import time

    NUM_ITERATIONS = 1000
    html = download('http://example.webscraping.com/places/view/United-Kingdom-239')

    for name, scraper in [('Regular expressions', re_scraper), ('BeautifulSoup', soup_scraper),
                          ('Lxml', lxml_scraper)]:
        start = time.time()
        for i in range(NUM_ITERATIONS):
            if scraper == re_scraper:
                re.purge()
            result = scraper(html)
            assert(result['area'] == '244,820 square kilometres')
        end = time.time()
        print '%s: %.2f seconds' % (name, end - start)

