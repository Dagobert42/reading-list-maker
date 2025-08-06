from openai import OpenAI
import json
from httpx import Timeout
from typing import Any

class OpenAIClient:
    def __init__(self, api_key_path: str, timeout: Timeout=Timeout(600.0, read=200.0, write=400.0, connect=3.0)):
        """
        Initialize the OpenAI client with API key and base URL.
        Hand different timeout parameters for larger queries/models.
        """
        with open(api_key_path, "r") as f:
            api_key = f.read().strip()
        base_url = "https://chat-ai.academiccloud.de/v1"

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    def prompt_model(self, messages: list[dict], model: str, stream: bool=False) -> str:
        """
        Prompt a model on the academic cloud. Response can be streamed.
        """
        if stream:
            print("Streaming response...", flush=True)
            final_response = ""
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                final_response += content
            print("\n[End of stream]")
            return final_response
        else:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model
            )
            return response.choices[0].message.content


def extract_json(response_text: str) -> Any:
    """
    Extract JSON content from the response, removing any reasoning or thinking.
    Expecting reasoning content to be marked as   <think> ... </think>
    Expecting JSON content to be marked as        ```json ... ```
    """

    reasoning_end = response_text.find('</think>')
    pure_response = response_text[max(reasoning_end, 0):]

    start = pure_response.find('```json')
    end = pure_response.rfind('```')
    json_part = pure_response[start:end].strip('```json').strip()

    return json.loads(json_part)
