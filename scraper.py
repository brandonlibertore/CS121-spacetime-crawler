import re
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
import time
from difflib import SequenceMatcher
import hashlib
import os
from fileProcessor import *


def scraper(url, resp):
    links = []
    if resp.status == 200:
        links = extract_next_links(url, resp)
        try:
            current_dir = str(os.getcwd()) + "/UrlFiles"  # gets current working directory (path of UrlFiles)
            os.mkdir(current_dir)  # create new directory named URL files
        except FileExistsError:
            pass

        x = [link for link in links if is_valid(link)]  # store every valid link
        for link in x:
            link_hash = hashlib.md5(link.lower().encode("utf-8")).hexdigest()  # Get a HASH for EACH URL -> Name of file
            file_dir = os.path.join(current_dir, link_hash)  # Create path to file name
            try:
                os.mkdir(file_dir)  # Create new directory for specific URL based on its hash
            except FileExistsError:
                pass

            # WITHIN DIRECTORY OF SPECIFIC URL:

            # Write the URL only to a single txt file
            url_path = file_dir + "/url_file.txt"
            f = open(url_path, "w")  # Open file to write content into
            f.write(link + '\n')

            # Write the content of the URL page to a file
            content_path = file_dir + "/page_content.html"
            f = open(content_path, "wb")
            f.write(resp.raw_response.content)  # Write content to file

    return [link for link in links if is_valid(link)]


# Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

def extract_next_links(url, resp):
    url_set = set()
    prev_url = None
    if (resp.raw_response is not None) and (resp.raw_response.content is not None) and (resp.status == 200):
        soup = BeautifulSoup(resp.raw_response.content, features="html.parser")
        for link in soup.find_all('a'):
            try:
                defragged_url = urldefrag(link.get('href'))[0]  # get current URL and defragment
                if prev_url is None: # first iteration
                    url_set.add(defragged_url) # add defragged url to set
                    prev_url = defragged_url # set previous url to current URL
                else: # iterations after first iteration
                    if SequenceMatcher(None, defragged_url, prev_url).ratio() >= .9:
                        prev_url = defragged_url
                    else:
                        url_set.add(defragged_url)
                        prev_url = defragged_url
            except Exception:
                pass
    return list(url_set)


def is_valid(url):
    # Decide whether to crawl this url or not.
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()) and \
            not re.search(
               r".*\.(css|js|bmp|gif|jpe?g|ico"
               + r"|png|tiff?|mid|mp2|mp3|mp4"
               + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
               + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
               + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
               + r"|epub|dll|cnf|tgz|sha1"
               + r"|thmx|mso|arff|rtf|jar|csv"
               + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower()) and \
            re.search(
                r".*\.(ics.uci.edu|cs.uci.edu|informatics.uci.edu|stat.uci.edu|"
                + r"today.uci.edu/department/information_computer_sciences)", parsed.netloc.lower()) and \
            not (re.search(r"\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])", parsed.path.lower()) and
                 re.search(r"(wics\.)", parsed.netloc.lower())) and \
            not re.search(r"(calendar.ics.uci.edu)", parsed.netloc.lower()) and \
            not re.search(r"(replytocom=)", parsed.query.lower()) and \
            not re.search(r"(version=)", parsed.query.lower()) and \
            not re.search(r"(share=)", parsed.query.lower()) and \
            not re.search(r"(wics-hosts-a-toy-hacking-workshop-with-dr-garnet-hertz)", parsed.path.lower()) and \
            not (re.search(r"(isg\.)", parsed.netloc.lower()) and re.search(r"(action=)", parsed.query.lower())) and \
            not (re.search(r"(mt-live\.)", parsed.netloc.lower()) and re.search(r"(events)", parsed.path.lower())) and \
            not (re.search(r"(mt-live\.)", parsed.netloc.lower()) and re.search(r"(filter)", parsed.query.lower()))

            # not re.match(r"(\d{4})", parsed.path.lower()) and \
            # not re.search(r"(ngs\.)", parsed.netloc.lower()) and \
            # not (re.search(r"(wics\.)", parsed.netloc.lower()) and re.search(r"(quarter)", parsed.path.lower())) and \
            # not (re.search(r"(isg\.)", parsed.netloc.lower()) and re.search(r"(event)", parsed.path.lower())) and \
            # not (re.search(r"(isg\.)", parsed.netloc.lower()) and re.search(r"(faculty2)", parsed.path.lower())) and \
            # not (re.search(r"(sli\.)", parsed.netloc.lower()) and re.search(r"(pmwiki)", parsed.path.lower())) and \
            # not (re.search(r"(isg\.)", parsed.netloc.lower()) and re.search(r"(news)", parsed.path.lower())) and \
            # not re.search(r"(cloudberry\.)", parsed.netloc.lower()) and \
            # not re.search(r"(filter)", parsed.query.lower())

            # PUT THESE BACK IF TRAPPED:
            # not (re.search(r"(sdcl\.)", parsed.netloc.lower()) and re.search(r"(\d{4})", parsed.path.lower())) and \
            # not (re.search(r"(cml\.)", parsed.netloc.lower()) and re.search(r"(\d{4})", parsed.path.lower())) and \
            # not re.search(r"(ucinetid=)", parsed.query.lower()) and \
            # not (re.search(r"(wics\.)", parsed.netloc.lower()) and re.search(r"(afg\d{2})", parsed.query.lower())) and \
            # not (re.search(r"(wics\.)", parsed.netloc.lower()) and re.search(r"(event)", parsed.path.lower())) and \

            # Line 94: remove all urls with any queries that match the ending.
            # Line 94: url must contain one of the domains
            # Line 97: remove urls that are from WICS calendar by path examination
            # Line 99: remove urls that lead to calendars
            # Line 100: remove urls that are blog thread replies
            # Line 101: ???
            # Line 102-103: remove urls that are WICS share links
            # Line 104: remove urls where the query is derived from a calendar event from WICS
            # Line 105: low content/information single image
            # Line 106: remove urls that are from wics and have events in path (calendar trap)
            # Line 107: remove urls that are from wics and have quarter in the path (blog like reports)
            # Line 108: remove subdomain pages of ngs, low content data and blog like
            # Line 109: remove subdomain cloudberry, extremely low content with only 1 line headers
            # Line 110: remove subdomain isg with paths containing faculty2, extremely low data.
            # Line 111: remove subdomain isg with paths containing event, extremely low data and certain event pages cannot be found.

# website that contains date and is WICS --> not (T & T) = FALSE
# website that has a date and is not WICS --> not (T & F) = TRUE
# website w/ no date and is WICS --> not (F & T) = TRUE
# website w/ no date and is not WICS --> not (F & F) = TRUE

    except TypeError:
        print ("TypeError for ", parsed)
        raise
