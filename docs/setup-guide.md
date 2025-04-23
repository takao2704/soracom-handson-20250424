# 環境構築ガイド

このガイドでは、SORACOMハンズオンを実施するための環境構築手順を説明します。

## 前提条件

- SORACOMアカウント（各自で用意）
- インターネット接続環境
- コマンドラインの基本的な操作知識

## 0.1 SORACOM API 環境

### SORACOMコンソールへのログイン

1. [SORACOMコンソール](https://console.soracom.io/)にアクセスします。
2. アカウント情報（メールアドレスとパスワード）を入力してログインします。

### APIキーの発行

1. コンソールにログインしたら、画面右上のユーザー名をクリックし、「ユーザー設定」を選択します。
2. 左側のメニューから「APIキー」を選択します。
3. 「認証情報を追加」ボタンをクリックします。
4. 「認証キーID（AuthKeyId）」と「認証キー（AuthKey）」が発行されます。
5. これらの情報をメモしておきます（後で使用します）。

### 設定ファイルの作成

1. このリポジトリのルートディレクトリに `.env` ファイルを作成します：

```bash
touch .env
```

2. テキストエディタで `.env` ファイルを開き、以下の内容を追加します：

```
SORACOM_AUTH_KEY_ID=keyId-xxxxxxxxxxxx
SORACOM_AUTH_KEY=secret-xxxxxxxxxxxx
```

注意: 環境変数の名前は正確に上記のとおりにしてください。特に`SORACOM_AUTH_KEY`は`SORACOM_AUTH_KEY_SECRET`ではなく、`SORACOM_AUTH_KEY`である必要があります。

3. 保存して閉じます。

## 0.2 Python実行環境

### Pythonのインストール確認

1. ターミナルを開き、以下のコマンドを実行してPythonのバージョンを確認します：

```bash
python --version
```

2. Python 3.12以上がインストールされていることを確認します。インストールされていない場合は、[Python公式サイト](https://www.python.org/downloads/)からダウンロードしてインストールしてください。

### 仮想環境の作成（推奨）

1. 以下のコマンドで仮想環境を作成します：

```bash
python -m venv venv
```

2. 仮想環境を有効化します：

- Windows:
```bash
venv\Scripts\activate
```

- macOS/Linux:
```bash
source venv/bin/activate
```

### 必要なライブラリのインストール

1. 以下のコマンドで必要なライブラリをインストールします：

```bash
pip install -r requirements.txt
```

2. インストールが完了したことを確認します：

```bash
pip list
```

3. 主な依存ライブラリ：
   - urllib3: HTTPリクエスト用
   - opencv-python: 画像処理用
   - numpy: 数値計算用
   - torch, torchvision: YOLOモデル用
   - pandas: データ解析用
   - flask: Webサーバー用
   - python-dotenv: 環境変数管理用

## 0.3 ハンズオンリポジトリダウンロード

### Gitのインストール確認

1. ターミナルを開き、以下のコマンドを実行してGitのバージョンを確認します：

```bash
git --version
```

2. Gitがインストールされていない場合は、[Git公式サイト](https://git-scm.com/downloads)からダウンロードしてインストールしてください。

### リポジトリのクローン

1. 以下のコマンドでリポジトリをクローンします：

```bash
git clone https://github.com/yourusername/soracom-handson-20250424.git
cd soracom-handson-20250424
```

## 0.4 YOLOモデルについて

ハンズオンでは、YOLOv8モデル（デフォルト: yolov8n.pt）を使用して画像解析を行います。
モデルファイルは既にプロジェクトに含まれているため、追加のダウンロードは必要ありません。

詳細は `docs/yolo-model-guide.md` を参照してください。

詳細は `docs/yolo-model-guide.md` を参照してください。

## 動作確認

### SORACOM API接続確認

1. 以下のコマンドを実行して、SORACOM APIへの接続を確認します：

```bash
python src/common/soracom_api.py
```

2. SIMの一覧が表示されれば成功です。

### Python環境確認

1. 以下のコマンドを実行して、Python環境を確認します：

```bash
python src/common/soracom_api.py
```

2. エラーなく実行されれば成功です。

## トラブルシューティング

### APIキーエラー

- `.env`ファイルの内容が正しいか確認してください。
- APIキーが有効であることを確認してください。

### Pythonライブラリのインストールエラー

- Pythonのバージョンが3.12以上であることを確認してください。
- 仮想環境が有効化されていることを確認してください。
- 管理者権限で実行してみてください。

### YOLOモデルのダウンロードエラー

- インターネット接続を確認してください。
- 必要なライブラリ（torch, torchvision, pandas）がインストールされていることを確認してください。
- `models/` ディレクトリが存在し、書き込み権限があることを確認してください。

### その他のエラー

- インターネット接続を確認してください。
- ファイアウォールやプロキシの設定を確認してください。