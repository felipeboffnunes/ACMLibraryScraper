def process_page(url, path='', find_pages=False, page_size=50):
    import os
    import re
    import csv
    import math
    import time
    import requests
    from bs4 import BeautifulSoup
    from proxyscrape import create_collector, get_collector
    # Processes in multiprocessing have separate contexts
    # You can't use information from outside the method
    
    class Page():
        status_code = 0

    # Returns the number of pages in the full search
    def how_many_pages(url, http, http_collector, page_size):
        page = get_page(url, http, http_collector)
        content = BeautifulSoup(page.content, 'lxml')

        result_count = content.find('span', class_='result__count').text
        result_count = result_count.split(' ')[0].replace(',', '')
        
        pages = math.ceil(int(result_count)/page_size)
        return pages


    def make_collector(page_i=''):
        http_collector = create_collector(f'http-collector-{page_i}', 'https')
        return http_collector

    # Returns requests session with proxies (http, https)
    def setup_new_proxies(http_collector, http):    
        proxy_http = http_collector.get_proxy()
        proxy_https = http_collector.get_proxy({'type':'https'})
        http.proxies={
            'http': f'http://{proxy_http.host}:{proxy_http.port}',
            'https' : f'https://{proxy_https.host}:{proxy_https.port}'
        }
        return http

    def create_new_session(http_collector):
        http = requests.Session()
        http = setup_new_proxies(http_collector, http)
        return http

    # Returns index of page from url    
    def get_page_i(url):
        if 'startPage' in url:
            page_i = next(re.finditer(r'\d+$', url)).group(0)
            page_i = int(page_i) + 1
        else:    
            page_i = 1

        if page_i < 10:
            page_i = '0' + str(page_i)
        return page_i

    # Returns page from url
    def get_page(url, http, http_collector):
        page = Page()
        start = time.time()
        while True:
            try:
                page = http.get(url, timeout=6)
                if page.status_code == 200:
                    break
            except BaseException as error:
                pass
            finally:
                print('CHANGE PROXY PAGE: ', page.status_code, http.proxies['https'])
                if page.status_code != 200:
                    http = setup_new_proxies(http_collector, http)
        end = time.time()
        page_i = get_page_i(url)
        print(f'R Page {page_i}: ', end - start)
        return page

    def process_result(result, http, http_collector):

        def get_full_result(DOI, http, http_collector):
            full_page = Page()
            while True:
                try:
                    full_page = http.get('https://dl.acm.org' + DOI, timeout=10)
                    if full_page.status_code == 200:
                        break
                except BaseException as error:
                    pass
                finally:
                    print('FULL PAGE: ', full_page.status_code, http.proxies['https'])
                    if full_page.status_code != 200:
                        http = setup_new_proxies(http_collector, http)
            return full_page
        
        def parse_full_result(full_result):
            full_result_parsed = BeautifulSoup(full_result.content, 'lxml')

            authors = full_result_parsed.find_all('span', class_='loa__author-name')
            authors_processed = set()
            for author in authors:
                authors_processed.add(author.text.encode('ascii', 'namereplace').decode())
            authors_string = ', '.join(list(authors_processed))
            
            abstract = full_result_parsed.find('div', class_='abstractSection abstractInFull')
            if abstract != None:
                abstract_processed = abstract.text.encode('ascii', 'namereplace').decode() 
            else:
                abstract_processed = 'No abstract available.'

            full_result_parsed = { 'Type' : type_result, \
                'Title': title_processed, 'DOI': DOI, 'Authors' : authors_string, \
                    'Abstract': abstract_processed}
            return full_result_parsed

        type_result = result.find('div', class_='issue-heading').text.lower()

        box = result.find('h5', class_='issue-item__title')
        title_processed = box.text.encode('ascii', 'namereplace').decode()
        DOI = box.find('a')['href']

        full_result = get_full_result(DOI, http, http_collector)
        full_result_processed = parse_full_result(full_result)
        return full_result_processed

    def get_results_list(page, http, http_collector):
        start = time.time()
        content = BeautifulSoup(page.content, 'lxml')
        results = content.find_all('li', class_='search__item issue-item-container')
        results_list = [process_result(result, http, http_collector) for result in results]
        end = time.time()
        print(f'Result Processing {page_i}: ', end - start)
        return results_list

    def write_csv(results_list, path):
        if not os.path.exists(f'{path}\\results'):
            os.mkdir(f'{path}\\results')

        if len(results_list) > 0:
            #with open('.\\results\\Page_{}.csv'.format(page_i), 'w', newline='') as csvfile:
            with open(f'{path}\\results\\Page_{page_i}.csv'.format(page_i), 'w', newline='') as csvfile:
                w = csv.DictWriter(csvfile, results_list[0].keys(), extrasaction='ignore')
                w.writeheader()
                w.writerows(results_list)


    page_i = get_page_i(url)
    http_collector = None
    try:
        http_collector = get_collector('http-collector-01')
    except:
        pass
    if http_collector == None:
        http_collector = make_collector(page_i)
    http = create_new_session(http_collector)

    if find_pages:
        return how_many_pages(url, http, http_collector, page_size)

    page = get_page(url, http, http_collector)
    results_list = get_results_list(page, http, http_collector)
    write_csv(results_list, path)
    return 

# Returns list of urls for scraping
def create_urls(page_size=50, pages=10, base_url=''):
    urls = [base_url+'&pageSize={}'.format(page_size)]
    for i in range(pages-1):
        next_url = base_url + '&pageSize={}&startPage={}'.format(page_size, i+1)
        urls.append(next_url)
    return urls

# Returns the url string for requests from search term
def parse_search_term(search_term):
    search_term = search_term.replace('(', '%28')
    search_term = search_term.replace(')', '%29')
    search_term = search_term.replace(' ', '+')
    return search_term
