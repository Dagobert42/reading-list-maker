from pybliometrics.sciencedirect import ArticleMetadata
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm


def search_sciencedirect(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None,
    ):
    """
    Performs keyword-based searches on ScienceDirect.
    """
    
    sciencedirect_results = []
    for keyword in tqdm(keywords, desc="Searching ScienceDirect..."):
        try:
            search = ArticleMetadata(
                query=f'TITLE("{keyword}") OR ABS("{keyword}") OR KEY("{keyword}")',
                download=True,
                subscriber=True
            )
        except Exception as e:
            print(e)
            continue

        if not search.results:
            continue

        for paper in search.results[:min(max_results, len(search.results))]:
            title = getattr(paper, 'title', None)
            abstract = getattr(paper, 'abstract_text', None)
            link = getattr(paper, 'link', None)

            if not all([title, abstract, link]):
                continue

            date = getattr(paper, "coverDate", None)
            year = int(date.split("-")[0]) if date else 0
            if year < min_year:
                continue
                
            if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                continue

            sciencedirect_results.append({
                "title": title,
                "authors": getattr(paper, 'authors', []),
                "doi": getattr(paper, 'doi', ''),
                "abstract": abstract,
                "url": link,
                "year": year,
                "source": "sciencedirect",
            })

    print(f"Found {len(sciencedirect_results)} candidate papers\n")
    add_to_all_results(sciencedirect_results, seen_keys, all_results, gold_titles)
