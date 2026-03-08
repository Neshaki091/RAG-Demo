import os
import glob
import google.generativeai as genai
from supabase import create_client, Client

# --- CẤU HÌNH ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATA_FOLDER = "data"  # Tên thư mục chứa file dữ liệu

if not SUPABASE_URL or not GEMINI_API_KEY:
    raise ValueError("❌ Lỗi: Chưa cấu hình Secrets (Environment Variables)!")

# Setup Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

def get_embedding(text):
    try:
        # Xử lý text: Xóa khoảng trắng thừa và xuống dòng
        clean_text = text.replace("\n", " ").strip()
        if not clean_text: return None

        result = genai.embed_content(
            model="models/text-embedding-004",
            content=clean_text,
            task_type="retrieval_document",
            title="Mood Quote"
        )
        return result['embedding']
    except Exception as e:
        print(f"⚠️ Lỗi khi tạo vector: {e}")
        return None

def main():
    print(f"🚀 Đang quét thư mục '{DATA_FOLDER}'...")
    
    # Tìm tất cả file .txt trong thư mục data
    # Bạn có thể đổi "*.txt" thành "*.md" nếu muốn dùng Markdown
    files = glob.glob(os.path.join(DATA_FOLDER, "*.txt"))

    if not files:
        print(f"⚠️ Không tìm thấy file .txt nào trong thư mục '{DATA_FOLDER}'!")
        return

    success_count = 0
    
    for file_path in files:
        try:
            # 1. Lấy tên tác giả từ tên file (Ví dụ: "data/Steve Jobs.txt" -> "Steve Jobs")
            filename = os.path.basename(file_path)
            author_name = os.path.splitext(filename)[0]

            # 2. Đọc nội dung file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                print(f"⏩ Bỏ qua file rỗng: {filename}")
                continue

            print(f"🔄 Đang xử lý: {author_name}...")

            # 3. Tạo Vector
            vector = get_embedding(content)
            if not vector: continue

            # 4. Chuẩn bị data
            data = {
                "author": author_name,
                "content": content,
                "embedding": vector
            }

            # 5. Gửi lên Supabase
            supabase.table("quotes").insert(data).execute()
            
            print(f"✅ Đã nạp thành công: {author_name}")
            success_count += 1

        except Exception as e:
            print(f"❌ Lỗi file {file_path}: {e}")

    print(f"\n🎉 TỔNG KẾT: Đã nạp thành công {success_count} file dữ liệu.")

if __name__ == "__main__":
    main()
