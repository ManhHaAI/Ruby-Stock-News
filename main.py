from fastapi import FastAPI, Request, BackgroundTasks
import requests
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from crawler import lay_tin_cafef_truc_tiep
from ai_summarizer import tom_tat_tin_tuc

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==========================================
# 1. HÀM CÀO TIN VÀ PHÁT SÓNG (ĐÃ THÊM is_auto)
# ==========================================
def phat_song_tin_tuc(chat_id=CHAT_ID, is_auto=True):
    try:
        print("⏰ Đang xử lý thu thập tin tức...")
        danh_sach_tin = lay_tin_cafef_truc_tiep()

        if not danh_sach_tin:
            print("⚠️ Không có tin mới.")
            return

        print("🧠 Đang nhờ AI Gemini phân tích...")
        ban_tin_ai = tom_tat_tin_tuc(danh_sach_tin)

        # --- TÍCH HỢP Ý TƯỞNG 1: PHÂN BIỆT NGỮ CẢNH ---
        if is_auto:
            loi_chao = "⏰ BẢN TIN CHỨNG KHOÁN TỰ ĐỘNG:\n\n"
        else:
            loi_chao = "✅ TRẢ LỜI YÊU CẦU CỦA SẾP:\n\n"
            
        ban_tin_cuoi_cung = loi_chao + ban_tin_ai
        # ----------------------------------------------

        print("📱 Đang gửi báo cáo qua Telegram...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
       
        # TẠM TẮT parse_mode để tránh lỗi ký tự đặc biệt từ AI
        payload = {"chat_id": chat_id, "text": ban_tin_cuoi_cung} 
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Đã gửi Ting Ting thành công!")
        else:
            print(f"❌ Telegram TỪ CHỐI gửi tin. Lý do: {response.text}")

    except Exception as e:
        print("❌ Lỗi hệ thống:", e)


# ==========================================
# 2. HỆ THỐNG HẸN GIỜ (APScheduler)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler(timezone="Asia/Ho_Chi_Minh")
    # Hẹn giờ: Chạy từ Thứ 2 đến Thứ 6 (mon-fri)
    # Lúc 8:15 sáng và 15:10 chiều
    # Vì không truyền tham số, nó sẽ tự dùng chat_id=CHAT_ID và is_auto=True
    scheduler.add_job(
        phat_song_tin_tuc, "cron", day_of_week="mon-fri", hour=8, minute=15
    )
    scheduler.add_job(
        phat_song_tin_tuc, "cron", day_of_week="mon-fri", hour=15, minute=10
    )

    scheduler.start()
    print("🕒 Hệ thống lập lịch đã khởi động!")
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


# ==========================================
# 3. HÀM GỬI TIN NHẮN NHANH CHO WEBHOOK
# ==========================================
def gui_tin_nhan_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


# ==========================================
# 4. CỔNG NHẬN LỆNH WEBHOOK TỪ TELEGRAM
# ==========================================
@app.post("/webhook")
async def nhan_tin_nhan(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        tin_nhan_den = data["message"]["text"]
        
        if tin_nhan_den == "/start":
            gui_tin_nhan_telegram(chat_id, "👋 Chào sếp! Gõ /tintuc để tôi cập nhật thị trường nhé!")
            
        elif tin_nhan_den == "/tintuc":
            gui_tin_nhan_telegram(chat_id, "⏳ Sếp đợi chút, tôi đang đi đọc báo CafeF và nhờ AI phân tích ngay đây...")
            
            # ĐIỂM MẤU CHỐT: Truyền False vào cuối để báo đây KHÔNG PHẢI tin tự động
            background_tasks.add_task(phat_song_tin_tuc, chat_id, False)
            
    return {"status": "ok"}


# ==========================================
# 5. CÁC ĐƯỜNG DẪN KIỂM TRA (TEST)
# ==========================================
@app.get("/")
def trang_chu():
    return {"message": "Bot đang chạy ngầm và chờ đến giờ phát sóng!"}

@app.get("/test-ngay")
def test_ngay():
    # Truyền False để khi test tay, nó cũng hiện "Trả lời yêu cầu của sếp"
    phat_song_tin_tuc(CHAT_ID, False)
    return {"message": "Đã ra lệnh phát sóng thủ công!"}
