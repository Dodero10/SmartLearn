import os
from dotenv import load_dotenv
from openai import OpenAI


class ChatGPTGen:
    def __init__(self):
        load_dotenv()

        self.open_api_key = os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.open_api_key)
        self.model = os.environ.get('OPENAI_MODEL')

    def default_chat_completion(self, messages: [], token_output=4085) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=token_output
        )
        return completion.choices[0].message.content

    def stream_chat_completion(self, messages: []):

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content