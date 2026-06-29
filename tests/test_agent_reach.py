from datetime import date

from islandedge.agent_reach import SearchRequest, parse_output, reddit_queries


def test_opencli_reddit_payload_maps_title_body_and_epoch_timestamp():
    output = """
    [
      {
        "id": "abc123",
        "title": "Bryce and Trinity",
        "subreddit": "r/LoveIslandUSA",
        "author": "tester",
        "score": 16,
        "comments": 21,
        "url": "https://www.reddit.com/r/LoveIslandUSA/comments/abc123/sample/",
        "created_utc": 1782751454,
        "selftext": "They are my Love Island USA favorites."
      }
    ]
    """
    request = SearchRequest(8, date(2026, 6, 29), "reddit", "Bryce", "LoveIslandUSA")

    rows = parse_output(output, request)

    assert rows[0]["source_id"] == "abc123"
    assert rows[0]["posted_at"].startswith("2026-06-29T")
    assert "Bryce and Trinity" in rows[0]["text"]
    assert "favorites" in rows[0]["text"]
    assert rows[0]["engagement"] == 16


def test_reddit_queries_do_not_embed_subreddit_operator():
    class Contestant:
        display_name = "Bryce"
        full_name = "Bryce Dettloff"
        aliases = ("bryce", "bryce dettloff")

    queries = reddit_queries([Contestant()])

    assert "Bryce" in queries
    assert all("subreddit:" not in query for query in queries)
