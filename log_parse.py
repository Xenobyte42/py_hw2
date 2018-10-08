"""
This module parses the contents of the query log file
and displays the top 5 URL path
"""

import re
import datetime
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


def make_datetime(datetimestring):
    """
    Creates an object of class datetime to string-based query
    """

    translator = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
                  "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                  "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

    date, time = datetimestring.split()
    day, month, year = date.split('/')
    hour, minute, second = time.split(':')
    return datetime.datetime(int(year), translator[month], int(day),
                             int(hour), int(minute), int(second))


def parse_request(line):
    """
    The function parses the query string and returns an object of type Request
    """

    datetimestring = re.search(r"\[.*\]", line).group().strip('[]')
    date_time = make_datetime(datetimestring)

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
        if request.date_time < make_datetime(params['start_at']):
            return False

    if params['stop_at']:
        if request.date_time > make_datetime(params['stop_at']):
            return False

    if params['request_type']:
        if params['request_type'] != request.request_type:
            return False
    return True


def add_to_request_list(request, request_list, params):
    """
    The function adds or updates the URL-path dictionary
    """

    if not is_good_request(request, params):
        return

    if params['ignore_www']:
        if re.match(r"www\.", request.url):
            # Remove www. from url
            request.url = request.url[4:]

    if request.url not in request_list:
        request_list[request.url] = [1, int(request.responce_time)]
    else:
        request_list[request.url][0] += 1
        request_list[request.url][1] += int(request.responce_time)


def find_top_five(request_list, slow_queries):
    """
    The function sorts the dictionary and returns the top 5 used URLs
    """

    sorted_pairs = sorted((v for k, v in request_list.items()),
                          key=lambda v: v[0], reverse=True)
    if slow_queries:
        sorted_pairs = sorted([(i[1] // i[0]) for i in sorted_pairs],
                              reverse=True)[:5]
    else:
        sorted_pairs = [i[0] for i in sorted_pairs[:5]]
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
        request_list = {}

        for line in log_file:
            if re.match(regular_exp, line):
                request = parse_request(line)
                add_to_request_list(request, request_list, params)
        top5 = find_top_five(request_list, slow_queries)
    return top5


if __name__ == "__main__":
    TOP5 = parse()
    print(TOP5)
