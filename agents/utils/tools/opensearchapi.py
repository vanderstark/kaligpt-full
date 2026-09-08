#!/env/bin/env python3

# /agents/utils/tools/opensearchapi.py
# SudoHopeX KaliGPT
# Last updated: 9 fEB 2026


import requests
from newspaper import Article, Config


# Define a realistic user agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"

DEFAULT_BASE_URL = "http://127.0.0.1:5000"


def check_search_connection(timeout: int = 10) -> bool:
    """
    checks if the OpenSearchAPI search backend is available.
    """

    # perform a get request to test availability
    try:
        response = requests.get(f"{DEFAULT_BASE_URL}", timeout=timeout)
        return response.status_code == 200

    except requests.RequestException as re:
        print(f"OpenSearchAPI Search Connection error\nEndpoint used: {DEFAULT_BASE_URL}\nError details: {re}")
        return False    # any exception results as False


def safe_get_json(url: str, timeout: int = 30):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def parse_url_with_newspaper(url: str) -> str:
    """
    Parses the content of a URL using the newspaper library.

    :param url: the URL to parse
    :return: the content of the URL, main body only.
    """

    # Configure the newspaper settings
    config = Config()
    config.browser_user_agent = USER_AGENT
    # Increase the timeout from default 7 seconds to 15 or 30 seconds
    config.request_timeout = 30

    # 1. Instantiate the Article with the custom config
    article = Article(url, config=config)

    try:
        # 2. Download the article content
        article.download()

        # Check if the download was successful before parsing
        if article.download_state != 2:  # 2 is ArticleDownloadState.SUCCESS
            # If download failed but didn't throw an exception (e.g., 404, 500 status)
            return f"Error: Download failed for unknown reason or server status was bad (Status: {article.download_state})."

        # 3. Parse the content
        article.parse()

        # Return the main text
        return article.text

    except Exception as e:
        return f"Error: Failed to parse {url}: {e}"


def keyword_search(keyword: str,
                engines: str = "google",
                top_n: int = 4,
                timeout: int = 30
    ) -> list:
    """
    Performs Live search via OpenSearchAPI.

    :param keyword: the keyword to search for
    :param engines: search keyword in specific engines (optional, default="google")
    :param top_n: number of results from top to return to llm
    :param timeout: timeout for the requests

    :return: a list of search results in the format of [(title, link), (title, link), ...]
        return [(None, None)] if no search results are found
    """

    blacklist = ["github.com", "medium.com"] # sites not to include in search results

    # full example query: GET http://127.0.0.1:5000/mega/search?q=SudoHopeX&engines=duckduckgo,bing
    url = f"{DEFAULT_BASE_URL}/mega/search?q={keyword}"

    # Mandatory parameters with default values
    if engines: url += f"&engines={engines}"

    try:
        response = safe_get_json(url, timeout=timeout)
        # print("Response: ", response)
        results_by_engine = response.get("results", {})
        # print("Results by engine: ", results_by_engine)

    except Exception as e:
        # print(f"Request failed: {e}")
        return [(None, None)]

    # get the top n search results on the current page
    search_result = []

    for engine, results in results_by_engine.items():  # will iterate for each engine's values
        # print(f"Results for engine - {engine}: ", results)
        for item in results:
            # print("Item: ", item)
            if len(search_result) >= top_n:
                break

            title = item.get("title")
            link = item.get("link")

            if not link or not title:
                continue

            # Blacklist check
            if any(domain in link for domain in blacklist):
                    continue

            search_result.append((title, link))

        if len(search_result) >= top_n:
            break

    return search_result if search_result else [(None, None)]


def crawl_search(search_results: list) -> list[tuple[str | None]]:
    """
    Crawls the search results into a JSON string as RAG.
    :param search_results: the search results returned by `keyword_search`
        the search result should be in the format of [(title, link), (title, link), ...]
        the search result should be as [(None, None)] if no search results are found

    :return: a list of strings as RAG
    """
    rag = []
    for item in search_results:

        # Check type (is a list/tuple), length(has 2 elements), and that both elements are truthy (not None or empty) of item
        if not (isinstance(item, (list, tuple)) and len(item) >= 2 and item[0] and item[1]):
            continue

        title, link = item[0], item[1]

        try:
            main_content = parse_url_with_newspaper(link)

            # each website info is in the format of {title: "title", link: "link", content: "content"}
            rag.append({"title": title, "link": link, "content": main_content})

        except Exception as e:
            # print(f"Request failed on {link}: {e}")
            rag.append(
                {"title": title, "link": link, "content": "Failed to retrieve content"}
            )
            continue

    return rag


def search_as_RAG(list_of_keywords: list[str]) -> list:
    """
    Search the list of keywords and returns the search results as RAG (via OpenSerp API).

    :param list_of_keywords: a list of keywords to search (keywords can be one or more)
    """
    rag = []
    for keyword in list_of_keywords:
        rag.extend(crawl_search(keyword_search(keyword=keyword)))

    return rag


# Testing tools
if __name__ == "__main__":
    print(check_search_connection())
    print(search_as_RAG(["SudoHopeX KaliGPT ai for Hackers"]))
