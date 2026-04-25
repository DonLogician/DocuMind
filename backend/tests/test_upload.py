import requests
import os

url = "http://127.0.0.1:8000/api/upload"

# 这里创建一个简单的 txt 文件用于测试
test_file_path = "test_upload.txt"
with open(test_file_path, "w", encoding="utf-8") as f:
    f.write(
        "这只是一个测试文件，用于测试文档研讨助手的上传和读取功能。\n包含一行单纯的文本！"
    )

try:
    with open(test_file_path, "rb") as f:
        response = requests.post(url, files={"file": f})

    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(response.json())
finally:
    # 善后工作：清理测试文件
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
