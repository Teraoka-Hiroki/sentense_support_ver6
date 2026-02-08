# setensesport3

## 概要
軽量な音声/文章支援アプリケーションです。主要な実行ファイルは `app.py`、ロジックは `logic.py` にあります。

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
- API キーはリポジトリに含めないでください。ローカルに `APIキー (1).txt` のようなファイルがある場合は、既に `.gitignore` に追加しています。
- 推奨: 実行時に環境変数 `API_KEY` を設定するか、CI の Secret 管理を利用してください。

例（PowerShell）:
```
$env:API_KEY = "あなたの_api_key"
```

## 実行
```
python app.py
```

## ライセンス
必要なら `LICENSE` ファイルを追加してください（例: MIT）。

## 備考
- 詳細な使い方・スクリーンショット・デプロイ手順は追って `README.md` に追加してください。
