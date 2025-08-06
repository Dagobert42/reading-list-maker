from scholarly import scholarly, ProxyGenerator
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm

def search_scholar(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None
    ):
    """
    Was out of order (server side errors) at the time of writing.
    Kudos to you if you can make it work. Use at your own discretion.
    """
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)

    scholar_results = []
    for keyword in tqdm(keywords, desc="Searching Google Scholar..."):
        search_query = scholarly.search_pubs(keyword, year_low=min_year)

        for _ in range(max_results):
            try:
                pub = next(search_query)
            except Exception as e:
                print(f"Searching {keyword} interrupted: {e}")
                break

            bib = pub.get('bib', {})
            title = bib.get('title', '')
            abstract = bib.get('abstract', '') or ''
            year_str = bib.get('pub_year', 0)

            try:
                year = int(year_str)
            except (ValueError, TypeError):
                continue

            if year < min_year:
                continue

            if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                continue
            
            scholar_results.append({
                "title": title,
                "authors": bib.get('author', ''),
                "doi": bib.get('doi', ''),
                "abstract": abstract,
                "year": year,
                "source": "scholarly"
            })

    print(f"Found {len(scholar_results)} candidate papers\n")
    add_to_all_results(scholar_results, seen_keys, all_results, gold_titles)
