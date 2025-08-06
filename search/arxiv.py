import arxiv
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm


def search_arxiv(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None
        ):
    """
    Performs keyword-based searches on arxiv.
    """

    arxiv_results = []
    for keyword in tqdm(keywords, desc="Searching arXiv..."):
        arxiv_results = []
        search = arxiv.Search(
            query=f"all:{keyword}",
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        try:
            for paper in arxiv.Client().results(search):
                if paper.published.year < min_year:
                    continue

                title = str(paper.title)
                abstract = str(paper.summary).replace("\n", " ")

                if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                    continue
                
                arxiv_results.append({
                    "title": title,
                    "authors": [str(a) for a in paper.authors],
                    "doi": paper.doi or "",
                    "abstract": paper.summary,
                    "url": paper.pdf_url,
                    "year": paper.published.year,
                    "source": "arxiv"
                })

        except Exception as e:
            print(e)
            continue

    print(f"Found {len(arxiv_results)} candidate papers\n")
    add_to_all_results(arxiv_results, seen_keys, all_results, gold_titles)
