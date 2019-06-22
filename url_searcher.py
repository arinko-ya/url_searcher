import re
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests


def generate_root_url(target_url: str) -> str:
    """
    ルートURLの生成
    """
    parsed_url = urlparse(target_url)
    return f'{parsed_url.scheme}://{parsed_url.netloc}/'


def replacement_to_absolute_link(link_list: set, root_url: str) -> set:
    """
    抽出された相対リンクを絶対リンクに置き換え
    """
    if link_list:
        return set(map(
            lambda x: re.sub('^/', root_url, x) if x and x.startswith('/') else x,
            link_list
        ))


def creation_link_in_pages(search_url: str, root_url: str, target_url: str) -> set:
    """
    ページ内のリンクを取得
    """
    res = requests.get(search_url)
    soup = BeautifulSoup(res.text, "html.parser")
    relative_links = set([a.get("href") for a in soup.find_all('a')])
    if not relative_links:
        return set()

    link_in_pages = replacement_to_absolute_link(
        relative_links, root_url
    )
    return set(l for l in link_in_pages if l and l.startswith(target_url))


def url_search(link_target: str, root_url: str, target_url: str, search_list: list) -> dict:
    """
    ターゲットリンクの存在するURLのリストとページ内リンクリストを作成
    """
    hit_link = []
    all_link_in_pages = set()

    for search_url in search_list:
        link_in_pages = creation_link_in_pages(
            search_url=search_url,
            root_url=root_url,
            target_url=target_url
        )
        if link_target in link_in_pages:
            hit_link.append(search_url)
        all_link_in_pages |= link_in_pages

    return {
        'hit_link': hit_link,
        'link_in_pages': list(all_link_in_pages)
    }


def output_result(result_list: list):
    """
    結果を出力
    """
    for result in result_list:
        print(result)


def main(target_url: str, link_target: str, recursive_times: int=0) -> list:
    root_url = generate_root_url(target_url)
    next_search_list = [target_url]
    scanned_list = [target_url]
    hit_links = []
    count = 0

    while recursive_times >= count:
        result = url_search(
            link_target=link_target,
            root_url=root_url,
            target_url=target_url,
            search_list=next_search_list
        )
        link_in_pages = set(result['link_in_pages'])
        link_in_pages -= set(scanned_list)
        next_search_list = list(link_in_pages)

        scanned_list.extend(next_search_list)
        hit_links.extend(result['hit_link'])
        print(count)
        count += 1

    return hit_links


if __name__ == '__main__':
    args = sys.argv
    hit_links = main(
        target_url=args[1],
        link_target=args[2],
        recursive_times=int(args[3])
    )

    output_result(hit_links)
