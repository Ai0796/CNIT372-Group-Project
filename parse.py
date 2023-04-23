import re
from datetime import datetime, timezone
import json
import shutil

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
        return datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
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
    return desc.strip(), urls[1], parsed_date


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
        
    data = [x for i, x in enumerate(data) if i % 100 == 0]
        
    for watch in tqdm(data):
        try:
            title = watch['title']
            url = watch['titleUrl']
            channelName = watch['subtitles'][0]['name']
            channleUrl = watch['subtitles'][0]['url']
            video = YouTube(url)
            yield title, url, channelName, channleUrl, video.length
        except:
            pass
        
def parse_search_history_file(p):
    with open(p, "r", encoding='ISO-8859-1') as f:
        data = json.load(f)
        f.close()
        
    for search in tqdm(data):
        try:
            title = search['title']
            url = search['time']
            yield title, url
        except:
            pass

if __name__ == "__main__":
    
    ##Parsing Comments
    commentsPath = 'Takeout\\YouTube and YouTube Music\\my-comments\\my-comments.html'
    watchHistoryPath = 'Takeout\\YouTube and YouTube Music\\history\\watch-history.json'
    searchHistoryPath = 'Takeout\\YouTube and YouTube Music\\history\\search-history.json'
    subscriptionsPath = 'Takeout\\YouTube and YouTube Music\\subscriptions\\subscriptions.csv'
    
    comments = []
    urls = []
    date = []
    for data in parse_html_comment_file(commentsPath):
        if isinstance(data, Exception):
            print(data)
        else:
            comments.append(data[0])
            urls.append(data[1])
            date.append(data[2])
            
    df = pd.DataFrame({'comment': comments, 'url': urls, 'date': date})
    df.to_csv('my-comments.csv', index=False)
    
    titles = []
    urls = []
    channelNames = []
    channelUrls = []
    videoLengths = []
    for data in parse_watch_history_file(watchHistoryPath):
        titles.append(data[0])
        urls.append(data[1])
        channelNames.append(data[2])
        channelUrls.append(data[3])
        videoLengths.append(data[4])
        
    df = pd.DataFrame({'title': titles, 'url': urls, 'channelName': channelNames, 'channelUrl': channelUrls, 'videoLength': videoLengths})
    df.to_csv('watch-history.csv', index=False)
    
    queries = []
    dates = []
    for data in parse_search_history_file(searchHistoryPath):
        queries.append(data[0])
        dates.append(data[1])
        
    df = pd.DataFrame({'query': queries, 'date': dates})
    df.to_csv('search-history.csv', index=False)
    
    shutil.copyfile(subscriptionsPath, 'subscriptions.csv')