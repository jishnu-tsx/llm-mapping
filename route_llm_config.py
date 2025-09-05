from routellm.controller import Controller

client = Controller(
    routers=["mf"],  # e.g., use the "matrix factorization" router
    strong_model="openai/gpt-4",
    weak_model="anyscale/mistralai/Mixtral-8x7B-Instruct-v0.1",
)


class LLMRouter:
    def __init__(self):
        self.client = Controller(
            routers=["mf"],
            strong_model="google/gemini-2.5-flash",
            weak_model="google/gemini-1.5-flash",
            config="config.yaml",
        )

    def generate_content(self, inputs):
        """
        Send content to RouteLLM, which decides whether to use
        Gemini 2.5-flash (strong) or 1.5-flash (weak).
        """
        response = self.client.completion(
            model="router-mf-0.1159",  # router alias
            messages=[{"role": "user", "content": inputs}],
        )
        return response["choices"][0]["message"]["content"]
