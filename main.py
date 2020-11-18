import argparse
import requests
import time
import pathlib
from fake_headers import Headers
from datetime import datetime
import concurrent.futures as cf


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Python script to bruteforce web directories using asyncio")
    parser.add_argument(
        "-u",
        "--url",
        help="The url to brute force (Include HTTP schema)",
        type=str,
        required=True)
    parser.add_argument(
        "-w",
        "--wordlist",
        help="The wordlist to use",
        type=str,
        required=True)
    parser.add_argument(
        "-t",
        "--threads",
        help="The number of simultaneous threads (Default 20)",
        type=int,
        required=False,
        default=20)
    parser.add_argument(
        "-r",
        "--recursive",
        help="Be recursive in the directories found",
        type=bool,
        required=False,
        default=False
    )
    args = parser.parse_args()
    return args


def count_lines(file):
    lines = 0
    with file.open(mode="r") as f:
        for line in f:
            lines += 1
    return lines


def check_url_status(url, session):
    header = Headers(headers=False).generate()

    try:
        with session.get(url, headers=header) as response:
            status = response.status_code
            if status == 200:
                print(f"[*] Found: {url.strip()} (Status: {status})")
                return url
    except requests.exceptions.RequestException as e:
        print(f"[!] Exception ocurred: {e}")


def run(urls, threads, recursive):
    urls_found = []

    with requests.Session() as session:
        try:
            with cf.ThreadPoolExecutor(max_workers=threads) as executor:
                tasks = (executor.submit(check_url_status, url, session)
                         for url in urls)

                for task in cf.as_completed(tasks):
                    result = task.result()
                    if result:
                        urls_found.append(url)
                return urls_found
        except KeyboardInterrupt:
            pass


def main():
    ts = time.perf_counter()
    start = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

    args = parse_args()
    wordlist = pathlib.Path(args.wordlist).resolve()
    wordlist_length = count_lines(wordlist)
    urls = (f"{args.url}/{url}" for url in wordlist.open(mode="r"))

    print("-"*50)
    print(f"[*] Started at {start} [*]")
    print("-"*50)
    print(f"[*] Url: {args.url} [*]")
    print(f"[*] Wordlist: {args.wordlist} ({wordlist_length} words)[*]")
    print("-"*50)

    urls_found = run(urls, args.threads, args.recursive)
    te = time.perf_counter()
    end = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

    print("[!] Keyboard interrupt detected, exiting... [!]")
    print("-"*50)
    print(f"[*] Found {len(urls_found)} urls in {round(te-ts,2)} seconds [*]")
    print("-"*50)
    print(f"[*] Finished at {end} [*]")
    print("-"*50)


if __name__ == "__main__":
    main()
