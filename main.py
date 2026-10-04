from fastapi import FastAPI
import requests
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from crawler import lay_tin_cafef_truc_tiep
from ai_summarizer import tom_tat_tin_tuc

load_dotenv()


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# Hàm thực thi chính (không cần @app.get nữa vì giờ nó chạy ngầm)
def phat_song_tin_tuc(chat_id):
    try:
        print("⏰ Đến giờ rồi! Đang tự động thu thập tin tức...")
        danh_sach_tin = lay_tin_cafef_truc_tiep()

        if not danh_sach_tin:
            print("⚠️ Không có tin mới.")
            return

        print("🧠 Đang nhờ AI Gemini phân tích...")
        ban_tin_ai = tom_tat_tin_tuc(danh_sach_tin)

        print("📱 Đang gửi báo cáo qua Telegram...")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
       
        # TẠM TẮT parse_mode để tránh lỗi ký tự đặc biệt từ AI
        payload = {"chat_id": chat_id, "text": ban_tin_ai} 
        
        # Hứng kết quả trả về từ Telegram
        response = requests.post(url, json=payload)
        
        # Kiểm tra xem Telegram có chấp nhận không
        if response.status_code == 200:
            print("✅ Đã gửi Ting Ting thành công!")
        else:
            # Nếu Telegram từ chối, in thẳng lý do ra Logs
            print(f"❌ Telegram TỪ CHỐI gửi tin. Lý do: {response.text}")

    except Exception as e:
        print("❌ Lỗi hệ thống:", e)



# Cài đặt lịch trình (Chạy ngầm cùng FastAPI)
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    # Hẹn giờ: Chạy từ Thứ 2 đến Thứ 6 (mon-fri)
    # Lúc 8:15 sáng (trước giờ giao dịch) và 15:10 chiều (sau giờ đóng cửa)
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
from fastapi import Request # Nhớ thêm Request vào dòng import fastapi ở đầu file nhé

# Hàm gửi tin nhắn phản hồi nhanh
def gui_tin_nhan_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

# Cửa nhận thư Webhook
# Nhớ import thêm BackgroundTasks ở đầu file
from fastapi import Request, BackgroundTasks 

@app.post("/webhook")
async def nhan_tin_nhan(request: Request, background_tasks: BackgroundTasks): # Thêm background_tasks vào đây
    data = await request.json()
    
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        tin_nhan_den = data["message"]["text"]
        
        if tin_nhan_den == "/start":
            gui_tin_nhan_telegram(chat_id, "👋 Chào sếp! Gõ /tintuc để tôi cập nhật thị trường nhé!")
            
        elif tin_nhan_den == "/tintuc":
            # 1. Gửi tin nhắn báo đang xử lý ngay lập tức
            gui_tin_nhan_telegram(chat_id, "⏳ Sếp đợi chút, tôi đang đi đọc báo CafeF và nhờ AI phân tích ngay đây...")
            
            # 2. Đẩy việc cào tin nặng nhọc ra chạy ngầm phía sau
            background_tasks.add_task(phat_song_tin_tuc, chat_id)
            
    # 3. Lập tức trả về "ok" cho Telegram để khỏi bị phạt
    return {"status": "ok"}



@app.get("/")
def trang_chu():
    return {"message": "Bot đang chạy ngầm và chờ đến giờ phát sóng!"}


# Vẫn giữ lại đường dẫn này để bạn có thể bấm chạy bằng tay (test) bất cứ lúc nào
@app.get("/test-ngay")
def test_ngay():
    phat_song_tin_tuc()
    return {"message": "Đã ra lệnh phát sóng thủ công!"} 
