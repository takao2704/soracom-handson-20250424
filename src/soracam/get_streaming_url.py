#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ソラカメのストリーミングURLを取得するスクリプト
MPEG-DASH形式のストリーミングURLを取得し、標準出力に表示します
"""

import os
import sys
import argparse
import time
from datetime import datetime, timedelta, timezone

# 共通モジュールのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from common.soracom_api import (
    load_config,
    auth_with_api_key,
    call_soracom_api
)

def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description='ソラカメのストリーミングURLを取得するスクリプト')
    
    parser.add_argument('--device_id', required=True, help='デバイスID')
    parser.add_argument('--from', dest='from_time', type=int, help='録画映像の開始時刻（UNIX時間、ミリ秒）')
    parser.add_argument('--to', dest='to_time', type=int, help='録画映像の終了時刻（UNIX時間、ミリ秒）')
    parser.add_argument('--config', default='soracom-config.json', help='設定ファイルのパス')
    
    return parser.parse_args()

def get_streaming_url(device_id, from_time=None, to_time=None):
    """ストリーミングURLを取得する"""
    path = f"/sora_cam/devices/{device_id}/stream"
    
    # クエリパラメータを設定
    query_params = {}
    if from_time:
        query_params['from'] = from_time
    if to_time:
        query_params['to'] = to_time
    
    # APIを呼び出す
    try:
        response = call_soracom_api(path, method='GET', additional_headers=None)
        
        # レスポンスからURLを取得
        if 'playList' in response and len(response['playList']) > 0:
            for entry in response['playList']:
                if 'url' in entry:
                    return entry['url']
            
            print("エラー: ストリーミングURLが見つかりません", file=sys.stderr)
            return None
        else:
            print("エラー: プレイリストが空です", file=sys.stderr)
            return None
    except Exception as e:
        print(f"エラー: ストリーミングURLの取得に失敗しました: {str(e)}", file=sys.stderr)
        return None

def main():
    """メイン関数"""
    args = parse_args()
    
    # 設定ファイルを読み込む
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', args.config)
    load_config(config_path)
    
    # APIキーとシークレットで認証
    print('APIキーとシークレットで認証中...', file=sys.stderr)
    auth_response = auth_with_api_key()
    print('認証成功:', auth_response, file=sys.stderr)
    
    # ストリーミングURLを取得
    print(f"デバイスID {args.device_id} のストリーミングURLを取得中...", file=sys.stderr)
    
    # from_timeとto_timeが指定されている場合は、その範囲の録画映像のURLを取得
    # 指定されていない場合は、最新映像のURLを取得
    url = get_streaming_url(args.device_id, args.from_time, args.to_time)
    
    if url:
        # 標準出力にURLのみを出力（他のスクリプトから利用しやすくするため）
        print(url)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())