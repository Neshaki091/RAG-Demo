import os
import google.generativeai as genai
from supabase import create_client, Client

# --- CẤU HÌNH ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATA_FILE = "data/quotes.md" # Đường dẫn đến file chứa toàn bộ danh ngôn

if not SUPABASE_URL or not GEMINI_API_KEY:
    raise ValueError("❌ Lỗi: Chưa cấu hình Secrets (Environment Variables)!")

# Setup Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text):
    try:
        clean_text = text.replace("\n", " ").strip()
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=clean_text,
            task_type="retrieval_document",
            title="Mood Quote"
        )
        return result['embedding']
    except Exception as e:
        print(f"⚠️ Lỗi embedding: {e}")
        return None

def parse_markdown_file(filepath):
    """
    Hàm này đọc file MD và tách thành list các dict:
    [{'author': 'Steve Jobs', 'content': '...'}, ...]
    """
    quotes_list = []
    current_author = None
    current_content = []

    if not os.path.exists(filepath):
        print(f"❌ Không tìm thấy file: {filepath}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        
        # Nếu dòng bắt đầu bằng # -> Đây là Tác giả
        if line.startswith("#"):
            # Lưu người trước đó lại (nếu có)
            if current_author and current_content:
                quotes_list.append({
                    "author": current_author,
                    "content": " ".join(current_content)
                })
            
            # Bắt đầu người mới (Xóa dấu # đi)
            current_author = line.lstrip("#").strip()
            current_content = [] # Reset nội dung
            
        # Nếu dòng có chữ (và không phải tiêu đề) -> Đây là Nội dung
        elif line:
            current_content.append(line)

    # Đừng quên lưu người cuối cùng sau khi hết vòng lặp
    if current_author and current_content:
        quotes_list.append({
            "author": current_author,
            "content": " ".join(current_content)
        })

    return quotes_list

def main():
    print(f"🚀 Đang đọc file tổng hợp '{DATA_FILE}'...")
    
    quotes = parse_markdown_file(DATA_FILE)
    print(f"-> Tìm thấy {len(quotes)} câu danh ngôn.")

    success_count = 0
    
    for q in quotes:
        try:
            print(f"🔄 Đang xử lý: {q['author']}...")

            # 1. Tạo Vector
            vector = get_embedding(q['content'])
            if not vector: continue

            # 2. Chuẩn bị data
            data = {
                "author": q['author'],
                "content": q['content'],
                "embedding": vector
            }

            # 3. Gửi lên Supabase
            supabase.table("quotes").insert(data).execute()
            success_count += 1
            print(f"✅ Đã lưu xong.")

        except Exception as e:
            print(f"❌ Lỗi câu của {q['author']}: {e}")

    print(f"\n🎉 TỔNG KẾT: Đã nạp thành công {success_count} câu danh ngôn.")

if __name__ == "__main__":
    main()
