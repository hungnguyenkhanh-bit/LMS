import requests
from bs4 import BeautifulSoup
from faker import Faker
import json
import csv

# Khởi tạo Faker (để tạo mô tả và học kỳ giả nếu cần)
fake = Faker('vi_VN')

# Các prefix môn học cần lấy
COURSE_PREFIXES = ["CO1", "CO2", "CO3", "CO4"]

def scrape_and_transform_courses(prefixes=COURSE_PREFIXES, csv_path="mon_all.csv"):
    """
    Cào (Extract) + Biến đổi (Transform) dữ liệu các môn có mã bắt đầu bằng CO1, CO2, CO3, CO4
    và ghi ra file CSV 'mon_all.csv' phù hợp với send_course_database().
    """

    url = "https://mybk.hcmut.edu.vn/dkmh/searchMonHocDangKy.action"

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': (
            'JSESSIONID=1grl3xxy4iltiu91m2sptbc12; '
            'twk_uuid_5ec349bc8ee2956d73a26b4e=%7B%22uuid%22%3A%221.SwyllJ1rMd0JtLNePXU5Vxlf9rcqZucJOxtNw8cSQrjIFwXiu0gpPyGJUprb1ClwCRQZJPsgAb4qKgpP9JbS0s98PvlsPXDxVT8OLWqHURtYD7zoihq4q%22%2C%22version%22%3A3%2C%22domain%22%3A%22hcmut.edu.vn%22%2C%22ts%22%3A1756739770242%7D'
        ),
        'Origin': 'https://mybk.hcmut.edu.vn',
        'Referer': 'https://mybk.hcmut.edu.vn/dkmh/dangKyMonHocForm.action',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    # Dùng dict để tránh trùng môn: key = course_code
    all_courses = {}

    # --------- CÀO DỮ LIỆU ---------
    for prefix in prefixes:
        payload = {
            'msmh': prefix
        }

        print(f"Đang gọi API 'searchMonHocDangKy.action' với msmh='{prefix}'...")

        try:
            response = requests.post(url, data=payload, headers=headers)

            if response.status_code != 200:
                print(f"  -> Lỗi! Status code {response.status_code} cho prefix {prefix}")
                continue

            soup = BeautifulSoup(response.text, 'lxml')
            course_table = soup.find('table', id='tblMonHocMoLop')

            if not course_table:
                print(f"  -> Không tìm thấy bảng 'tblMonHocMoLop' cho prefix {prefix}.")
                print("--- DEBUG HTML (500 ký tự đầu) ---")
                print(response.text[:500])
                print("-----------------------------------")
                continue

            rows = course_table.find_all('tr')
            print(f"  -> Tìm thấy {len(rows)} hàng <tr> trong bảng cho prefix {prefix}.")

            for row in rows:
                cols = row.find_all('td')

                # Hàng dữ liệu môn thường có 7 cột
                if len(cols) == 7:
                    ma_mh = cols[2].get_text(strip=True)
                    ten_mh = cols[3].get_text(strip=True)
                    so_tin_chi_str = cols[4].get_text(strip=True)

                    if not ma_mh:
                        continue

                    if not any(ma_mh.startswith(p) for p in prefixes):
                        continue

                    if ma_mh in all_courses:
                        continue

                    try:
                        credits_float = float(so_tin_chi_str)

                        all_courses[ma_mh] = {
                            "course_name": ten_mh,
                            "course_code": ma_mh,
                            "credits": int(credits_float),
                            "semester": fake.random_element(
                                elements=('HK241', 'HK242', 'HK251')
                            ),
                        }
                    except ValueError:
                        continue

        except requests.RequestException as e:
            print(f"  -> Lỗi khi gọi API cho prefix {prefix}: {e}")
        except Exception as e:
            print(f"  -> Lỗi khi phân tích HTML cho prefix {prefix}: {e}")

    list_mon_hoc = list(all_courses.values())
    print(f"\nTrích xuất và biến đổi thành công {len(list_mon_hoc)} môn học (CO1/CO2/CO3/CO4).")

    # --------- GHI RA CSV PHÙ HỢP send_course_database() ---------
    # Cột đúng format: "Mã MH", "Tên MH", "Tín chỉ"
    if list_mon_hoc:
        fieldnames = ["Mã MH", "Tên MH", "Tín chỉ"]

        # utf-8-sig để DictReader trong hàm send_course_database đọc đúng BOM
        with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for mh in list_mon_hoc:
                writer.writerow({
                    "Mã MH": mh["course_code"],
                    "Tên MH": mh["course_name"],
                    "Tín chỉ": mh["credits"],
                })

        print(f"✅ Đã ghi {len(list_mon_hoc)} môn học vào file '{csv_path}' với cột: {fieldnames}")
    else:
        print("Không có môn học nào để ghi ra CSV (có thể cookie hết hạn hoặc không có môn phù hợp).")

    # (Optional) vẫn có thể in ra JSON để debug
    # print(json.dumps(list_mon_hoc, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    scrape_and_transform_courses()
