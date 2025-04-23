#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ソラカメの静止画をエクスポートするスクリプト
指定した時刻の静止画をJPEG形式でエクスポートします
"""

import os
import sys
import argparse
from datetime import datetime, timedelta, timezone
import time

# 共通モジュールのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.soracom_api import (
    load_config,
    auth_with_api_key,
    get_image_snapshot,
    request_image_export,
    get_image_export_status,
    download_image_export,
    wait_for_image_export_completion
)

def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description='ソラカメの静止画をエクスポートするスクリプト')
    
    # デバイスIDを必須パラメータとして設定
    parser.add_argument('--device_id', required=True, help='デバイスID')
    parser.add_argument('--timestamp', help='時刻（ISO 8601形式、例: 2023-04-24T10:00:00）')
    parser.add_argument('--output', required=True, help='出力ファイル名（複数時刻の場合は%dが連番に置換されます）')
    parser.add_argument('--config', default='soracom-config.json', help='設定ファイルのパス')
    parser.add_argument('--export-type', choices=['snapshot', 'recorded'], default='snapshot',
                        help='エクスポートタイプ（snapshot: リアルタイムの静止画、recorded: 録画映像からの静止画）')
    parser.add_argument('--wait', action='store_true', help='エクスポート完了を待つ（recordedタイプのみ）')
    parser.add_argument('--timeout', type=int, default=600, help='タイムアウト（秒）（recordedタイプのみ）')
    
    # 複数時刻の静止画取得用オプション
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', help='開始時刻（ISO 8601形式、例: 2025-04-24T10:00:00）')
    group.add_argument('--timestamps', help='カンマ区切りの時刻リスト（例: 2025-04-24T10:00:00,2025-04-24T11:00:00）')
    
    parser.add_argument('--end', help='終了時刻（ISO 8601形式、例: 2025-04-24T10:10:00）')
    parser.add_argument('--interval', type=int, help='時間間隔（秒）')
    
    return parser.parse_args()

def validate_datetime(dt_str):
    """日時文字列が有効かチェックする"""
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def generate_timestamps(start, end, interval):
    """開始時刻、終了時刻、間隔から時刻リストを生成する"""
    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
    
    timestamps = []
    current_dt = start_dt
    
    while current_dt <= end_dt:
        timestamps.append(current_dt.isoformat())
        current_dt += timedelta(seconds=interval)
    
    return timestamps

def export_image_snapshot(device_id, timestamp, output_path, wait_for_completion=True, timeout=600):
    """リアルタイムの静止画を取得する（エクスポートAPIを使用）"""
    print(f"デバイスID: {device_id}")
    print(f"時刻: {timestamp}")
    print(f"出力ファイル: {output_path}")
    
    try:
        # 静止画エクスポートをリクエスト
        input("Enterキーを押すと、静止画エクスポートをリクエストします...")
        print("静止画エクスポートをリクエスト中...")
        try:
            export_info = request_image_export(device_id, timestamp)
            export_id = export_info.get('exportId')
            
            if not export_id:
                print("エラー: エクスポートIDが取得できませんでした")
                raise Exception("エクスポートIDが取得できませんでした")
                
            print(f"エクスポートID: {export_id}")
            
            if not wait_for_completion:
                print(f"エクスポートジョブを開始しました。後で以下のコマンドで状態を確認できます:")
                print(f"python src/soracam/export_image.py --device_id {device_id} --timestamp {timestamp} --output {output_path} --export-type snapshot --wait")
                return True
            
            # エクスポート完了を待つ
            input("Enterキーを押すと、エクスポート完了を待ちます...")
            export_info = wait_for_image_export_completion(device_id, export_id, timeout)
            
            # 静止画をダウンロード
            input("Enterキーを押すと、静止画をダウンロードします...")
            print("静止画をダウンロード中...")
            download_image_export(device_id, export_id, output_path)
            
            print(f"静止画のエクスポートが完了しました: {output_path}")
            return True
        except Exception as e:
            print(f"静止画エクスポートのリクエスト中にエラーが発生しました: {str(e)}")
            return False
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False

def export_image_recorded(device_id, timestamp, output_path, wait_for_completion=True, timeout=600):
    """録画映像から静止画をエクスポートする"""
    print(f"デバイスID: {device_id}")
    print(f"時刻: {timestamp}")
    print(f"出力ファイル: {output_path}")
    
    try:
        # 静止画エクスポートをリクエスト
        input("Enterキーを押すと、録画映像から静止画エクスポートをリクエストします...")
        print("録画映像から静止画エクスポートをリクエスト中...")
        try:
            export_info = request_image_export(device_id, timestamp)
            export_id = export_info.get('exportId')
            
            if not export_id:
                print("エラー: エクスポートIDが取得できませんでした")
                raise Exception("エクスポートIDが取得できませんでした")
                
            print(f"エクスポートID: {export_id}")
            
            if not wait_for_completion:
                print(f"エクスポートジョブを開始しました。後で以下のコマンドで状態を確認できます:")
                print(f"python src/soracam/export_image.py --device_id {device_id} --timestamp {timestamp} --output {output_path} --export-type recorded --wait")
                return True
            
            # エクスポート完了を待つ
            input("Enterキーを押すと、エクスポート完了を待ちます...")
            export_info = wait_for_image_export_completion(device_id, export_id, timeout)
            
            # 静止画をダウンロード
            input("Enterキーを押すと、静止画をダウンロードします...")
            print("静止画をダウンロード中...")
            download_image_export(device_id, export_id, output_path)
            
            print(f"静止画のエクスポートが完了しました: {output_path}")
            return True
        except Exception as e:
            print(f"静止画エクスポートのリクエスト中にエラーが発生しました: {str(e)}")
            return False
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False

def export_image(device_id, timestamp, output_path, export_type='snapshot', wait=False, timeout=600):
    """静止画をエクスポートする"""
    if export_type == 'snapshot':
        return export_image_snapshot(device_id, timestamp, output_path, wait, timeout)
    else:  # recorded
        return export_image_recorded(device_id, timestamp, output_path, wait, timeout)

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
    
    # 時刻リストを準備
    timestamps = []
    
    if args.timestamp:
        # 単一の時刻
        if not validate_datetime(args.timestamp):
            print(f"エラー: 時刻の形式が無効です: {args.timestamp}")
            print("正しい形式: 2025-04-24T10:00:00")
            sys.exit(1)
        timestamps = [args.timestamp]
    
    elif args.timestamps:
        # カンマ区切りの時刻リスト
        timestamp_list = args.timestamps.split(',')
        for ts in timestamp_list:
            if not validate_datetime(ts):
                print(f"エラー: 時刻の形式が無効です: {ts}")
                print("正しい形式: 2025-04-24T10:00:00")
                sys.exit(1)
        timestamps = timestamp_list
    
    elif args.start and args.end and args.interval:
        # 開始時刻、終了時刻、間隔から生成
        if not validate_datetime(args.start):
            print(f"エラー: 開始時刻の形式が無効です: {args.start}")
            print("正しい形式: 2025-04-24T10:00:00")
            sys.exit(1)
        
        if not validate_datetime(args.end):
            print(f"エラー: 終了時刻の形式が無効です: {args.end}")
            print("正しい形式: 2025-04-24T10:10:00")
            sys.exit(1)
        
        timestamps = generate_timestamps(args.start, args.end, args.interval)
    
    else:
        # 現在時刻を使用
        print("時刻が指定されていないため、現在時刻の静止画を取得します")
        timestamps = [datetime.now(timezone.utc).isoformat()]
    
    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 静止画をエクスポート
    success_count = 0
    for i, timestamp in enumerate(timestamps):
        # 出力ファイル名を生成（複数の場合は連番）
        if len(timestamps) > 1:
            output_path = args.output.replace('%d', str(i + 1))
            if '%d' not in args.output:
                base, ext = os.path.splitext(args.output)
                output_path = f"{base}_{i + 1}{ext}"
        else:
            output_path = args.output
        
        if export_image(device_id, timestamp, output_path, args.export_type, args.wait, args.timeout):
            success_count += 1
        
        # APIレート制限を避けるために少し待機
        if i < len(timestamps) - 1:
            time.sleep(1)
    
    print(f"合計: {len(timestamps)}件中{success_count}件の静止画をエクスポートしました")
    
    if success_count < len(timestamps):
        print("一部の静止画のエクスポートに失敗しましたが、処理は完了しました")
    else:
        print("処理が正常に完了しました")

if __name__ == "__main__":
    main()