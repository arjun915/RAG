# from gpt4all import GPT4All
# from config import Config
# from pathlib import Path
# import os
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class LocalLLMService:
#     def __init__(self):
#         # Convert to absolute path (Windows-compatible)
#         self.model_path = Path(Config.LOCAL_LLM_PATH) / Config.LOCAL_LLM_MODEL
#         self.model_path = str(self.model_path.absolute())

#         # Verify file exists with exact name
#         if not Path(self.model_path).exists():
#             available_files = os.listdir(Path(Config.LOCAL_LLM_PATH))
#             raise FileNotFoundError(
#                 f"Model file '{Config.LOCAL_LLM_MODEL}' not found.\n"
#                 f"Folder contents: {available_files}\n"
#                 f"Expected path: {self.model_path}"
#             )

#         # Initialize model
#         self.model = GPT4All(
#             model_name=Config.LOCAL_LLM_MODEL,
#             model_path=Config.LOCAL_LLM_PATH,
#             allow_download=False  # Critical to prevent auto-downloads
#         )
#         logger.info(f"Successfully loaded: {self.model_path}")

#     def generate_response(self, query: str, context: list) -> str:
#         prompt = self._build_prompt(query, context)
#         try:
#             with self.model.chat_session():
#                 response = self.model.generate(
#                     prompt=prompt,
#                     max_tokens=256,
#                     temp=0.7
#                 )
#             return response.strip()
#         except Exception as e:
#             logger.error(f"Generation error: {str(e)}")
#             return "Sorry, I couldn't process that request."

#     def _build_prompt(self, query: str, context: list) -> str:
#         context_str = "\n".join([doc['content'] for doc in context])
#         return f"""Answer ONLY using this context:

# Context:
# {context_str}

# Question: {query}

# Answer (short and precise):"""
import openai
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalLLMService:
    def __init__(self):
        try:
            openai.api_key = Config.TOGETHER_AI_API_KEY
            openai.api_base = "https://api.together.xyz"  # no `/v1` in this version
            self.model = "mistralai/Mistral-7B-Instruct-v0.1"  # e.g., "mistralai/Mistral-7B-Instruct-v0.1"
            logger.info(f"Using Together AI model: {self.model}")

        except Exception as e:
            logger.error(f"Failed to initialize Together AI model: {str(e)}")
            raise

    def generate_response(self, query: str, context: list) -> str:
        prompt = self._build_prompt(query, context)

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an assistant answering user questions using context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=256,
                temperature=0.7
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return "Sorry, there was an issue generating a response."

    def _build_prompt(self, query: str, context: list) -> str:
        context_str = "\n".join([doc['content'] for doc in context])
        return f"Context:\n{context_str}\n\nQuestion: {query}\nAnswer:"
