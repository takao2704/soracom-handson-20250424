#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ソラカメの動画をエクスポートするスクリプト
指定した時間範囲の動画をMP4形式でエクスポートします
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta, timezone
import json

# 共通モジュールのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.soracom_api import (
    load_config,
    auth_with_api_key,
    request_video_export,
    get_video_export_status,
    download_video_export,
    wait_for_export_completion
)

def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description='ソラカメの動画をエクスポートするスクリプト')
    
    # デバイスIDを必須パラメータとして設定
    parser.add_argument('--device_id', required=True, help='デバイスID')
    parser.add_argument('--start', help='開始時刻（ISO 8601形式、例: 2023-04-24T10:00:00）')
    parser.add_argument('--end', help='終了時刻（ISO 8601形式、例: 2023-04-24T10:10:00）')
    parser.add_argument('--output', help='出力ファイル名（指定しない場合は "output.mp4" を使用）')
    parser.add_argument('--config', default='soracom-config.json', help='設定ファイルのパス')
    parser.add_argument('--wait', action='store_true', help='エクスポート完了を待つ')
    parser.add_argument('--timeout', type=int, default=600, help='タイムアウト（秒）')
    
    return parser.parse_args()

def validate_datetime(dt_str):
    """日時文字列が有効かチェックする"""
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def export_video(device_id, start_time, end_time, output_path, wait_for_completion=True, timeout=600):
    """動画をエクスポートする"""
    print(f"デバイスID: {device_id}")
    print(f"開始時刻: {start_time}")
    print(f"終了時刻: {end_time}")
    print(f"出力ファイル: {output_path}")
    
    # エクスポートをリクエスト
    input("Enterキーを押すと、動画エクスポートをリクエストします...")
    print("動画エクスポートをリクエスト中...")
    try:
        export_info = request_video_export(device_id, start_time, end_time)
        export_id = export_info.get('exportId')
        
        if not export_id:
            print("エラー: エクスポートIDが取得できませんでした")
            return False
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False
    
    print(f"エクスポートID: {export_id}")
    
    if not wait_for_completion:
        print(f"エクスポートジョブを開始しました。後で以下のコマンドで状態を確認できます:")
        print(f"python src/soracam/export_video.py --device_id {device_id} --start {start_time} --end {end_time} --output {output_path} --wait")
        # エクスポートIDをファイルに保存
        with open(f"{output_path}.export_id", 'w') as f:
            json.dump({
                'device_id': device_id,
                'export_id': export_id,
                'start': start_time,
                'end': end_time
            }, f)
        return True
    
    try:
        # エクスポート完了を待つ
        input("Enterキーを押すと、エクスポート完了を待ちます...")
        export_info = wait_for_export_completion(device_id, export_id, timeout)
        
        # 動画をダウンロード
        input("Enterキーを押すと、動画をダウンロードします...")
        print("動画をダウンロード中...")
        download_video_export(device_id, export_id, output_path)
        
        print(f"動画のエクスポートが完了しました: {output_path}")
        return True
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False

def main():
    """メイン関数"""
    args = parse_args()
    
    # device_idの設定
    device_id = args.device_id
    
    # 設定ファイルを読み込む
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', args.config)
    load_config(config_path)
    
    # APIキーとシークレットで認証
    print('APIキーとシークレットで認証中...')
    auth_response = auth_with_api_key()
    print('認証成功:', auth_response)
    
    input("Enterキーを押すと、処理を続行します...")
    
    # 日時の設定
    now = datetime.now(timezone.utc)
    
    # 開始時刻が指定されていない場合は、現在の時刻から1日前を使用
    if args.start:
        if not validate_datetime(args.start):
            print(f"エラー: 開始時刻の形式が無効です: {args.start}")
            print("正しい形式: 2023-04-24T10:00:00")
            sys.exit(1)
        start_time = args.start
    else:
        # 現在の時刻から1日前
        start_time = (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
        print(f"開始時刻が指定されていないため、現在の時刻から1日前を使用します: {start_time}")
    
    # 終了時刻が指定されていない場合は、開始時刻から10分後を使用
    if args.end:
        if not validate_datetime(args.end):
            print(f"エラー: 終了時刻の形式が無効です: {args.end}")
            print("正しい形式: 2023-04-24T10:10:00")
            sys.exit(1)
        end_time = args.end
    else:
        # 開始時刻から10分後（最大15分まで）
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_time = (start_dt + timedelta(minutes=10)).strftime('%Y-%m-%dT%H:%M:%S')
        print(f"終了時刻が指定されていないため、開始時刻から10分後を使用します: {end_time}")
    
    # 出力ファイルの設定
    if args.output:
        output_path = args.output
    else:
        # デフォルトの出力ファイル名
        output_path = "output.mp4"
        print(f"出力ファイル名が指定されていないため、デフォルト値を使用します: {output_path}")
    
    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 動画をエクスポート
    success = export_video(
        device_id,
        start_time,
        end_time,
        output_path,
        args.wait,
        args.timeout
    )
    
    if success:
        print("処理が正常に完了しました")
    else:
        print("処理中にエラーが発生しました")

if __name__ == "__main__":
    main()