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
    print(f"Googleドライブにテキストファイルを保存しました: {output_path}")


# PDFファイルが保存されているフォルダのパスを指定
folder_path = '/content/drive/My Drive/翻訳'
output_folder = '/content/drive/My Drive/翻訳出力'

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# ファイル名に日付と時間を組み込む
filename = f"translated_text_{current_time}.txt"

# Googleドライブの保存先パス
output_path = f"/content/drive/My Drive/翻訳出力/{filename}"

mp3_path = f"/content/drive/My Drive/翻訳出力/translated_text_{current_time}.mp3"


def process_pdf(pdf_file):
    global full_text
    full_text = ""
    images = convert_from_path(pdf_file)

    for i, image in enumerate(images):
        preprocessed_image = preprocess_image(image)
        text = pytesseract.image_to_string(preprocessed_image, lang='eng')
        full_text += text + "\n"

    translated_text = ""  # 変数を初期化

    try:
        response = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "user", "content": f"Please translate the following text into Japanese: '{full_text}'"},
          ]
        )
        # レスポンスからテキストを抽出
        translated_text = response.choices[0].message.content
        print("Translated Text:")
        print(translated_text)

    except Exception as e:
        print(f"An error occurred: {e}")

    if translated_text:
        save_text(translated_text, output_path) 
        tts = gTTS(text=translated_text, lang='ja')
        tts.save(str(mp3_path))
        print(f"MP3ファイルを保存しました: {mp3_path}")

for pdf_file in Path(folder_path).glob('*.pdf'):
    process_pdf(pdf_file)  
