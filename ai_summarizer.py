import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Tải biến môi trường từ file .env
load_dotenv()

# 2. Cấu hình chìa khóa (API Key) cho Gemini
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)


def tom_tat_tin_tuc(danh_sach_tin):
    # Nếu không có tin nào thì báo lỗi luôn
    if not danh_sach_tin:
        return "Không có tin tức nào mới để tóm tắt."

    # 3. Chọn mô hình AI (gemini-3.6-flash chạy rất nhanh và thông minh)
    model = genai.GenerativeModel("gemini-3.6-flash")

    # 4. Soạn "Lệnh" (Prompt) để ra việc cho AI
    prompt = "Bạn là một chuyên gia tư vấn đầu tư chứng khoán tại Việt Nam. Dưới đây là các tin tức thị trường mới nhất hôm nay:\n\n"

    for i, tin in enumerate(danh_sach_tin, 1):
        prompt += f"{i}. {tin['tieu_de']}\n"

    prompt += """
    Dựa vào các tiêu đề trên, hãy thực hiện 4 việc:
    1. Viết 1 đoạn văn ngắn (khoảng 3-4 câu) tóm tắt tình hình chung của thị trường. Đặc biệt, nếu trong tin có nhắc đến các mã cổ phiếu PC1, CII, VIX, hãy in đậm và đưa lên đầu tiên kèm theo nhận định tác động.
    2. Đánh giá nhanh xem những tin tức này mang tính Tích cực, Tiêu cực hay Trung lập đối với nhà đầu tư.
    3. Hãy chấm điểm tâm lý thị trường theo thang điểm từ 1 đến 10 (1 là cực kỳ hoảng loạn, 10 là hưng phấn tột độ) và giải thích ngắn gọn lý do.
    4. Hãy trình bày kết quả bằng gạch đầu dòng, sử dụng các biểu tượng cảm xúc (emoji) như 📈 (tăng), 📉 (giảm), ⚠️ (chú ý) và in đậm (bằng dấu ** **) các từ khóa quan trọng.
    Giọng văn chuyên nghiệp, gần gũi và dễ hiểu.
    """

    try:
        print("🧠 Đang gửi dữ liệu cho Gemini suy nghĩ...")
        # 5. Gọi AI sinh ra câu trả lời
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("❌ Lỗi khi gọi AI Gemini:", e)
        return "Xin lỗi, hệ thống AI đang bận, vui lòng thử lại sau."


# Đoạn code chạy thử
if __name__ == "__main__":
    # Giả lập 2 tin tức để test xem AI có hoạt động không
    tin_test = [
        {"tieu_de": "VN-Index bất ngờ vượt mốc 1300 điểm, thanh khoản bùng nổ"},
        {"tieu_de": "Ngân hàng Nhà nước tiếp tục giữ nguyên mức lãi suất điều hành"},
    ]

    ket_qua = tom_tat_tin_tuc(tin_test)
    print("\n🤖 BẢN TIN TỪ GEMINI:\n")
    print(ket_qua)
