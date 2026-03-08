import os
from supabase import create_client
import google.generativeai as genai

# Config (Lấy từ .env của bạn)
SUPABASE_URL = "..."
SUPABASE_KEY = "..." # Service Role Key
GEMINI_API_KEY = "..."

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def embed_text(text):
    return genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document"
    )['embedding']

def main():
    # Đọc file (Giả lập việc đọc Markdown)
    quotes = [
        {"author": "Steve Jobs", "content": "Hãy cứ khát khao, hãy cứ dại khờ."},
        {"author": "Thomas Edison", "content": "Tôi không thất bại. Tôi chỉ tìm ra 10000 cách sai."},
        # ... thêm vài câu nữa
    ]

    for q in quotes:
        print(f"Đang xử lý: {q['author']}...")
        vector = embed_text(q['content'])
        
        data = {
            "author": q['author'],
            "content": q['content'],
            "embedding": vector
        }
        supabase.table("quotes").insert(data).execute()

if __name__ == "__main__":
    main()
 
