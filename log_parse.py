"""
This module parses the contents of the query log file
and displays the top 5 URL path
"""

import re
from collections import defaultdict, Counter
from time import strptime
from urllib.parse import urlparse


class Request:
    """
    The class stores all data about the web request
    """

    def __init__(self, request_line, date_time):
        urltype = re.search(r'\".*\"', request_line).group().strip('"')
        request_type, row_url, protocol = urltype.split()
        parse_url = urlparse(row_url)
        url = parse_url.netloc + parse_url.path
        responce_code, responce_time = re.search(r' \d+ \d+',
                                                 request_line).group().split()

        self.url = url
        self.date_time = date_time
        self.request_type = request_type
        self.protocol = protocol
        self.responce_code = responce_code
        self.responce_time = responce_time

    def __str__(self):
        return """url={}
datetime={}
request_type={}
protocol={}
responce_code={}
responce_time={}
""".format(self.url, self.date_time,
           self.request_type, self.protocol,
           self.responce_code, self.responce_time)

    def is_file(self):
        """
        Checks if this query is leading to a file
        """

        url_path = self.url.split('/')
        if re.match(r".+\.\w+", url_path[-1]):
            # Find <file_name>.<extension>
            return True
        return False


def parse_request(line):
    """
    The function parses the query string and returns an object of type Request
    """

    datetimestring = re.search(r"\[.*\]", line).group().strip('[]')
    date_time = strptime(datetimestring, "%d/%b/%Y %H:%M:%S")

    return Request(line, date_time)


def is_good_request(request, params):
    """
    Сhecks the query for compliance with the parameters
    """

    if params['ignore_files']:
        if request.is_file():
            return False

    if params['ignore_urls']:
        if request.url in params['ignore_urls']:
            return False

    if params['start_at']:
        if request.date_time < strptime(params['start_at'], "%d/%b/%Y %H:%M:%S"):
            return False

    if params['stop_at']:
        if request.date_time > strptime(params['stop_at'], "%d/%b/%Y %H:%M:%S"):
            return False

    if params['request_type']:
        if params['request_type'] != request.request_type:
            return False
    return True


def add_to_request_dict(request, request_dict, params):
    """
    The function adds or updates the URL-path dictionary
    """

    if not is_good_request(request, params):
        return

    if params['ignore_www']:
        if re.match(r"www\.", request.url):
            # Remove www. from url ????????????????????
            request.url = request.url[4:]

    request_dict[request.url][0] += 1
    request_dict[request.url][1] += int(request.responce_time)


def find_top_five(request_dict, slow_queries):
    """
    The function sorts the dictionary and returns the top 5 used URLs
    """

    if slow_queries:
        request_counter = Counter({k: v[1] // v[0] for k, v in request_dict.items()})
        sorted_pairs = [i[1] for i in request_counter.most_common(5)]
    else:
        request_counter = Counter({k: v[0] for k, v in request_dict.items()})
        sorted_pairs = [i[1] for i in request_counter.most_common(5)]

    return sorted_pairs


def parse(
        ignore_files=False,
        ignore_urls=None,
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    """
    The main function that parses the log file
    """
    params = {'ignore_files': ignore_files, 'ignore_urls': ignore_urls,
              'start_at': start_at, 'stop_at': stop_at,
              'request_type': request_type, 'ignore_www': ignore_www}

    with open("log.log", 'r') as log_file:
        regular_exp = r'\[.*\] \".*\" \d+ \d+'
        # Find correct requests in log file
        request_dict = defaultdict(lambda: [0, 0])

        for line in log_file:
            if re.match(regular_exp, line):
                request = parse_request(line)
                add_to_request_dict(request, request_dict, params)
        top5 = find_top_five(request_dict, slow_queries)
    return top5


if __name__ == "__main__":
    TOP5 = parse()
    print(TOP5)
