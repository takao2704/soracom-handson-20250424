#!/bin/bash

# SORACOM Beam経由でUDPデータを送信するスクリプト
# SORACOMハンズオン用

# エラーが発生したら終了
set -e

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 引数の解析
HOST="uni.soracom.io"
PORT=23080
INTERVAL=5
COUNT=1

while getopts "h:p:i:c:?" opt; do
    case $opt in
        h)
            HOST="$OPTARG"
            ;;
        p)
            PORT="$OPTARG"
            ;;
        i)
            INTERVAL="$OPTARG"
            ;;
        c)
            COUNT="$OPTARG"
            ;;
        \?|?)
            echo "使用方法: $0 [-h ホスト] [-p ポート] [-i 送信間隔(秒)] [-c 送信回数]"
            echo "  -h: 送信先ホスト (デフォルト: $HOST)"
            echo "  -p: 送信先ポート (デフォルト: $PORT)"
            echo "  -i: 送信間隔（秒） (デフォルト: $INTERVAL)"
            echo "  -c: 送信回数 (デフォルト: $COUNT, 0の場合は無限に送信)"
            exit 0
            ;;
    esac
done

# センサーデータの生成
generate_sensor_data() {
    # 乱数を使って温度、湿度、位置情報を生成
    local temp=$(echo "scale=2; 20 + $(od -An -N1 -i /dev/urandom) % 10" | bc)
    local humidity=$(echo "scale=2; 40 + $(od -An -N1 -i /dev/urandom) % 30" | bc)
    local lat="35.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
    local lon="139.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
    
    # デバイスID（ホスト名を使用）
    local device_id=$(hostname)
    
    # 現在時刻（ISO 8601形式）
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # JSONデータの生成
    cat << EOF
{
  "device_id": "$device_id",
  "timestamp": "$timestamp",
  "payload": {
    "temperature": $temp,
    "humidity": $humidity,
    "location": {
      "lat": $lat,
      "lon": $lon
    }
  }
}
EOF
}

# データの送信
send_data() {
    local data=$(generate_sensor_data)
    
    log_info "送信データ:"
    echo "$data" | jq .
    
    log_info "SORACOM Beam経由でUDPデータを送信中... ($HOST:$PORT)"
    
    # netcatでデータを送信
    echo "$data" | nc -u -w1 "$HOST" "$PORT"
    
    # 送信結果の確認
    if [ $? -eq 0 ]; then
        log_success "送信完了: $(date)"
    else
        log_error "送信失敗: $(date)"
    fi
}

# netcatコマンドの確認
check_netcat() {
    if ! command -v nc &> /dev/null; then
        log_error "netcat (nc) コマンドがインストールされていません"
        log_info "sudo apt-get install -y netcat-openbsd でインストールしてください"
        exit 1
    fi
}

# メイン処理
main() {
    echo "================================================"
    echo "  SORACOM Beam経由でUDPデータを送信するスクリプト"
    echo "  SORACOMハンズオン用"
    echo "================================================"
    
    log_info "送信先: $HOST:$PORT"
    log_info "送信間隔: ${INTERVAL}秒"
    
    if [ "$COUNT" -eq 0 ]; then
        log_info "送信回数: 無限"
    else
        log_info "送信回数: $COUNT回"
    fi
    
    echo "================================================"
    
    # netcatコマンドの確認
    check_netcat
    
    # jqコマンドの確認
    if ! command -v jq &> /dev/null; then
        log_warning "jqコマンドがインストールされていません"
        log_info "sudo apt-get install -y jq でインストールしてください"
    fi
    
    # SORACOM Beamの説明
    log_info "SORACOM Beam UDP to HTTPSについて:"
    log_info "1. uni.soracom.io:23080はSORACOM BeamのUDPエンドポイントです"
    log_info "2. UDPデータはBeamによってHTTPSに変換されます"
    log_info "3. 転送先はSORACOMコンソールのBeam設定で指定します"
    log_info "4. UDPからHTTPSへの変換では、UDPデータがHTTPリクエストのボディになります"
    
    # データ送信
    local i=1
    while [ "$COUNT" -eq 0 ] || [ "$i" -le "$COUNT" ]; do
        if [ "$COUNT" -ne 0 ]; then
            log_info "データ送信 $i/$COUNT"
        else
            log_info "データ送信 $i"
        fi
        
        send_data
        
        if [ "$COUNT" -eq 0 ] || [ "$i" -lt "$COUNT" ]; then
            log_info "${INTERVAL}秒待機中..."
            sleep "$INTERVAL"
        fi
        
        i=$((i + 1))
    done
    
    echo "================================================"
    log_success "すべての送信が完了しました"
    echo "================================================"
}

# スクリプトの実行
main