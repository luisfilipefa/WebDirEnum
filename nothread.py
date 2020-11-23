import argparse
import pathlib
import requests
import time
from datetime import datetime
from fake_headers import Headers


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--url", help="The url to bruteforce", type=str, required=True)
    parser.add_argument("-w", "--wordlist",
                        help="The wordlist to use", type=str, required=True)
    args = parser.parse_args()
    return args


def check_url_status(url, session):
    header = Headers(headers=False).generate()

    with session.get(url, headers=header) as response:
        if response.status_code != 404:
            print(f"[+] Found: {url.strip()} [Status: {response.status_code}]")
            return True


def queue_wordlist(domain, file):
    wordlist = pathlib.Path(file).resolve()
    urls = (f"{domain}/{url}" for url in wordlist.open(mode="r"))
    urls_count = 0

    with wordlist.open(mode="r") as f:
        for line in f:
            urls_count += 1

    return urls, urls_count


def main():
    start = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    ts = time.perf_counter()

    args = args_parser()
    domain = args.url
    file = args.wordlist
    urls, urls_count = queue_wordlist(domain, file)

    print("-"*50)
    print(f"[*] Started at {start}")
    print("-"*50)
    print(f"[*] Domain: {domain}")
    print(f"[*] File: {file}")
    print(f"[*] {urls_count} lines in file")
    print("-"*50)

    with requests.Session() as session:
        urls_found = 0

        for url in urls:
            try:
                result = check_url_status(url, session)
                if result:
                    urls_found += 1
            except KeyboardInterrupt:
                print("\n[!] Keyboard interrupt detected, exiting...")
                break

    te = time.perf_counter()
    print("-"*50)
    print(f"[*] Found {urls_found} in {round(te-ts,2)} seconds")
    print("-"*50)


if __name__ == '__main__':
    main()
