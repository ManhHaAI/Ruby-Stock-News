import requests
from bs4 import BeautifulSoup


def lay_tin_cafef_truc_tiep():
    # Link chuyên mục Chứng khoán trực tiếp của CafeF
    url = "https://cafef.vn/thi-truong-chung-khoan.chn"

    # Thêm 'headers' để giả dạng làm người dùng thật (tránh bị CafeF chặn)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print(f"1. Đang truy cập: {url}")
        response = requests.get(url, headers=headers)
        response.encoding = "utf-8"

        print(f"2. Mã trạng thái: {response.status_code}")

        # Dùng 'html.parser' thay vì 'xml' vì đây là trang web bình thường
        soup = BeautifulSoup(response.text, "html.parser")

        # Tìm các thẻ chứa bài viết (Trên CafeF, các bài báo thường nằm trong thẻ <h3> có class 'tlitem')
        # Lưu ý: Cấu trúc này có thể thay đổi tùy theo thiết kế của CafeF
        bai_viet_list = soup.find_all("h3")

        ket_qua = []
        for bai_viet in bai_viet_list:
            the_a = bai_viet.find("a")
            if the_a and the_a.has_attr("title") and the_a.has_attr("href"):
                tieu_de = the_a["title"]
                link = the_a["href"]

                # Bổ sung tên miền nếu link bị thiếu
                if link.startswith("/"):
                    link = "https://cafef.vn" + link

                ket_qua.append({"tieu_de": tieu_de, "link": link})

            # Chỉ lấy 5 bài để test
            if len(ket_qua) == 5:
                break

        return ket_qua

    except Exception as e:
        print("❌ Lỗi:", e)
        return []


if __name__ == "__main__":
    print("🚀 BẮT ĐẦU CHẠY CRAWLER CAFEF...\n")
    danh_sach_tin = lay_tin_cafef_truc_tiep()

    if len(danh_sach_tin) == 0:
        print("⚠️ Không lấy được tin nào.")
    else:
        for i, tin in enumerate(danh_sach_tin, 1):
            print(f"{i}. {tin['tieu_de']}")
            print(f"   Link: {tin['link']}\n")

    print("🏁 KẾT THÚC!")
