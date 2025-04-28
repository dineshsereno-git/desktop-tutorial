"""
Gemini integration module for generating summaries and comments.
"""

from google.generativeai import configure, GenerativeModel

# Gemini Pro config
configure(api_key="edit the key here")
model = GenerativeModel(model_name="gemini-1.5-pro-latest")

def summarize_reviews(reviews):
    prompt = "Summarize these user reviews into 3 key points:\n" + "\n".join(reviews)
    response = model.generate_content(prompt)
    return response.text.strip()   # strip removes all un-necessary white spaces.. 

def generate_comment(summary):
    prompt = f"Write a short, friendly comment about a product based on this summary:\n{summary}"
    response = model.generate_content(prompt)
    return response.text.strip()
