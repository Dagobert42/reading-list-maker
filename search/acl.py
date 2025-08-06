from acl_anthology import Anthology
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm


def search_acl_anthology(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        gold_titles:list[str]=None
        ):
    """
    Searching ACL Anthology works a little differently. There is no API-based search.
    The client object presents all papers (>100.000) with metadata (do not ask me how).
    We can perform keyword matching directly on all titles and abstracts.
    """
    def contains_keywords(search_text: str, keywords: list[str]):
        search_text = search_text.lower()
        for keyword in keywords:
            words = keyword.lower().split()
            if all(word in search_text for word in words):
                return True
        return False
    acl_client = Anthology.from_repo()

    acl_results = []
    for paper in tqdm(acl_client.papers(), desc="Searching ACL Anthology..."):
        if not all([paper.pdf, paper.abstract, paper.pdf and paper.pdf.url]):
            continue

        year = int(paper.year) or 0
        if year < min_year:
            continue

        title = str(paper.title)
        abstract = str(paper.abstract)

        if not contains_keywords(f"{title} {abstract}", keywords):
            continue

        if relevance_terms and not is_relevant(title, abstract, relevance_terms):
            continue

        acl_results.append({
            "title": title,
            "authors": [a.name for a in paper.authors],
            "doi": paper.doi or "",
            "abstract": abstract,
            "url": paper.pdf.url,
            "year": year,
            "source": "acl_anthology"
        })

    print(f"Found {len(acl_results)} candidate papers\n")
    add_to_all_results(acl_results, seen_keys, all_results, gold_titles)
