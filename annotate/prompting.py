from tqdm import tqdm
from pandas import DataFrame, Series
from typing import Callable, Optional
from openai import RateLimitError
from academiccloud_api import OpenAIClient, extract_json

def annotate_df(
    df: DataFrame,
    client: OpenAIClient,
    model: str,
    prompt_fn: Callable,
    get_prompt_args: Callable,
    start: int = 0,
    end: int = None
) -> DataFrame:
    """
    Generic paper annotation using a user-defined prompt strategy.

        df:               DataFrame of papers
        client:           facilitates API access given a valid key
        model:            identifier of the model to query
        prompt_fn:        generates messages to prompt the model
        get_prompt_args:  returns the required arguments for `prompt_fn` from the rows of the df
        start:            optional index for continued annotation after encountering an error
        end:              optional index for continued annotation after encountering an error

    Returns the DataFrame with the new annotations added for each row.
    """
    end = min(end, len(df)) if end is not None else len(df)

    for i, row in tqdm(df[start:end].iterrows(), desc="Annotating papers...", total=end-start):
        if row.get('requires reannotation') is False:
            continue

        try:
            args = get_prompt_args(row)
            messages = prompt_fn(*args)
            response = client.prompt_model(messages, model)
            response_list = extract_json(response)

            for entry in response_list:
                for key, value in entry.items():
                    if isinstance(value, str):
                        df.loc[i, key] = value
                    elif isinstance(value, list):
                        df.loc[i, key] = ",\n".join(value)

        except RateLimitError as e:
            print(f"{e}.\nStopping early at index {i}. Resume later when rate limit resets.")
            break

        except Exception as e:
            print(f"Error processing row {i}: {e}")
            df.loc[i, "requires reannotation"] = True
            continue

        df.loc[i, "requires reannotation"] = False
    return df

############# String definitions for prompting #############
# Edit these to fit your search and annotation 

SYSTEM_PROMPT = (
        "You are an expert researcher in computational social science "
        "with experience in narrative analysis, disinformation, and NLP."
    )

GENERAL_INSTRUCTIONS = """If you answer "No" to any question enter an empty string "" in the accompanying field.
Return only a single, valid JSON object in ANSWER FORMAT (no comments, no trailing commas, use double quotes).
Mark the final output JSON object with ```json```.
"""

############# Prompt for abstract-based paper filter #############

def get_screening_prompt(title:str, abstract: str) -> list[dict]:
    """
    Builds a prompt for title and abstract based screening of a paper.

    Refactor this prompt for your needs!
    """
    user_prompt = f"""INSTRUCTIONS
Read the abstract below and answer the numbered questions.
{GENERAL_INSTRUCTIONS}

TITLE
{title}

ABSTRACT
{abstract}

QUESTIONS

1. Is the paper a system description for a shared task submission?
If "Yes", stop your analysis and enter an empty string "" for remaining answers.

2. Is the paper itself a survey paper?
If "Yes", stop your analysis and enter an empty string "" for remaining answers.

3. Does the paper study any disinformation-related concept(s)?
If "No", stop your analysis and enter an empty string "" for remaining answers.

4. Does the paper study disinformation narratives or the use of narratives in the context of disinformation?
If "Yes", quote the respective section.

5. Does the paper present any computational task(s)?

6. Does the paper apply any computational method(s)?

7. Does the paper introduce or use dataset(s) and what is the domain or topic of the data?

8. Does the abstract mention any of the following additional concepts: Multi-modal Data, Explainability, Interpretability, Interpretation Techniques?

ANSWER FORMAT

```json
[
  {{
    "shared task": "Yes|No",
  }},
  {{
    "survey": "Yes|No",
  }},
  {{
    "disinformation focused": "Yes|No",
    "disinformation topics": ["Fake News", "Propaganda", "Conspiracy Theories", ...]
  }},
  {{
    "narrative focused": "Yes|No",
    "indicative quote": "..."
  }},
  {{
    "tasks present": "Yes|No",
    "tasks": ["Narrative Classification", "Fact-Checking", "Stance Detection", ...]
  }},
  {{
    "methods present": "Yes|No",
    "methods": ["Retrieval Augmented Generation", "Clustering", "Graph-based Analysis", ...],
  }},
  {{
    "datasets present": "Yes|No",
    "domains": ["COVID-19 Twitter posts", "Russia-Ukraine War Telegram messages", "Climate Change news articles", ...],
  }},
  {{
    "additional concepts present": "Yes|No",
    "additional concepts": ["Multi-modal Data", "Explainability", "Interpretability", ...],
  }}
]
```"""
    
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]


############# Prompt for full text information extraction #############


def get_review_prompt(full_paper: str, disinfo_topics: str) -> list[dict]:
    """
    Builds a prompt for full text information extraction on a paper.
    The full paper is a str representing markdown which is converted from
    the original paper pdf. So title, abstract, contents should be included automatically.

    Refactor this prompt for your needs!
    """
    disinfo_topics_str = ','.join(
        disinfo_topics[:-1]) + (' and' + disinfo_topics[-1]
        if len(disinfo_topics) > 1 else disinfo_topics[0]
        )
    user_prompt = f"""INSTRUCTIONS
Read and summarize the paper below by answering the numbered questions.
{GENERAL_INSTRUCTIONS}

PAPER
{full_paper}

QUESTIONS

1. Research Questions
Which explicit research questions does the paper formulate ?
If "Yes", quote them.

2. Results and Findings
What are the concrete results or findings reported in the paper?

3. Evaluation
Which evaluation methods and/or metrics are mentioned (e.g. F1 score, human annotation, qualitative analysis)?

4. Future Work
Which future research directions or open questions are outlined?

5. Disinformation Understanding
The paper is concerned with {disinfo_topics_str}. Does the paper present any definition(s) for {'these concepts' if len(disinfo_topics)>1 else 'this concept'}?
If "Yes", quote the relevant sections.

6. Narrative Definitions
Does the paper include explicit definitions or conceptualizations of narratives in the context of disinformation?
If "Yes", quote the definition(s) or definitional statements.

7. Narrative Features
Does the paper make any statements about properties, characteristics, or features of narratives?
If "Yes", quote the statements.

8. Models Used
Does the paper employ neural models (e.g. BERT, GPT, LSTM)?
If "Yes", specify the model(s).

9. Languages
Does the paper specify the language(s) of the data?
If "Yes", list the language(s).

10. Target Group
Does the paper identify specific target groups of the disinformation (e.g. ethnic minorities, political followers, general public)?
If "Yes", specify the group(s).

11. Data Perspective
Does the paper indicate whose perspective the data reflects (e.g. a specific regime, social media users, third-party observers)?
If "Yes", describe the perspective(s).

12. Modalities
Does the paper analyze or use multi-modal data (e.g. text, images, video, audio)?
If "Yes", list all data modalities mentioned.

ANSWER FORMAT

```json
[
  {{
    "research questions": ["..."]
  }},
  {{
    "findings": ["..."]
  }},
  {{
    "evaluation methods": ["..."]
  }},
  {{
    "future work": ["..."]
  }},
  {{
    "disinfo definitions present": "Yes|No",
    "disinfo definitions": ["..."]
  }},
  {{
    "narrative definitions present": "Yes|No",
    "narrative definitions": ["..."]
  }},
  {{
    "narrative properties stated": "Yes|No",
    "narrative properties statements": ["..."]
  }},
  {{
    "neural models used": "Yes|No",
    "models": ["..."]
  }},
  {{
    "languages specified": "Yes|No",
    "languages": ["..."]
  }},
  {{
    "target group specified": "Yes|No",
    "target groups": ["..."]
  }},
  {{
    "data perspective specified": "Yes|No",
    "perspectives": ["..."]
  }},
  {{
    "modalities specified": "Yes|No",
    "modalities": ["Text", "Image", "Video", "Audio", ...]
  }}
]
```"""
    
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    