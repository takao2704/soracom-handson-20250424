# SORACOM ハンズオン 2025/04/24

このリポジトリはSORACOMハンズオン（2025年4月24日開催）のためのプロジェクトです。

## 概要

SORACOMのサービスを使用したIoTデバイスの接続と管理に関するハンズオン資料を含みます。このハンズオンは初心者〜中級者向けに設計されており、基本的なPythonの知識を前提としています。

## ハンズオン内容

ハンズオンは以下の3つの主要セクションで構成されています：

### 0. 環境構築/確認（15-30分）

- **SORACOM API 環境**: APIキーの発行と設定
- **Python実行環境**: Python 3.12と必要なライブラリの確認
- **ハンズオンリポジトリ**: リポジトリのクローンと構造確認

### 1. ソラカメ動画エクスポート（75-90分）

- **動画の切り出し**: 時刻を指定した動画のmp4ファイルへのエクスポート
- **Webアプリによるライブ視聴**: HTMLとJavaScriptを使った映像の再生
- **静止画の切り出し**: 時刻を指定した静止画のjpegファイルへのエクスポート
- **YOLO解析(+alpha)**: 切り出した静止画の軽量モデルによる解析
- **生成AI解析(+alpha)**: OpenAI GPT-4oを使った静止画の解析

### 2. vSIMを使ったAWSへのデータ送信（45-60分）

- **Raspberry Piのセットアップ**: OSインストール済みRaspberry Piの設定
- **vSIMの発行**: SORACOMコンソールでの操作とRaspberry Piへの設定
- **センサ模擬データ送信(HTTP)**: curlコマンドを使ったデータ送信
- **センサ模擬データ送信(UDP)(+alpha)**: netcatを使ったUDPデータ送信
- **SORACOM Beam連携(HTTP)**: uni.soracom.ioへのPOSTとAWSへの転送
- **SORACOM Beam連携(UDP)(+alpha)**: UDP to HTTPS変換とデータ送信

## リポジトリ構造

```
soracom-handson-20250424/
├── README.md                      # プロジェクト概要
├── package.json                   # Node.js設定ファイル
├── requirements.txt               # Pythonの依存関係
├── .gitignore                     # Gitの無視ファイル設定
├── docs/                          # ドキュメント
│   ├── handson-guide.md           # ハンズオン全体のガイド
│   ├── setup-guide.md             # 環境構築ガイド
│   ├── soracam-guide.md           # ソラカメ動画エクスポートガイド
│   └── vsim-guide.md              # vSIM AWS連携ガイド
├── src/                           # ソースコード
│   ├── common/                    # 共通コード
│   │   ├── soracom_api.js         # SORACOM API共通関数
│   │   └── soracom_api.py         # SORACOM API共通関数(Python版)
│   ├── soracam/                   # ソラカメ関連
│   │   ├── export_video.py        # 動画エクスポート
│   │   ├── export_image.py        # 静止画エクスポート
│   │   ├── analyze_image_yolo.py  # YOLO解析
│   │   ├── analyze_image_gpt.py   # GPT-4o解析
│   │   └── web/                   # Webアプリ
│   │       ├── index.html         # ライブ視聴ページ
│   │       ├── styles.css         # スタイルシート
│   │       └── script.js          # JavaScript
│   └── vsim/                      # vSIM関連
│       ├── setup_raspi.sh         # Raspberry Piセットアップスクリプト
│       ├── send_http.sh           # HTTPデータ送信
│       ├── send_udp.sh            # UDPデータ送信
│       ├── send_beam_http.sh      # Beam経由HTTPデータ送信
│       └── send_beam_udp.sh       # Beam経由UDPデータ送信
└── examples/                      # サンプルデータ
    ├── config_sample.json         # 設定ファイルサンプル
    └── sensor_data_sample.json    # センサーデータサンプル
```

## 使用方法

1. このリポジトリをクローンします：
   ```
   git clone https://github.com/yourusername/soracom-handson-20250424.git
   cd soracom-handson-20250424
   ```

2. 必要な依存関係をインストールします：
   ```
   # Node.js依存関係
   npm install
   
   # Python依存関係
   pip install -r requirements.txt
   ```

3. 各セクションのドキュメントに従ってハンズオンを進めてください：
   - 環境構築: `docs/setup-guide.md`
   - ソラカメ: `docs/soracam-guide.md`
   - vSIM: `docs/vsim-guide.md`

## 前提条件

- SORACOMアカウント（各自で用意）
- Python 3.12
- Node.js 14以上
- Raspberry Pi（OSインストール済み）
- vSIM