import pathlib
import argparse
import time
import requests
import uuid
# import schedule
# import socks
# import socket
import sys
import threading
from queue import Queue
from datetime import datetime
from fake_headers import Headers
from stem import Signal
from stem.control import Controller
# from threading import Thread
# import concurrent.futures as cf


class Worker(threading.Thread):
    def __init__(self, queue, session, log_file):
        threading.Thread.__init__(self)
        self.queue = queue
        self.session = session
        self.log_file = log_file

    def run(self):
        while True:
            url = self.queue.get()
            try:
                fetch(url, self.session, self.log_file)
            finally:
                self.queue.task_done()


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        help="The url to bruteforce",
        type=str,
        required=True
    )
    parser.add_argument(
        "-w",
        "--wordlist",
        help="The wordlist to use",
        type=str,
        required=True
    )
    parser.add_argument(
        "-t",
        "--threads",
        help="The number of concurrent threads to use",
        type=int,
        required=False,
        default=10
    )
    parser.add_argument(
        "-p",
        "--proxy",
        help="Enable proxy (Default False)",
        type=bool,
        required=False,
        default=False
    )
    args = parser.parse_args()
    return args


def fetch(url, session, log_file):
    fh = Headers(headers=False).generate()

    try:
        # if proxy:
        #     get_new_ip()

        #     proxies = {
        #         "http": "socks5://127.0.0.1:9050",
        #         "https": "socks5://127.0.0.1:9050"
        #     }

        with session.get(url, headers=fh) as response:
            status = response.status_code

        if status < 400:
            with threading.Lock():
                print(f"+ [+] Found: {url.strip()} (Status: {status})")
                # print(f"+ [*] Source ip: {get_external_ip()}")
                return True
    except requests.exceptions.RequestException as e:
        print(f"+ [!] An exception occurred: See log file... [!]")
        with log_file.open(mode="a") as f:
            f.write(str(e)+"\n")


def count_wordlist_len(wordlist):
    with wordlist.open(mode="r") as f:
        wordlist_len = f.readlines()
    return len(wordlist_len)


# def get_external_ip():
#     ext_ip = requests.get("https://api.ipify.org").text
#     return ext_ip


# def get_new_ip():
#     with Controller.from_port(port=9051) as c:
#         c.authenticate(password="215099")
#         c.signal(Signal.NEWNYM)


# def scheduler_threader(job):
#     job_thread = Thread(target=job)
#     job_thread.start()


def main():
    start = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    ts = time.perf_counter()

    args = args_parser()
    wordlist = pathlib.Path(args.wordlist).resolve()
    wordlist_len = count_wordlist_len(wordlist)
    urls = Queue()
    # urls_found = 0
    log_filename = str(uuid.uuid4())
    log_file = pathlib.Path(f"{log_filename}.log").resolve()

    for url in wordlist.open(mode="r"):
        urls.put(f"{args.url}/{url}")

    print("+"+"-"*50+"+")
    print(f"+ [*] Started at {start}")
    print("+"+"-"*50+"+")
    print(f"+ [*] Url: {args.url}")
    print(f"+ [*] Wordlist: {args.wordlist}")
    print(f"+ [*] {wordlist_len} words in wordlist")
    print(f"+ [*] Threads: {args.threads}")
    print("+"+"-"*50+"+")

    # schedule.every(5).seconds.do(scheduler_threader, get_new_ip)

    # while True:
    #     schedule.run_pending()

    try:
        with requests.Session() as session:
            for _ in range(args.threads):
                worker = Worker(urls, session, log_file)
                worker.daemon = True
                worker.start()

            urls.join()
    except KeyboardInterrupt:
        sys.exit(0)

    end = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    te = time.perf_counter()

    print("+"+"-"*50+"+")
    print(f"+ [*] Finished at {end}")
    # print(f"+ [*] Found {urls_found} urls in {round(te-ts,2)} seconds")
    print("+"+"-"*50+"+")


if __name__ == "__main__":
    main()
