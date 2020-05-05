import sys
import time
import multiprocessing
from csv_merger import concatenate_csv
from pathos.multiprocessing import ProcessPool as Pool
from processing import process_page, create_urls, parse_search_term

def call_processes(url, path, pages):
    urls = create_urls(10, int(pages), url)

    # I want a better way to do this
    paths = []
    for _ in range(len(urls)):
        paths.append(path)
    
    start = time.time()
    p = Pool(multiprocessing.cpu_count() - 1)
    result = p.map(process_page, urls, paths)
    end = time.time()
    print('Full Run: ', end - start)
    p.clear()


if __name__ == "__main__":
    multiprocessing.freeze_support()

    search_term = sys.argv[1]
    path = sys.argv[2]
    pages = sys.argv[3]

    call_processes(search_term, path, pages)


