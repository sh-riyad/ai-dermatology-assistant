from langchain_tavily import TavilySearch

tavily= TavilySearch(max_results=2,
                     topic="general",
                     # include_answer=False,
                     # include_raw_content=False,
                     # include_images=False,
                     # include_image_descriptions=False,
                     # search_depth="basic",
                     # time_range="day",
                     # include_domains=None,
                     # exclude_domains=None
                    )