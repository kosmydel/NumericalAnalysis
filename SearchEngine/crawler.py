import random
from multiprocessing import Process, Queue, Pool
import requests
from bs4 import BeautifulSoup
import time, os

URL_PREFIX = "https://en.wikipedia.org"
N = 64
MAX_DEPTH = 2
START_WEBPAGES = ["/wiki/Poland", "/wiki/Ma", "/wiki/World"]


def scrape_page(tasks):
	while not queue.empty():
		depth, msg = tasks.get()
		print(f'{os.getpid()} looking in {msg} by {os.getpid()}\t, left {queue.qsize()}')
		page = requests.get(URL_PREFIX + msg)

		soup = BeautifulSoup(page.content, "html.parser")
		results = soup.find_all(name="p")

		f = open(msg[1:] + ".txt", "w")
		for paragraph in results:
			if paragraph.text:
				f.write(paragraph.text)
		f.close()

		links = soup.find_all(name="a", href=lambda h: h and h.startswith('/wiki/') and not h.startswith(
			'/wiki/File:') and not h.startswith('/wiki/Special:'),
							  rel=False, lang=False)
		if depth < MAX_DEPTH:
			for link in links:
				tasks.put((depth + 1, link['href']))

	print(f'exiting {os.getpid()}')


class CrawlerStatus:
	def __init__(self):
		self.webpages_processed = 0


if __name__ == "__main__":
	queue = Queue()
	for wp in START_WEBPAGES:
		queue.put((0, wp))
	processes = [Process(target=scrape_page, args=[queue]) for _ in range(N)]

	for i in range(len(START_WEBPAGES)):
		processes[i].start()

	time.sleep(3)

	for i in range(len(START_WEBPAGES), N):
		processes[i].start()

	for p in processes:
		p.join()