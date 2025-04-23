#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SORACOM APIを使用するための共通関数
ハンズオン用に拡張されたバージョン
"""

import os
import json
import urllib3
import certifi
import time
import zipfile
import tempfile
from datetime import datetime
from urllib.parse import urlencode
from dotenv import load_dotenv
import shutil

# .envファイルを読み込む
load_dotenv()

# 設定
config = {
    "endpoint": "https://api.soracom.io/v1",
    "auth": {
        "auth_key_id": os.environ.get("SORACOM_AUTH_KEY_ID", "keyId-xxxxxxxxxxxx"),
        "auth_key": os.environ.get("SORACOM_AUTH_KEY", "secret-xxxxxxxxxxxx"),
        "api_key": None,
        "token": None
    }
}

# HTTPクライアントの初期化
http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

def load_config(config_path):
    """
    設定ファイルから認証情報を読み込む
    
    Args:
        config_path (str): 設定ファイルのパス
    """
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        if 'authKeyId' in config_data and 'authKey' in config_data:
            config['auth']['auth_key_id'] = config_data['authKeyId']
            config['auth']['auth_key'] = config_data['authKey']
            print('設定ファイルから認証情報を読み込みました')
    except Exception as e:
        print(f'設定ファイル {config_path} の読み込みに失敗しました: {str(e)}')
        print('環境変数または既定値を使用します')

def call_soracom_api(path, method='GET', body=None, additional_headers=None):
    """
    SORACOMのAPIを呼び出す関数
    
    Args:
        path (str): APIのパス
        method (str): HTTPメソッド
        body (dict): リクエストボディ
        additional_headers (dict): 追加のヘッダー
        
    Returns:
        dict: レスポンス
    """
    url = f"{config['endpoint']}{path}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 認証トークンがあれば使用する
    if config['auth']['api_key'] and config['auth']['token']:
        headers['X-Soracom-API-Key'] = config['auth']['api_key']
        headers['X-Soracom-Token'] = config['auth']['token']
    else:
        # 認証トークンがなければAPIキーとシークレットを使用する
        headers['X-Soracom-API-Key'] = config['auth']['auth_key_id']
        headers['X-Soracom-Token'] = config['auth']['auth_key']
    
    if additional_headers:
        headers.update(additional_headers)
    
    try:
        if body:
            encoded_body = json.dumps(body).encode('utf-8')
            response = http.request(
                method,
                url,
                body=encoded_body,
                headers=headers
            )
        else:
            response = http.request(
                method,
                url,
                headers=headers
            )
        
        if response.status >= 400:
            error_text = response.data.decode('utf-8')
            raise Exception(f"API呼び出しエラー: {response.status} - {error_text}")
        
        # レスポンスが空の場合は空の辞書を返す
        if response.status == 204 or len(response.data) == 0:
            return {}
        
        return json.loads(response.data.decode('utf-8'))
    except Exception as e:
        print(f"API呼び出しエラー: {str(e)}")
        raise

# ===== SIM関連のAPI =====

def get_subscribers(limit=None, last_evaluated_key=None):
    """
    SIMの一覧を取得する
    
    Args:
        limit (int): 取得する最大件数
        last_evaluated_key (str): 前回の取得結果の最後のキー
        
    Returns:
        list: SIMの一覧
    """
    query_params = {}
    if limit:
        query_params['limit'] = limit
    if last_evaluated_key:
        query_params['last_evaluated_key'] = last_evaluated_key
    
    query = f"?{urlencode(query_params)}" if query_params else ""
    path = f"/subscribers{query}"
    
    return call_soracom_api(path)

# この関数は存在しないAPIを呼び出しているため削除
# def get_subscriber_status(imsi):
#     """
#     SIMのステータスを取得する
#
#     Args:
#         imsi (str): IMSI
#
#     Returns:
#         dict: SIMのステータス
#     """
#     return call_soracom_api(f"/subscribers/{imsi}/status")

def get_subscriber(imsi):
    """
    SIMの詳細情報を取得する
    
    Args:
        imsi (str): IMSI
        
    Returns:
        dict: SIMの詳細情報
    """
    return call_soracom_api(f"/subscribers/{imsi}")

# ===== ソラカメ関連のAPI =====

def get_cameras():
    """
    ソラカメの一覧を取得する
    
    Returns:
        list: ソラカメの一覧
    """
    return call_soracom_api("/sora_cam/devices")

def get_camera(device_id):
    """
    ソラカメの詳細情報を取得する
    
    Args:
        device_id (str): デバイスID
        
    Returns:
        dict: ソラカメの詳細情報
    """
    return call_soracom_api(f"/sora_cam/devices/{device_id}")

def get_camera_live_stream_url(device_id):
    """
    ソラカメのライブストリームURLを取得する
    
    Args:
        device_id (str): デバイスID
        
    Returns:
        dict: ライブストリーム情報
    """
    return call_soracom_api(f"/sora_cam/devices/{device_id}/stream")

def request_video_export(device_id, start, end):
    """
    ソラカメの動画エクスポートをリクエストする
    
    Args:
        device_id (str): デバイスID
        start (str): 開始時刻（ISO 8601形式）
        end (str): 終了時刻（ISO 8601形式）
        
    Returns:
        dict: エクスポートジョブ情報
    """
    # ISO 8601形式の時刻をUNIXタイムスタンプ（ミリ秒）に変換
    from datetime import datetime
    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
    
    # 時間差を計算（秒）
    time_diff = (end_dt - start_dt).total_seconds()
    
    # 時間差が900秒（15分）を超える場合はエラー
    if time_diff > 900:
        raise Exception(f"エクスポート時間が長すぎます: {time_diff}秒（最大900秒）")
    
    # 未来の時刻を指定している場合は警告
    now = datetime.now()
    if start_dt > now or end_dt > now:
        print("警告: 未来の時刻が指定されています。過去の録画映像のみエクスポートできます。")
    
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    body = {
        "from": start_ms,
        "to": end_ms
    }
    return call_soracom_api(f"/sora_cam/devices/{device_id}/videos/exports", "POST", body)

def get_video_export_status(device_id, export_id=None):
    """
    ソラカメの動画エクスポートジョブのステータスを取得する
    
    Args:
        device_id (str): デバイスID
        export_id (str, optional): エクスポートジョブID。指定しない場合は全てのジョブを取得
        
    Returns:
        dict or list: エクスポートジョブのステータス
    """
    if export_id:
        # 特定のエクスポートジョブのステータスを取得
        return call_soracom_api(f"/sora_cam/devices/{device_id}/videos/exports/{export_id}")
    else:
        # デバイスの全てのエクスポートジョブを取得
        return call_soracom_api(f"/sora_cam/devices/{device_id}/videos/exports")

def download_video_export(device_id, export_id, output_path):
    """
    ソラカメの動画エクスポートをダウンロードする
    
    Args:
        device_id (str): デバイスID
        export_id (str): エクスポートジョブID
        output_path (str): 出力ファイルパス
    """
    # デバイスの全てのエクスポートジョブを取得
    exports = get_video_export_status(device_id)
    
    # 指定したエクスポートジョブを探す
    export_info = None
    for export in exports:
        if export.get('exportId') == export_id:
            export_info = export
            break
    
    if not export_info:
        raise Exception(f"エクスポートジョブが見つかりません: {export_id}")
    
    if export_info.get('status') != 'completed':
        raise Exception(f"エクスポートジョブがまだ完了していません: {export_info.get('status')}")
    
    download_url = export_info.get('url')
    if not download_url:
        raise Exception("ダウンロードURLが見つかりません")
    
    print(f"動画をダウンロード中: {download_url}")
    
    # URLがZIPファイルかどうかを確認
    is_zip = download_url.lower().endswith('.zip') or '.zip?' in download_url.lower()
    
    if is_zip:
        # 一時ファイルを作成してZIPをダウンロード
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_path = temp_file.name
            
            response = http.request('GET', download_url, preload_content=False)
            if response.status >= 400:
                raise Exception(f"ダウンロードエラー: {response.status}")
            
            # 一時ファイルにZIPを保存
            shutil.copyfileobj(response, temp_file)
            response.release_conn()
            
        try:
            # ZIPファイルを解凍
            print(f"ZIPファイルを解凍中...")
            with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                # ZIPファイル内のファイル一覧を取得
                file_list = zip_ref.namelist()
                
                if not file_list:
                    raise Exception("ZIPファイルが空です")
                
                # 動画ファイルを探す（.mp4, .avi, .movなど）
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
                video_files = [f for f in file_list if any(f.lower().endswith(ext) for ext in video_extensions)]
                
                if video_files:
                    # 最初の動画ファイルを出力パスに解凍
                    video_file = video_files[0]
                    print(f"動画ファイルを解凍: {video_file}")
                    
                    with zip_ref.open(video_file) as source, open(output_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                else:
                    # 動画ファイルが見つからない場合は最初のファイルを使用
                    first_file = file_list[0]
                    print(f"動画ファイルが見つからないため、最初のファイルを使用: {first_file}")
                    
                    with zip_ref.open(first_file) as source, open(output_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
            
            print(f"動画を保存しました: {output_path}")
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    else:
        # 通常のファイルとしてダウンロード
        response = http.request('GET', download_url, preload_content=False)
        if response.status >= 400:
            raise Exception(f"ダウンロードエラー: {response.status}")
        
        with open(output_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        response.release_conn()
        print(f"動画を保存しました: {output_path}")

def request_image_export(device_id, timestamp):
    """
    ソラカメの静止画エクスポートをリクエストする
    
    Args:
        device_id (str): デバイスID
        timestamp (str): 時刻（ISO 8601形式）
        
    Returns:
        dict: エクスポートジョブ情報
    """
    # ISO 8601形式の時刻をUNIXタイムスタンプ（ミリ秒）に変換
    from datetime import datetime
    timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    timestamp_ms = int(timestamp_dt.timestamp() * 1000)
    
    body = {
        "time": timestamp_ms
    }
    return call_soracom_api(f"/sora_cam/devices/{device_id}/images/exports", "POST", body)

def get_image_export_status(device_id, export_id=None):
    """
    ソラカメの静止画エクスポートジョブのステータスを取得する
    
    Args:
        device_id (str): デバイスID
        export_id (str, optional): エクスポートジョブID。指定しない場合は全てのジョブを取得
        
    Returns:
        dict or list: エクスポートジョブのステータス
    """
    if export_id:
        # 特定のエクスポートジョブのステータスを取得
        return call_soracom_api(f"/sora_cam/devices/{device_id}/images/exports/{export_id}")
    else:
        # デバイスの全てのエクスポートジョブを取得
        return call_soracom_api(f"/sora_cam/devices/{device_id}/images/exports")

def download_image_export(device_id, export_id, output_path):
    """
    ソラカメの静止画エクスポートをダウンロードする
    
    Args:
        device_id (str): デバイスID
        export_id (str): エクスポートジョブID
        output_path (str): 出力ファイルパス
    """
    # デバイスの全てのエクスポートジョブを取得
    exports = get_image_export_status(device_id)
    
    # 指定したエクスポートジョブを探す
    export_info = None
    for export in exports:
        if export.get('exportId') == export_id:
            export_info = export
            break
    
    if not export_info:
        raise Exception(f"エクスポートジョブが見つかりません: {export_id}")
    
    if export_info.get('status') != 'completed':
        raise Exception(f"エクスポートジョブがまだ完了していません: {export_info.get('status')}")
    
    download_url = export_info.get('url')
    if not download_url:
        raise Exception("ダウンロードURLが見つかりません")
    
    print(f"静止画をダウンロード中: {download_url}")
    
    response = http.request('GET', download_url, preload_content=False)
    if response.status >= 400:
        raise Exception(f"ダウンロードエラー: {response.status}")
    
    with open(output_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    
    response.release_conn()
    print(f"静止画を保存しました: {output_path}")

def wait_for_image_export_completion(device_id, export_id, timeout=600, interval=5):
    """
    静止画エクスポートジョブの完了を待つ
    
    Args:
        device_id (str): デバイスID
        export_id (str): エクスポートジョブID
        timeout (int): タイムアウト（秒）
        interval (int): ステータス確認間隔（秒）
        
    Returns:
        dict: エクスポートジョブ情報
    """
    start_time = time.time()
    while True:
        # デバイスの全てのエクスポートジョブを取得
        exports = get_image_export_status(device_id)
        
        # 指定したエクスポートジョブを探す
        export_info = None
        for export in exports:
            if export.get('exportId') == export_id:
                export_info = export
                break
        
        if not export_info:
            raise Exception(f"エクスポートジョブが見つかりません: {export_id}")
        
        status = export_info.get('status')
        
        if status == 'completed':
            print(f"エクスポートジョブが完了しました: {export_id}")
            return export_info
        elif status in ['failed', 'canceled']:
            raise Exception(f"エクスポートジョブが失敗しました: {status}")
        
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise Exception(f"エクスポートジョブがタイムアウトしました: {elapsed}秒経過")
        
        print(f"エクスポートジョブの状態: {status}, {int(elapsed)}秒経過")
        time.sleep(interval)

def get_image_snapshot(device_id, timestamp, output_path):
    """
    ソラカメの静止画を取得する
    
    Args:
        device_id (str): デバイスID
        timestamp (str): 時刻（ISO 8601形式）
        output_path (str): 出力ファイルパス
    """
    query = f"?timestamp={timestamp}" if timestamp else ""
    url = f"{config['endpoint']}/sora_cam/devices/{device_id}/snapshots{query}"
    
    headers = {}
    
    # 認証トークンがあれば使用する
    if config['auth']['api_key'] and config['auth']['token']:
        headers['X-Soracom-API-Key'] = config['auth']['api_key']
        headers['X-Soracom-Token'] = config['auth']['token']
    else:
        # 認証トークンがなければAPIキーとシークレットを使用する
        headers['X-Soracom-API-Key'] = config['auth']['auth_key_id']
        headers['X-Soracom-Token'] = config['auth']['auth_key']
    
    print(f"静止画を取得中: {url}")
    
    response = http.request('GET', url, headers=headers, preload_content=False)
    if response.status >= 400:
        error_text = response.data.decode('utf-8')
        raise Exception(f"静止画取得エラー: {response.status} - {error_text}")
    
    with open(output_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    
    response.release_conn()
    print(f"静止画を保存しました: {output_path}")

def wait_for_export_completion(device_id, export_id, timeout=600, interval=5):
    """
    エクスポートジョブの完了を待つ
    
    Args:
        device_id (str): デバイスID
        export_id (str): エクスポートジョブID
        timeout (int): タイムアウト（秒）
        interval (int): ステータス確認間隔（秒）
        
    Returns:
        dict: エクスポートジョブ情報
    """
    start_time = time.time()
    while True:
        # デバイスの全てのエクスポートジョブを取得
        exports = get_video_export_status(device_id)
        
        # 指定したエクスポートジョブを探す
        export_info = None
        for export in exports:
            if export.get('exportId') == export_id:
                export_info = export
                break
        
        if not export_info:
            raise Exception(f"エクスポートジョブが見つかりません: {export_id}")
        
        status = export_info.get('status')
        
        if status == 'completed':
            print(f"エクスポートジョブが完了しました: {export_id}")
            return export_info
        elif status in ['failed', 'canceled']:
            raise Exception(f"エクスポートジョブが失敗しました: {status}")
        
        elapsed = time.time() - start_time
        if elapsed > timeout:
            raise Exception(f"エクスポートジョブがタイムアウトしました: {elapsed}秒経過")
        
        print(f"エクスポートジョブの状態: {status}, {int(elapsed)}秒経過")
        time.sleep(interval)

def auth_with_api_key():
    """
    APIキーとシークレットを使用して認証する
    
    Returns:
        dict: 認証レスポンス
    """
    # 認証トークンをリセット
    config['auth']['api_key'] = None
    config['auth']['token'] = None
    
    url = f"{config['endpoint']}/auth"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    body = {
        'authKeyId': config['auth']['auth_key_id'],
        'authKey': config['auth']['auth_key'],
        'scope': 'SoraCam:* OAuth2:authorize'
    }
    
    try:
        encoded_body = json.dumps(body).encode('utf-8')
        response = http.request(
            'POST',
            url,
            body=encoded_body,
            headers=headers
        )
        
        if response.status >= 400:
            error_text = response.data.decode('utf-8')
            raise Exception(f"認証エラー: {response.status} - {error_text}")
        
        auth_response = json.loads(response.data.decode('utf-8'))
        
        # 認証トークンを設定
        config['auth']['api_key'] = auth_response.get('apiKey')
        config['auth']['token'] = auth_response.get('token')
        
        return auth_response
    except Exception as e:
        print(f"認証エラー: {str(e)}")
        raise

def main():
    """メイン関数"""
    try:
        # 設定ファイルがあれば読み込む
        import os
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'soracom-config.json')
        load_config(config_path)
        
        print('APIキーとシークレットで認証中...')
        auth_response = auth_with_api_key()
        print('認証成功:', auth_response)
        
        input("Enterキーを押すと、SIMの一覧を取得します...")
        print('SIMの一覧を取得中...')
        subscribers = get_subscribers()
        print(f"{len(subscribers)}件のSIMが見つかりました")
        
        if subscribers:
            input("Enterキーを押すと、最初のSIMの詳細を取得します...")
            first_sim = subscribers[0]
            print(f"最初のSIM ({first_sim['imsi']}) の詳細を取得中...")
            try:
                # SIM情報を取得
                subscriber_info = get_subscriber(first_sim['imsi'])
                print(f"SIM情報: {subscriber_info}")
                
                # get_subscriber_status関数は存在しないAPIを呼び出しているため削除
            except Exception as e:
                print(f"SIM詳細の取得に失敗しました: {str(e)}")
                print("これは特定のSIMに対するアクセス権限がない可能性があります。")
        
        input("Enterキーを押すと、ソラカメの一覧を取得します...")
        print('ソラカメの一覧を取得中...')
        try:
            cameras = get_cameras()
            print(f"{len(cameras)}件のソラカメが見つかりました")
            
            if cameras:
                input("Enterキーを押すと、最初のソラカメの詳細を取得します...")
                first_camera = cameras[0]
                print(f"最初のソラカメ ({first_camera['deviceId']}) の詳細を取得中...")
                camera_info = get_camera(first_camera['deviceId'])
                print(f"カメラ情報: {camera_info}")
        except Exception as e:
            print(f"ソラカメの取得に失敗しました: {str(e)}")
            print("これはソラカメのAPIにアクセスする権限がない可能性があります。")
            print("SAMユーザーに、SoraCam:*とOAuth2:authorizeの権限が必要です。")
    
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()