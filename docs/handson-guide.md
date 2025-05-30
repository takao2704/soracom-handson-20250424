# SORACOMハンズオン手順書

このドキュメントは、SORACOM ハンズオン（2025年4月24日開催）の全体的な流れと手順を説明します。

## ハンズオン概要

このハンズオンでは、SORACOMのサービスを使用したIoTシステムの構築方法を学びます。具体的には以下の3つの主要セクションで構成されています：

1. **環境構築/確認** (15-30分)
2. **ソラカメ動画エクスポート** (75-90分)
3. **vSIMを使ったAWSへのデータ送信** (45-60分)

## 前提条件

- SORACOMアカウント（各自で用意）
- Python 3.12
- Node.js 14以上
- インターネット接続環境
- OSインストール済みRaspberry Pi（vSIMセクション用）
- vSIM（vSIMセクション用）

## タイムテーブル

| 時間 | 内容 |
|------|------|
| 14:00 - 14:15 | イントロダクション |
| 14:15 - 14:45 | 環境構築/確認 |
| 14:45 - 16:15 | ソラカメ動画エクスポート |
| 16:15 - 17:15 | vSIMを使ったAWSへのデータ送信 |
| 17:15 - 17:30 | まとめと質疑応答 |

## セクション0: 環境構築/確認 (15-30分)

このセクションでは、ハンズオンを進めるための環境を構築します。

### 主な内容

- SORACOM API環境の設定
- Python実行環境の確認
- ハンズオンリポジトリのダウンロードと確認

### 詳細手順

詳細な手順については、[環境構築ガイド](./setup-guide.md)を参照してください。

## セクション1: ソラカメ動画エクスポート (75-90分)

このセクションでは、SORACOMのソラカメサービスを使用して、動画や静止画をエクスポートし、解析する方法を学びます。

### 主な内容

- 時刻を指定した動画の切り出し(mp4ファイルへのエクスポート)
- 簡単なwebアプリ（htmlファイル+javascript）によるライブ視聴映像の再生
- 時刻を指定した静止画の切り出し(jpegファイルへのエクスポート)
- 切り出した静止画のYOLOv8nなどの軽量なモデルによる解析 (+alpha)
- 切り出した静止画の生成AIモデルによる解析 (+alpha)

### 詳細手順

詳細な手順については、[ソラカメ動画エクスポートガイド](./soracam-guide.md)を参照してください。

## セクション2: vSIMを使ったAWSへのデータ送信 (45-60分)

このセクションでは、SORACOMのvSIMを使用してRaspberry PiからAWSにセンサーデータを送信する方法を学びます。

### 主な内容

- Raspberry Piのセットアップ
- vSIMの発行
- SORACOMへのセンサ模擬データ送信（HTTP）
- SORACOMへのセンサ模擬データ送信（UDP）(+alpha)
- SORACOM Funnelを介したデータ送信（HTTP to HTTPS）
- SORACOM Funnelを介したデータ送信（UDP to HTTPS）(+alpha)

### 詳細手順

詳細な手順については、[vSIM AWS連携ガイド](./vsim-guide.md)を参照してください。

## トラブルシューティング

各セクションの詳細ガイドには、それぞれのトラブルシューティング情報が含まれています。一般的な問題については以下を参照してください：

### APIエラーが発生する場合
- APIキーが正しく設定されているか確認
- SORACOMコンソールでAPIキーの権限を確認
- ネットワーク接続を確認

### 環境構築の問題
- Pythonのバージョンが3.12以上であることを確認
- Node.jsのバージョンが14以上であることを確認
- 必要なライブラリがすべてインストールされていることを確認

## 参考リソース

- [SORACOM公式ドキュメント](https://dev.soracom.io/)
- [SORACOM API リファレンス](https://dev.soracom.io/jp/docs/api/)
- [OpenAI API ドキュメント](https://platform.openai.com/docs/api-reference)
- [YOLOv8 GitHub リポジトリ](https://github.com/ultralytics/ultralytics)
- [GitHub Issues](https://github.com/yourusername/soracom-handson-20250424/issues)