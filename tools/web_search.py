from ddgs import DDGS


# ============================================================
# LIVE WEB SEARCH
# ============================================================

def search_web(query: str, max_results: int = 5) -> str:
    """
    Perform live web search using DDGS.

    - Current/latest/news questions -> DDGS News
    - News searches prioritize very recent results
    - Normal questions -> DDGS Text
    - Returns compact information for the AI model to summarize
    """

    try:
        print("=" * 60)
        print("LIVE WEB SEARCH")
        print(f"Query: {query}")
        print("=" * 60)

        query_lower = query.lower()

        # ----------------------------------------------------
        # DETECT NEWS / CURRENT INFORMATION
        # ----------------------------------------------------

        news_keywords = [
            "news",
            "latest",
            "current",
            "today",
            "recent",
            "right now",
            "now",
            "happening",
            "updates",
            "update",
            "breaking",
            "live",
        ]

        is_news_query = any(
            keyword in query_lower
            for keyword in news_keywords
        )

        # ----------------------------------------------------
        # IMPROVE NEWS QUERY
        # ----------------------------------------------------

        search_query = query

        if is_news_query:

            # For local news, make the search explicitly local.
            if "vijayawada" in query_lower:

                search_query = (
                    "Vijayawada Andhra Pradesh latest news today"
                )

            elif "andhra pradesh" in query_lower:

                search_query = (
                    f"{query} latest news today"
                )

            else:

                search_query = (
                    f"{query} latest news today"
                )

        print(f"Final search query: {search_query}")

        # ----------------------------------------------------
        # PERFORM SEARCH
        # ----------------------------------------------------

        with DDGS() as ddgs:

            if is_news_query:

                print("Search type: NEWS")

                try:

                    results = list(
                        ddgs.news(
                            search_query,
                            region="in-en",
                            safesearch="moderate",
                            timelimit="d",
                            max_results=max_results
                        )
                    )

                except Exception as news_error:

                    print(
                        f"News search failed: {news_error}"
                    )

                    results = []

                # --------------------------------------------
                # FALLBACK
                # --------------------------------------------

                if not results:

                    print(
                        "No recent news results found."
                    )

                    print(
                        "Falling back to text search..."
                    )

                    results = list(
                        ddgs.text(
                            search_query,
                            region="in-en",
                            safesearch="moderate",
                            timelimit="d",
                            max_results=max_results
                        )
                    )

            else:

                print("Search type: TEXT")

                results = list(
                    ddgs.text(
                        query,
                        region="in-en",
                        safesearch="moderate",
                        max_results=max_results
                    )
                )

        # ----------------------------------------------------
        # NO RESULTS
        # ----------------------------------------------------

        if not results:

            print("=" * 60)
            print("NO SEARCH RESULTS")
            print("=" * 60)

            return (
                "I could not find current web information "
                "for this query right now."
            )

        # ----------------------------------------------------
        # FORMAT NEWS RESULTS
        # ----------------------------------------------------

        output = []

        if is_news_query:

            output.append(
                "CURRENT NEWS SEARCH RESULTS"
            )

            output.append(
                "These are recent search results. "
                "Use the title, source, date and summary "
                "to answer the user's question."
            )

            output.append("")

            for i, result in enumerate(
                results,
                start=1
            ):

                title = (
                    result.get("title")
                    or "No title"
                )

                body = (
                    result.get("body")
                    or result.get("excerpt")
                    or "No summary available."
                )

                url = (
                    result.get("url")
                    or result.get("href")
                    or ""
                )

                source = (
                    result.get("source")
                    or "Unknown source"
                )

                date = (
                    result.get("date")
                    or "Date unavailable"
                )

                output.append(
                    f"NEWS {i}\n"
                    f"Headline: {title}\n"
                    f"Source: {source}\n"
                    f"Date: {date}\n"
                    f"Details: {body}\n"
                    f"URL: {url}\n"
                )

        # ----------------------------------------------------
        # FORMAT NORMAL SEARCH RESULTS
        # ----------------------------------------------------

        else:

            output.append(
                "WEB SEARCH RESULTS"
            )

            output.append("")

            for i, result in enumerate(
                results,
                start=1
            ):

                title = (
                    result.get("title")
                    or "No title"
                )

                body = (
                    result.get("body")
                    or "No summary available."
                )

                href = (
                    result.get("href")
                    or result.get("url")
                    or ""
                )

                output.append(
                    f"RESULT {i}\n"
                    f"Title: {title}\n"
                    f"Details: {body}\n"
                    f"URL: {href}\n"
                )

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        final_result = "\n".join(output)

        print("=" * 60)
        print("WEB SEARCH SUCCESS")
        print(f"Results found: {len(results)}")
        print("=" * 60)

        return final_result

    except Exception as e:

        print("=" * 60)
        print("WEB SEARCH ERROR")
        print(f"Error: {repr(e)}")
        print("=" * 60)

        return (
            "Sorry, I could not access live web information "
            "right now."
        )