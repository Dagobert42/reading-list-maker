from semanticscholar import SemanticScholar
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm
from time import sleep


def search_semanticscholar(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        semanticscholar_api_key_path:str,
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None,
    ):
    """
    Performs keyword-based searches on Semantic Scholar.
    """
    try:
        with open(semanticscholar_api_key_path) as f:
            semanticscholar_api_key = f.readline().strip()
    except:
        print("Could not find Semantic Scholar API key (recommended). Continuing without...")
        semanticscholar_api_key = None
    semanticscholar_client = SemanticScholar(api_key=semanticscholar_api_key, timeout=10)

    semanticscholar_results = []
    for keyword in tqdm(keywords, desc="Searching Semantic Scholar..."):
        try:
            search = semanticscholar_client.search_paper(
                query=keyword,
                fields=["title", "authors", "abstract", "year", "paperId", "citationCount", "externalIds"]
            )

            for paper in search[:min(max_results, search.total)]:
                title = getattr(paper, 'title', None)
                abstract = getattr(paper, 'abstract', None)
                doi = paper.externalIds.get('DOI', None) if hasattr(paper, 'externalIds') else None

                if not all([title, abstract, doi]):
                    continue

                year = getattr(paper, "year", None)
                year = int(year) if year else None
                if not year or year < min_year:
                    continue

                if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                    continue
                
                semanticscholar_results.append({
                    "title": title,
                    "authors": [a.name for a in paper.authors] if hasattr(paper, 'authors') else [],
                    "doi": doi,
                    "abstract": abstract,
                    "url": f"https://doi.org/{doi}",
                    "year": year,
                    "source": "semanticscholar",
                })

        except Exception as e:
            print(f"Error searching '{keyword}': {e}")
            continue

        # Enforce rate limiting
        sleep(1)

    print(f"Found {len(semanticscholar_results)} candidate papers\n")
    add_to_all_results(semanticscholar_results, seen_keys, all_results, gold_titles)
