import re
from datetime import datetime
import json

import bs4
import pandas as pd
from pytube import YouTube
from tqdm import tqdm

COMMENT_DATE_REGEX = re.compile(
    r"([0-9]{4})\-([0-9]{2})\-([0-9]{2})(?:\s*|T)([0-9]{2})\:([0-9]{2})\:([0-9]{2})"
)


def _group_by_brs(els):
    """
    splits elements (children of some top-level div)
    into groups of elements, separated by 'br' elements
    we want to split by lines which have '<br/>' elements, since
    it can contain URLs whose link text contains both text and
    a URL we want
    """
    res: ListOfTags = []
    cur: List[TextOrEl]
    cur = []
    for tag in els:
        if isinstance(tag, bs4.element.NavigableString):
            cur.append(tag)
        elif isinstance(tag, str):
            cur.append(tag)
        elif isinstance(tag, bs4.element.Tag):
            # is a bs4.element.Tag
            if tag.name == "br":
                res.append(cur)
                cur = []
            else:
                cur.append(tag)
    if cur:
        res.append(cur)
    return res


def _extract_html_li_date(comment: str) -> datetime:
    matches = re.search(COMMENT_DATE_REGEX, comment)
    if matches:
        g = matches.groups()
        year, month, day, hour, minute, second = tuple(map(int, g))
        return str(datetime(year, month, day, hour, minute, second))
    else:
        raise RuntimeError(f"Couldn't parse date from {comment}")


def _parse_html_li(li: bs4.element.Tag):
    parsed_date: datetime = _extract_html_li_date(li.text)
    groups = _group_by_brs(li.children)
    assert len(groups) == 2, f"Expected 2 parts separated by a <br /> {groups}"
    desc = ""
    for tag in groups[1]:
        if isinstance(tag, bs4.element.NavigableString):
            desc += str(tag)
        elif isinstance(tag, bs4.element.Tag):
            desc += str(tag.text)
    urls = list({link.attrs["href"]
                for link in li.select("a") if "href" in link.attrs})
    return urls[1], urls[0], desc.strip()[:255], parsed_date.replace('T', ' ')


def parse_html_comment_file(p):
    with open(p, "r", encoding='ISO-8859-1') as f:
        text = f.read()
        f.close()
    soup = bs4.BeautifulSoup(text, "html.parser")
    for li in soup.select("li"):
        try:
            yield _parse_html_li(li)
        except Exception as e:
            yield e
            
def parse_watch_history_file(p):
    with open(p, "r", encoding='ISO-8859-1') as f:
        data = json.load(f)
        f.close()
      
    ##Limit to around 1000 videos to prevent running too long
    if len(data) > 1000:
        data = [x for i, x in enumerate(data) if i % int((len(data)/1000)) == 0]
        
    for watch in tqdm(data):
        try:
            title = watch['title'][7:]
            url = watch['titleUrl']
            date = watch['time'][:-1].replace('T', ' ')
            channelName = watch['subtitles'][0]['name']
            channelUrl = watch['subtitles'][0]['url']
            video = YouTube(url)
            yield title, url, channelName, channelUrl, date, video.length
        except:
            yield title, url, channelName, channelUrl, date, 'NULL'
        
def parse_search_history_file(p):
    with open(p, "r", encoding='ISO-8859-1') as f:
        data = json.load(f)
        f.close()
        
    for search in tqdm(data):
        try:
            if search['title'].startswith('Watched'):
                continue
            title = search['title'][13:]
            url = search['titleUrl']
            date = search['time'][:-1].replace('T', ' ')
            yield title, date, url
        except:
            pass
        
def formatString(string):
    string = string.replace("'", "''")
    string = string.replace("&", "' || chr(38) || '")
    return string

if __name__ == "__main__":
    
    initStr = []
    
    commentsPath = 'Takeout\\YouTube and YouTube Music\\my-comments\\my-comments.html'
    watchHistoryPath = 'Takeout\\YouTube and YouTube Music\\history\\watch-history.json'
    searchHistoryPath = 'Takeout\\YouTube and YouTube Music\\history\\search-history.json'
    subscriptionsPath = 'Takeout\\YouTube and YouTube Music\\subscriptions\\subscriptions.csv'
    
    commentInsert = 'INSERT INTO comments(commentURL, videoURL, commentText, commentDate) VALUES (\'{}\', \'{}\', \'{}\', TIMESTAMP \'{}\');'
    watchHistoryInsert = 'INSERT INTO watch_history(title, videoURL, channelName, channelURL, watchDate, length) VALUES (\'{}\', \'{}\', \'{}\', \'{}\', TIMESTAMP \'{}\', {});'
    searchHistoryInsert = 'INSERT INTO search_history(searchQuery, searchDate, searchURL) VALUES (\'{}\', TIMESTAMP \'{}\', \'{}\');'
    subscriptionsInsert = 'INSERT INTO subscriptions(channelId, channelName, channelURL) VALUES (\'{}\', \'{}\', \'{}\');'
    
    with open('lib/base.sql', 'r') as f:
        initStr.append(f.read())
        initStr.append('\n')
        f.close()
    
    comments = []
    urls = []
    date = []
    for data in parse_html_comment_file(commentsPath):
        if isinstance(data, Exception):
            print(data)
        else:
            initStr.append(commentInsert.format(formatString(data[0]), formatString(data[1]), formatString(data[2]), data[3]))
    
    titles = []
    urls = []
    channelNames = []
    channelUrls = []
    videoLengths = []
    for data in parse_watch_history_file(watchHistoryPath):
        initStr.append(watchHistoryInsert.format(formatString(data[0]), formatString(data[1]), formatString(data[2]), formatString(data[3]), data[4], data[5]))
    
    queries = []
    dates = []
    for data in parse_search_history_file(searchHistoryPath):
        initStr.append(searchHistoryInsert.format(formatString(data[0]), data[1], formatString(data[2])))
    
    df = pd.read_csv(subscriptionsPath)
    
    for index, row in df.iterrows():
        initStr.append(subscriptionsInsert.format(formatString(row['Channel Id']), formatString(row['Channel Title']), formatString(row['Channel Url'])))
        
    with open('init.sql', 'w', encoding='utf8') as f:
        f.write('\n'.join(initStr))