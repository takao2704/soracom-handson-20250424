#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenAI GPT-4oを使用して画像を解析するスクリプト
"""

import os
import sys
import argparse
import base64
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io
import httpx

# .envファイルを読み込む
load_dotenv()

def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description='OpenAI GPT-4oを使用して画像を解析するスクリプト')
    
    parser.add_argument('--image', required=True, help='解析する画像ファイルのパス')
    parser.add_argument('--output', help='解析結果を保存するファイルのパス')
    parser.add_argument('--prompt', default='この画像に何が写っているか詳しく説明してください。', help='GPT-4oに送るプロンプト')
    parser.add_argument('--api-key', help='OpenAI APIキー（指定しない場合は環境変数から読み込みます）')
    
    return parser.parse_args()

def encode_image(image_path):
    """画像をbase64エンコードする"""
    try:
        # 画像を開いてリサイズ（必要に応じて）
        img = Image.open(image_path)
        
        # 画像が大きすぎる場合はリサイズ
        max_size = 4000  # OpenAI APIの制限に合わせて調整
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            print(f"画像をリサイズしました: {img.size[0]}x{img.size[1]}")
        
        # JPEGに変換してバッファに保存
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        
        # base64エンコード
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return encoded_image
    except Exception as e:
        print(f"画像のエンコードに失敗しました: {str(e)}")
        sys.exit(1)

def analyze_image_with_gpt4o(image_path, prompt, api_key=None):
    """GPT-4oを使用して画像を解析する"""
    print(f"画像 {image_path} を解析中...")
    
    # APIキーの設定
    api_key_to_use = api_key if api_key else os.environ.get("OPENAI_API_KEY")
    if not api_key_to_use:
        print("エラー: OpenAI APIキーが設定されていません")
        print("--api-keyオプションで指定するか、OPENAI_API_KEY環境変数を設定してください")
        sys.exit(1)
    
    try:
        # 画像をbase64エンコード
        base64_image = encode_image(image_path)
        
        # OpenAIクライアントを初期化（プロキシ設定を無効化）
        http_client = httpx.Client(proxies=None)
        client = OpenAI(api_key=api_key_to_use, http_client=http_client)
        
        # GPT-4oに画像を送信
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "auto"  # 画像の詳細レベル: "low", "high", "auto"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        # レスポンスから解析結果を取得
        analysis = response.choices[0].message.content
        return analysis
    
    except Exception as e:
        print(f"画像解析に失敗しました: {str(e)}")
        sys.exit(1)

def save_analysis(analysis, output_path):
    """解析結果をファイルに保存する"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(analysis)
        print(f"解析結果を保存しました: {output_path}")
        return True
    except Exception as e:
        print(f"結果の保存に失敗しました: {str(e)}")
        return False

def main():
    """メイン関数"""
    args = parse_args()
    
    # 入力ファイルの存在確認
    if not os.path.isfile(args.image):
        print(f"エラー: 画像ファイル {args.image} が見つかりません")
        sys.exit(1)
    
    # 出力ファイルのパスを設定
    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(args.image)[0]
        output_path = f"{base_name}_analysis.txt"
    
    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 画像を解析
    analysis = analyze_image_with_gpt4o(args.image, args.prompt, args.api_key)
    
    # 解析結果を表示
    print("\n解析結果:")
    print("=" * 50)
    print(analysis)
    print("=" * 50)
    
    # 結果を保存
    if output_path:
        save_analysis(analysis, output_path)
    
    print("解析が完了しました")

if __name__ == "__main__":
    main()