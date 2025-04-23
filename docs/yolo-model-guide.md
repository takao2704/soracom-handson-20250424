# YOLOモデルの使用方法

このガイドでは、YOLOv8モデルを使用して、ハンズオン環境で画像解析を行う方法を説明します。

## YOLOv8について

YOLOv8は、Ultralyticsが開発した最新のオブジェクト検出モデルです。YOLOv5の後継として、より高速かつ高精度な物体検出を実現しています。

## ハンズオン環境のセットアップ

ハンズオン環境では、YOLOv8モデル（デフォルト: yolov8n.pt）が既にプロジェクトに含まれています。追加のダウンロードは必要ありません。

必要なPythonパッケージは以下のコマンドでインストールできます：

```bash
pip install -r requirements.txt
```

これにより、`ultralytics`パッケージ（YOLOv8を使用するためのライブラリ）がインストールされます。

## ハンズオン中の使用方法

ハンズオン中は、以下のコマンドで画像内の物体を検出できます。

```bash
# 基本的なモデル（yolov8n）を使用
python src/soracam/analyze_image_yolo.py --image 画像ファイル --output 出力ファイル

# または、camera_image引数を使用することもできます（--imageと同じ機能）
python src/soracam/analyze_image_yolo.py --camera_image 画像ファイル --output 出力ファイル

# より大きなモデル（精度が高いが処理が遅い）を使用
python src/soracam/analyze_image_yolo.py --image 画像ファイル --output 出力ファイル --model yolov8s.pt
```

### オプション

- `--image` または `--camera_image`: 解析する画像ファイルのパス（どちらか一方が必須）
- `--output`: 解析結果を保存するファイルのパス（必須）
- `--model`: 使用するモデル（デフォルト: yolov8n.pt）
  - 選択肢: yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
  - モデルサイズが大きいほど精度が高いが、処理が遅くなります
- `--conf`: 信頼度のしきい値（0-1、デフォルト: 0.25）
  - 値が小さいほど検出される物体が増えますが、誤検出も増えます
- `--save-txt`: 検出結果をテキストファイルにも保存する

## インターネット接続がない環境での動作

YOLOv8のnanoモデル（yolov8n.pt）は既にプロジェクトに含まれているため、インターネット接続がなくても基本的な物体検出を行うことができます。

他のモデル（yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt）を使用する場合は、初回実行時にインターネット接続が必要です。モデルは自動的にダウンロードされ、キャッシュされます。

## トラブルシューティング

### 画像の解析に失敗する場合

- 画像ファイルのパスが正しいか確認してください
- 画像ファイルが破損していないか確認してください
- Ultralyticsパッケージがインストールされているか確認してください
  ```bash
  pip show ultralytics
  ```

### その他のエラー

- インターネット接続を確認してください
- Pythonの依存ライブラリをインストールしてください
  ```bash
  pip install -r requirements.txt
  ```

## 注意事項

- YOLOv8モデルは、COCOデータセットの80クラスを検出できます（人、車、犬、猫など）
- モデルのサイズによって、必要なメモリ量と処理時間が異なります
  - yolov8n: 最小モデル（最高速、低精度）
  - yolov8s: 小さいモデル
  - yolov8m: 中程度のモデル
  - yolov8l: 大きいモデル
  - yolov8x: 最大モデル（低速、高精度）