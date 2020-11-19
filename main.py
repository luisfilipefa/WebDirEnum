import pathlib
import argparse
import time
import requests
import uuid
from datetime import datetime
from fake_headers import Headers
import concurrent.futures as cf


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
    args = parser.parse_args()
    return args


def fetch(url, session, log_file):
    fake_header = Headers(headers=False).generate()

    try:
        with session.get(url, headers=fake_header) as response:
            status = response.status_code

        if status < 400:
            print(f"+ [+] Found: {url.strip()} (Status: {status})")
            return True
    except requests.exceptions.RequestException as e:
        print(f"+ [!] An exception occurred: See log file... [!]")
        with log_file.open(mode="a") as f:
            f.write(str(e)+"\n")


def count_wordlist_len(wordlist):
    with wordlist.open(mode="r") as f:
        wordlist_len = f.readlines()
    return len(wordlist_len)


def main():
    start = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    ts = time.perf_counter()

    args = args_parser()
    wordlist = pathlib.Path(args.wordlist).resolve()
    wordlist_len = count_wordlist_len(wordlist)
    urls = (f"{args.url}/{url}" for url in wordlist.open(mode="r"))
    urls_found = 0
    log_filename = str(uuid.uuid4())
    log_file = pathlib.Path(f"{log_filename}.log").resolve()

    print("+"+"-"*50+"+")
    print(f"+ [*] Started at {start}")
    print("+"+"-"*50+"+")
    print(f"+ [*] Url: {args.url}")
    print(f"+ [*] Wordlist: {args.wordlist}")
    print(f"+ [*] {wordlist_len} words in wordlist")
    print(f"+ [*] Threads: {args.threads}")
    print("+"+"-"*50+"+")

    with requests.Session() as session:
        with cf.ThreadPoolExecutor(max_workers=args.threads) as executor:
            try:
                tasks = [executor.submit(
                    fetch, url, session, log_file) for url in urls]

                for task in cf.as_completed(tasks):
                    result = task.result()
                    if result:
                        urls_found += 1
            except KeyboardInterrupt:
                print(f"\n+ [!] Keyboard interrupt detected, exiting... [!]")
                pass

    end = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    te = time.perf_counter()

    print("+"+"-"*50+"+")
    print(f"+ [*] Finished at {end}")
    print(f"+ [*] Found {urls_found} urls in {round(te-ts,2)} seconds")
    print("+"+"-"*50+"+")


if __name__ == "__main__":
    main()
