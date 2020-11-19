# WebDirEnum

Simple multithreaded tool to bruteforce web directories.

## Installation

Install requirements with pip.
```
pip install -r requirements.txt
```
## Arguments

|Flags|Args         |Description                                         |
|-----|-------------|----------------------------------------------------|
|-u   |--url        |The url to bruteforce (must provide http schema)    |
|-w   |--wordlist   |The wordlist to use                                 |
|-t   |--threads    |The number of concurrent threads to use (Default 20)|

## Usage

```
python webdirenum.py -u http://example.com -w wordlist.txt -t 30
```
