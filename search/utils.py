import os
import pybliometrics

def setup_elsevier_api(api_key_path: str):
    if api_key_path and os.path.exists(api_key_path):
        with open(api_key_path) as f:
            key = f.read().strip()
            pybliometrics.init(keys=[key])
    else:
        print("WARNING: No Elsevier API key (required to search Scopus and ScienceDirect)")


def contains_any_substring(text: str, substrings: list[str]) -> bool:
    return any(sub in text for sub in substrings)


def is_relevant(title: str, abstract: str, relevance_terms: list[list[str]]) -> bool:
    """
    Implements our master bool query in a str search by checking
    if a paper's title and abstract contain at least one term
    from each group in relevance terms.
    
    Returns True if all groups are matched.
    """
    search_space = f"{title.lower()} {abstract.lower()}"
    
    return all(
        contains_any_substring(search_space, term_list)
        for term_list in relevance_terms
        )


def init_gold_titles(gold_titles_path: str="gold_papers.txt"):
    try:
        with open(gold_titles_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    except:
        print("WARNING Could not instantiate gold titles. Continuing without...")
        return None
    

def nr_gold_papers_found(search_result_titles: list[str], gold_titles: list[str], verbose=False):
    """
    If gold paper titles are specified, this function checks how many of them
    are present in the given search results.
    """
    result_titles = [paper['title'].replace("\n", " ").strip() for paper in search_result_titles]

    match_count = 0
    for gold_title in gold_titles:
        found = False
        gold_title = gold_title.lower()
        for result_title in result_titles:
            if result_title == "":
                print(f"WARNING: Empty title str in results.")
                continue
            result_title = result_title.lower()
            if gold_title in result_title or result_title in gold_title:
                match_count += 1
                found = True
                break
        if verbose and not found:
            print(f"Not found: {gold_title}")

    print(f"Gold papers found in this search: {match_count}")


def add_to_all_results(new_results: list[dict], seen_titles: set[str], all_results: list[dict], gold_titles: list[str]=None):
    """
    Adds new results (whose titles are not in seen titles) from a search to all results.
    """
    added = 0
    temp_results = []
    for paper in new_results:
        title = paper.get("title", "").lower()
        if title == "":
            print(f"WARNING: Empty title str in results.")
            continue
    
        if title not in seen_titles:
            seen_titles.add(title)
            temp_results.append(paper)
            added += 1
            if added < 4:
                print(f"Added: {paper['title']}")
            elif added == 4:
                print(f"Adding more...")
    all_results.extend(temp_results)
    if gold_titles:
        nr_gold_papers_found(temp_results, gold_titles)
    print(f"Added {len(temp_results)} new papers\n")


def reconstruct_inverted_abstract(abstract_inverted_index: dict) -> str:
    """
    Used to reconstruct abstracts from Open Alex which are presented 
    in inverted index form for legal reasons.
    """
    if not abstract_inverted_index:
        return ""

    max_index = max(pos for positions in abstract_inverted_index.values() for pos in positions)
    words = [""] * (max_index + 1)
    for word, positions in abstract_inverted_index.items():
        for pos in positions:
            words[pos] = word

    return " ".join(words)
