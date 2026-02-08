# setensesport3

## 概要
軽量な小説の場面の文章支援アプリケーションです。主要な実行ファイルは `app.py`、ロジックは `logic.py` にあります。

## 必要条件
- Python 3.8+
- 依存関係は `requirements.txt` に記載されています。

## セットアップ
1. リポジトリをクローンまたはこのフォルダへ移動します。

2. 仮想環境を作成して有効化します（Windows PowerShell の例）:
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. 依存関係をインストールします:
```
pip install -r requirements.txt
```

## 環境変数 / 秘密情報

例（PowerShell）:
```
$env:API_KEY = "あなたの_api_key"
```

## 実行
```
python app.py
```

## ライセンス
LICENSE: MIT

## 備考
- ブラックボックス最適化でヒューマンインザループを回して、より良い小説の場面を作ります。
  
