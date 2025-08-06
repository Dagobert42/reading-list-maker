from pybliometrics.scopus import ScopusSearch
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm


def search_scopus(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None
    ):
    """
    Performs keyword-based searches on Scopus.
    """
    
    scopus_results = []
    for keyword in tqdm(keywords, desc="Searching Scopus..."):
        try:
            search = ScopusSearch(
                query=f'TITLE-ABS-KEY("{keyword}")',
                download=True,
                subscriber=True
            )
            if not search.results:
                continue
        except Exception as e:
            print(e)
            continue

        for paper in search.results[:min(max_results, len(search.results))]:
            title = getattr(paper, 'title', None)
            abstract = getattr(paper, 'description', None)
            doi = getattr(paper, 'doi', None)

            if not all([title, abstract, doi]):
                continue

            date = getattr(paper, "coverDate", None)
            year = int(date.split("-")[0]) if date else 0
            if year < min_year:
                continue

            if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                continue
            
            scopus_results.append({
                "title": title,
                "authors": getattr(paper, 'author_names', ''),
                "doi": doi,
                "abstract": abstract,
                "url": f"https://doi.org/{doi}",
                "year": year,
                "source": "scopus",
            })

    print(f"Found {len(scopus_results)} candidate papers\n")
    add_to_all_results(scopus_results, seen_keys, all_results, gold_titles)
