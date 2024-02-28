# translateBook

## 必要なライブラリのインストール
```
!sudo apt install tesseract-ocr
!pip install pytesseract
!pip install openai
```

## Googleドライブのマウント
```
from google.colab import drive
drive.mount('/content/drive')

!pip install openai
import os
```

## 環境変数にAPIキーを設定
```
os.environ["OPENAI_API_KEY"] = "【APIキー】"
```
https://platform.openai.com/api-keys
