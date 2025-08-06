import pyalex
from pyalex import Works as PyAlexWorks
from .utils import (
    is_relevant,
    add_to_all_results,
    reconstruct_inverted_abstract
    )
from tqdm import tqdm

def search_openalex(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None,
        email: str=None,
    ):
    """
    Performs keyword-based searches on OpenAlex.
    """
    # Set email for API etiquette
    if email:
        pyalex.config.email = email

    openalex_results = []
    for keyword in tqdm(keywords, desc="Searching OpenAlex..."):
        works = PyAlexWorks() \
            .search(keyword) \
            .filter(publication_year=f">{min_year - 1}") \
            .sort(cited_by_count="desc") \
            .get(per_page=max_results)

        for work in works:
            doi = work.get("doi", None)
            title = work.get("title", None)
            raw_abstract = work.get("abstract", None)

            # Handle OpenAlex abstract inversion
            abstract = raw_abstract if raw_abstract and len(raw_abstract) > 5 \
                else reconstruct_inverted_abstract(work.get("abstract_inverted_index", {}))

            if not all([doi, title, abstract]):
                continue

            year = work.get("publication_year", 0)
            if year < min_year:
                continue

            if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                    continue
            
            openalex_results.append({
                "title": title,
                "authors": [a["author"]["display_name"] for a in work.get("authorships", [])],
                "doi": doi,
                "abstract": abstract,
                "url": doi,
                "year": year,
                "source": "openalex",
            })

    print(f"Found {len(openalex_results)} candidate papers\n")
    add_to_all_results(openalex_results, seen_keys, all_results, gold_titles)
