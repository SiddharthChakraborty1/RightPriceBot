import ollama

from ai_utils.context_generators import DefaultContextGenerator


class AIManager(DefaultContextGenerator):
    
    def __init__(self, model_name: str):
        self.model = model_name
    
    
    def get_response(self, prompt: str):
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": f"context: {self.basic_context}, The question is {prompt}"}]
        )
        if not (returned_message := response.get("message", {}).get("content", 0)):
            return "We might not know the answer for this but we'll notify if the price drops"
        
        return returned_message
    
    def get_streaming_responses(self, prompt: str):
        stream = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            yield chunk.get("message", {}).get("content", "")
       