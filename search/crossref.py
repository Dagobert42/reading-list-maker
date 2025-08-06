from crossref_commons.iteration import iterate_publications_as_json
from .utils import is_relevant, add_to_all_results
from tqdm import tqdm
import re


def search_crossref(
        keywords: list[str],
        seen_keys: list[str],
        all_results: list[dict],
        relevance_terms: list[list[str]]=None,
        min_year: int=0,
        max_results: int=100,
        gold_titles:list[str]=None
    ):
    """
    Performs keyword-based searches on Crossref.
    """

    crossref_results = []
    for keyword in tqdm(keywords, desc="Searching Crossref..."):
        iter = iterate_publications_as_json(
            max_results=max_results,
            queries={'query.bibliographic': keyword},
            filter={"has-full-text": "true"}
        )

        while True:
            try:
                paper = next(iter)
            except ConnectionError as e:
                print(f"{e} searching {keyword}")
                continue
            except StopIteration:
                break

            year = paper.get("issued", {}).get("date-parts", [[None]])[0][0]
            if year is None or year < min_year:
                continue

            title = (paper.get("title", [""])[0] or "")
            raw_abstract = paper.get("abstract", "")
            match = re.search(r"<jats:p>(.*?)</jats:p>", raw_abstract or "", re.DOTALL)
            abstract = (match.group(1).strip() if match else None)
            url = paper.get("link", "")[0].get("URL", None)

            if not all([title, abstract, url]):
                continue
                
            if relevance_terms and not is_relevant(title, abstract, relevance_terms):
                continue

            crossref_results.append({
                "title": title,
                "authors": [
                    " ".join(filter(None, [a.get("given", ""), a.get("family", "")]))
                    for a in paper.get("author", [])
                ],
                "doi": paper.get("DOI", ""),
                "abstract": abstract,
                "url": url,
                "year": year,
                "source": "crossref"
            })

    print(f"Found {len(crossref_results)} candidate papers\n")
    add_to_all_results(crossref_results, seen_keys, all_results, gold_titles)
