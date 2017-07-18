#https://nocodewebscraping.com/facebook-scraper/
#RUN THIS SCRIPT THIRD

import urllib2
import json
import datetime
import csv
import time
from collections import defaultdict


group_id = "558429457587216"

access_token = "1420698734686960|35deb28b79cd51e64ab729c0ba2c4566"

def request_until_succeed(url):
    time.sleep(100)
    req = urllib2.Request(url)
    success = False
    while success is False:
        try:
            response = urllib2.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception, e:
            print e
            time.sleep(5)

            print "Error for URL %s: %s" % (url, datetime.datetime.now())
            print "Retrying."

            if '400' in str(e):
                return None

    return response.read()

# Needed to write tricky unicode correctly to csv
def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22,
                            0x201D:0x22, 0xa0:0x20 }).encode('utf-8')


def getFacebookCommentFeedUrl(base_url):

    # Construct the URL string
    fields = "&fields=id,message,reactions.limit(0).summary(true)" + \
        ",created_time,comments,from,attachment"
    url = base_url + fields

    return url


def getReactionsForComments(base_url):

    reaction_types = ['like', 'love', 'wow', 'haha', 'sad', 'angry']
    reactions_dict = {}   # dict of {status_id: tuple<6>}

    for reaction_type in reaction_types:
        fields = "&fields=reactions.type({}).limit(0).summary(total_count)".format(
            reaction_type.upper())

        url = base_url + fields

        data = json.loads(request_until_succeed(url))['data']

        data_processed = set()  # set() removes rare duplicates in statuses
        for status in data:
            id = status['id']
            count = status['reactions']['summary']['total_count']
            data_processed.add((id, count))

        for id, count in data_processed:
            if id in reactions_dict:
                reactions_dict[id] = reactions_dict[id] + (count,)
            else:
                reactions_dict[id] = (count,)

    return reactions_dict

def processFacebookComment(comment, status_id, parent_id = ''):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first

    comment_id = comment['id']
    comment_message = '' if 'message' not in comment else \
            unicode_normalize(comment['message'])
    comment_author = unicode_normalize(comment['from']['name'])
    num_reactions = 0 if 'reactions' not in comment else \
        comment['reactions']['summary']['total_count']
    if 'attachment' in comment:
        attach_tag = "[[%s]]" % comment['attachment']['type'].upper()
        comment_message = attach_tag if comment_message is '' else \
                (comment_message.decode("utf-8") + " " + \
                        attach_tag).encode("utf-8")


    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    comment_published = datetime.datetime.strptime(
            comment['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    comment_published = comment_published + datetime.timedelta(hours=-5) # EST
    comment_published = comment_published.strftime(
            '%Y-%m-%d %H:%M:%S') # best time format for spreadsheet programs

    # Return a tuple of all processed data

    return (comment_id, status_id, parent_id, comment_message, comment_author,
            comment_published, num_reactions)

def scrapeFacebookPageFeedComments():
    with open('%s_facebook_comments.csv' % group_id, 'wb') as file:
        w = csv.writer(file)
        w.writerow(["comment_id", "status_id", "parent_id", "comment_message",
                    "comment_author", "comment_published", "num_reactions",
                    "num_likes", "num_loves", "num_wows", "num_hahas",
                    "num_sads", "num_angrys"])

        num_processed = 0   # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()

        column = defaultdict(list)

        with open('StatusIds.csv') as f:
            reader = csv.DictReader(f)  # read rows into a dictionary format
            for row in reader:  # read a row as {column1: value1, column2: value2,...}
                for (k, v) in row.items():  # go over each column name and value
                    column[k].append(v)  # append the value into the appropriate list

        listofstatusids = list(column['status_id'])

        for i in range(len(listofstatusids)):
            base = "https://graph.facebook.com/v2.9"
            parameters = "/?limit={}&access_token={}".format(
                302, access_token) #302 was the most comments a single status had in the JOTW facebook group page
            node = "/{}/comments".format(str(listofstatusids[i]))
            base_url = base + node + parameters

            url = getFacebookCommentFeedUrl(base_url)
            if request_until_succeed(url) is None:
                continue

            comments = json.loads(request_until_succeed(url))
            for comment in comments['data']:
                reactions = getReactionsForComments(base_url)
                comment_data = processFacebookComment(comment, str(listofstatusids[i]))
                reactions_data = reactions[comment_data[0]]
                w.writerow(comment_data + reactions_data)
                if 'comments' in comment:
                    has_next_subpage = True
                    sub_after = ''

                    while has_next_subpage:
                        sub_node = "/{}/comments".format(comment['id'])
                        sub_after = '' if sub_after is '' else "&after={}".format(
                            sub_after)
                        sub_base_url = base + sub_node + parameters + sub_after

                        sub_url = getFacebookCommentFeedUrl(
                            sub_base_url)
                        sub_comments = json.loads(
                            request_until_succeed(sub_url))
                        sub_reactions = getReactionsForComments(
                            sub_base_url)

                        for sub_comment in sub_comments['data']:
                            sub_comment_data = processFacebookComment(
                                sub_comment, str(listofstatusids[i]), comment['id'])
                            sub_reactions_data = sub_reactions[
                                sub_comment_data[0]]
                            w.writerow(sub_comment_data +
                                       sub_reactions_data)

                            num_processed += 1
                            if num_processed % 100 == 0:
                                print("{} Comments Processed: {}".format(
                                    num_processed,
                                    datetime.datetime.now()))

                        if 'paging' in sub_comments:
                            if 'next' in sub_comments['paging']:
                                sub_after = sub_comments[
                                    'paging']['cursors']['after']
                            else:
                                has_next_subpage = False
                        else:
                            has_next_subpage = False
                num_processed += 1
                if num_processed % 100 == 0:
                    print "%s Comments Processed: %s" % (num_processed,
                                                        datetime.datetime.now())
        print "\nDone!\n%s Comments Processed in %s" % \
          (num_processed, datetime.datetime.now() - scrape_starttime)


if __name__ == '__main__':
    scrapeFacebookPageFeedComments()


# The CSV can be opened in all major statistical programs. Have fun! :)