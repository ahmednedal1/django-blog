from openai import OpenAI


class ContentClient:
    def __init__(self, api_key, model):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_content(self, prompt, system=None):

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    # Task 3 uses the same client as the existing content-generation feature.
    def generate(self, prompt):
        return self.generate_content(prompt)
