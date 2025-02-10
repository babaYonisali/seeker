from openai import OpenAI

class DeepSeekAPI:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

    async def generate_response(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",  # This will use DeepSeek-V3
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}") 