from PIL import Image
import pytesseract
from gtts import gTTS
from datetime import datetime
from pdf2image import convert_from_path
from pathlib import Path
from openai import OpenAI
client = OpenAI()

# 環境変数からAPIキーを設定
openai.api_key = os.getenv("OPENAI_API_KEY")

def preprocess_image(image):
    # 画像のサイズを取得
    width, height = image.size
    crop_height = height - 150
    cropped_image = image.crop((0, 0, width, crop_height))

    return cropped_image

def save_text(text, output_path):
    """テキストをGoogleドライブに保存"""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Googleドライブにテキストファイルを保存: {output_path}")


# PDFファイルが保存されているフォルダのパス
folder_path = '/content/drive/My Drive/翻訳'
output_folder = '/content/drive/My Drive/翻訳出力'

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# ファイル名に日付と時間を組み込む
filename = f"translated_text_{current_time}.txt"

# Googleドライブの保存先パス
output_path = f"/content/drive/My Drive/翻訳出力/{filename}"

mp3_path = f"/content/drive/My Drive/翻訳出力/translated_text_{current_time}.mp3"

def split_text_smartly(full_text, max_length=2000):
    """指定された最大長でテキストを区切り、文の区切りを尊重する"""
    segments = []
    while full_text:
        if len(full_text) <= max_length:
            segments.append(full_text)
            break
        # 指定された最大長で区切る位置を見つける
        split_index = full_text.rfind('。', 0, max_length) + 1
        if split_index == 0:  # 句点が見つからない場合は、強制的に区切る
            split_index = full_text.rfind(' ', 0, max_length)
            if split_index == -1:
                split_index = max_length
        segment = full_text[:split_index].strip()
        segments.append(segment)
        full_text = full_text[split_index:].strip()
    return segments

def process_pdf(pdf_file):
    global full_text
    full_text = ""
    images = convert_from_path(pdf_file)

    for i, image in enumerate(images):
        preprocessed_image = preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed_image, lang='eng')
        full_text += text + "\n"
    
    # テキストをセグメントに分割
    segments = split_text_smartly(full_text)
    translated_text = ""

    for segment in segments:
        try:
            response = client.chat.completions.create(
              model="gpt-3.5-turbo",
              messages=[
                {"role": "user", "content": f"以下の英文を日本語に翻訳してください: '{segment}'"},
              ]
            )
            translated_segment = response.choices[0].message.content
            translated_text += translated_segment
        except Exception as e:
            print(f"An error occurred: {e}")

    if translated_text:
        save_text(translated_text, output_path)
        tts = gTTS(text=translated_text, lang='ja')
        tts.save(str(mp3_path))
        print(f"MP3ファイルを保存: {mp3_path}")

latest_pdf = None
latest_mtime = 0

for pdf_file in Path(folder_path).glob('*.pdf'):
    mtime = pdf_file.stat().st_mtime
    if mtime > latest_mtime:
        latest_mtime = mtime
        latest_pdf = pdf_file

# 最新のPDFが見つかった場合処理
if latest_pdf:
    print(f"最新： {latest_pdf}")
    process_pdf(latest_pdf)
else:
    print("PDFなし")
