# import pyspark
# print(pyspark.__version__)
import requests
from bs4 import BeautifulSoup
import io
import re
# Lấy link url và xác định vị trí nội dung truyện
url = "https://sachtruyen.net/doc-sach/nhung-cuoc-phieu-luu-cua-tom-s.87188.0001"

response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Cái này bạn mở Devtools lên chịu khó tìm class và div của nội dung nghe
story_content_elements = soup.find_all("div", class_="reading-paragraph")

# Lấy nội dung truyện
story_content = []

for div in story_content_elements:
    story_content.append(div.text.strip())

# Tách nội dung các câu theo kí tự
sentences = re.split("(?<=[.!?])\s", " ".join(story_content))

# Ghi danh sách các câu vào file
with io.open("data_en.txt", "w", encoding="utf-8") as f:
    for sentence in sentences:
        f.write(sentence + "\n")