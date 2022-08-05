import os
from bs4 import BeautifulSoup
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from urllib.parse import urlparse
import re


def get_url_files_dir():
    current_dir = str(os.getcwd()) + "/UrlFiles"  # gets current working directory (path to scraper.py
    return current_dir


def unique_pages():
    url_files_directory = get_url_files_dir()
    count = 0
    for roots, dirs, files in os.walk(url_files_directory):
        for file in files:
            count += 1
    return int(count / 2)


def longest_page():
    url_files_directory = get_url_files_dir()
    longest_file = ""
    maxi = 0
    for roots, dirs, files in os.walk(url_files_directory):
        for file in files:
            try:
                if file == "page_content.html":
                    file_path = os.path.join(roots, file)
                    f = open(file_path, "r")
                    html = f.read()
                    soup = BeautifulSoup(html, features="html.parser")
                    text = soup.get_text().lower().strip().rstrip()
                    tokens = [x.lower() for x in re.split('[^a-zA-Z0-9]+', text)]
                    if len(tokens) > maxi:
                        maxi = len(tokens)
                        longest_file = open(os.path.join(roots, files[0])).readline().rstrip()
            except UnicodeDecodeError:
                pass
    return longest_file, maxi


def word_frequency():
    url_files_directory = get_url_files_dir()
    freq_dict = defaultdict(int)
    stops = set(stopwords.words('english'))
    for roots, dirs, files in os.walk(url_files_directory):
        for file in files:
            try:
                if file == "page_content.html":
                    file_path = os.path.join(roots, file)
                    f = open(file_path, "r")
                    html = f.read()
                    soup = BeautifulSoup(html, features="html.parser")
                    text = soup.get_text().lower().strip().rstrip()
                    tokens = [x.lower() for x in re.split('[^a-zA-Z]+', text)]
                    for words in tokens:
                        if words not in stops:
                            freq_dict[words] += 1
            except UnicodeDecodeError:
                pass
    freq_dict = dict(sorted(freq_dict.items(), key=lambda x: (-x[1], x[0])))
    top = list()
    count = 0
    for keys, values in freq_dict.items():
        if count < 50:
            count += 1
            top.append((keys, values))
        else:
            break
    return top


def sub_domains():
    sub_domain_dict = defaultdict(int)
    url_files_directory = get_url_files_dir()
    for roots, dirs, files in os.walk(url_files_directory):
        for file in files:
            try:
                file_path = os.path.join(roots, file)
                if file == "url_file.txt":
                    f = open(file_path, "r")
                    page_url = f.readline()
                    url = urlparse(page_url)
                    if re.search(r".*\.(ics.uci.edu)", url.netloc.lower()):
                        # subdomain = url.netloc.split('.')
                        sub_domain_dict[url.scheme.lower() + "://" + url.netloc.lower()] += 1
                elif file == "page_content.html":
                    pass
            except UnicodeDecodeError:
                pass
    return sub_domain_dict


def return_sub_domain():
    sub_domain_dict = sub_domains()
    sub_domain_dict = sorted(sub_domain_dict.items(), key=lambda x: (x[0], x[1]))
    return sub_domain_dict


if __name__ == "__main__":
    f = open("ReportLogs.txt", "w")

    f.write("The Amount of Unique Pages: \n")
    f.write(str(unique_pages()) + '\n')
    f.write("\n")

    f.write("The URL of the Longest Page is : \n")
    f.write(str(longest_page()) + '\n')
    f.write("\n")

    f.write("The 50 Most Common Words and Associated Frequency: \n")
    f.write(str(word_frequency()) + '\n')
    f.write("\n")

    f.write("The URL and count of different subdomains in the ics.uci.edu domain: \n")
    f.write(str(return_sub_domain()) + '\n')
    f.close()
