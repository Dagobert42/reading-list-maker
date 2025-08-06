# Reading List Maker

Reading List Maker lets you search multiple paper outlets via their python APIs using a set of keywords. Subsequently, results can be filtered and annotated using an LLM-based reviewing process. The method is intended to curate comprehensive yet targeted reading lists for survey papers using a semi-automatic, human-guided approach.

So far the following sources have been implemented:

- ACL Anthology via [acl-anthology](https://github.com/acl-org/acl-anthology)
- arXiv via [arxiv](https://github.com/lukasschwab/arxiv.py)
- Crossref via [crossref-commons](https://gitlab.com/crossref/crossref_commons_py)
- Google Scholar via [scholarly](https://github.com/scholarly-python-package/scholarly) (⚠️ currently unreliable)
- OpenAlex via [pyalex](https://github.com/J535D165/pyalex)
- ScienceDirect via [pybliometrics](https://github.com/pybliometrics-dev/pybliometrics)
- Scopus via [pybliometrics](https://github.com/pybliometrics-dev/pybliometrics)
- Semantic Scholar via [semanticscholar](https://github.com/danielnsilva/semanticscholar)


## Install
```
git clone https://github.com/Dagobert42/reading-list-maker.git
cd reading-list-maker
pip install -r requirements.txt
```

## Usage

### 1. Get some API keys
You can get required API keys from:

- [Academic Cloud](https://kisski.gwdg.de/en/leistungen/2-02-llm-service/) to perform LLM-based filtering and review of papers, if you don't want to filter or annotate papers using LLMs you can elect to use only the search functionalities
- [Elsevier](https://dev.elsevier.com/apikey/manage) to search ScienceDirect and Scopus via pybliometrics
- [Semantic Scholar](https://www.semanticscholar.org/product/api#api-key-form) OPTIONAL but recommended to search Semantic Scholar, WARNING the application form may not be accessible through Firefox, try a different browser

### 2. OPTIONAL: Define a list of gold paper titles
If you have already performed a small manual search you can optionally define a list of gold papers to see how many of them are retrieved in the automated search. These titles will be compared in lower case to the found paper titles. The intent is just to get an initial idea of the usefulness of your keywords, provided you already have identified interesting titles.

gold_papers.txt should look like this:
```
Analyzing Mis/Disinformation: UnderstandingSwiss COVID-19 Narratives Through NLP Analysis
Identifying Conspiracy Theories News based on Event Relation Graph
Recontextualized Knowledge and Narrative Coalitions on Telegram
```

### 3. Open and read `main.ipynb`

`main.ipynb` walks you through how to perform the search and annotation process. You can modify this file to your needs!

Results will get saved to the `/results` folder in CSV format. It is therefore recommended to use a program that can visualize CSV files nicely when working with the results. Although the process is mostly automated it will likely be necessary to frequently screen intermediary results.
