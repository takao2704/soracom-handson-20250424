#!/bin/bash

# Raspberry Piセットアップスクリプト
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

# ルート権限チェック
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_error "このスクリプトはroot権限で実行する必要があります"
        log_info "sudo ./setup_raspi.sh を実行してください"
        exit 1
    fi
}

# システム情報の表示
show_system_info() {
    log_info "システム情報を取得しています..."
    
    echo "ホスト名: $(hostname)"
    echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
    echo "カーネル: $(uname -r)"
    echo "アーキテクチャ: $(uname -m)"
    
    # IPアドレス
    echo "ネットワーク情報:"
    ip -4 addr show | grep inet | grep -v "127.0.0.1" | awk '{print "  " $NF " - " $2}'
    
    # ディスク使用量
    echo "ディスク使用量:"
    df -h / | tail -n 1 | awk '{print "  " $1 " - " $2 " 合計, " $3 " 使用中, " $4 " 空き (" $5 ")"}'
    
    # メモリ使用量
    echo "メモリ使用量:"
    free -h | grep Mem | awk '{print "  " $2 " 合計, " $3 " 使用中, " $4 " 空き"}'
}

# パッケージの更新
update_packages() {
    log_info "パッケージリストを更新しています..."
    apt-get update
    
    log_info "システムをアップグレードしています..."
    apt-get upgrade -y
    
    log_success "パッケージの更新が完了しました"
}

# 必要なパッケージのインストール
install_required_packages() {
    log_info "必要なパッケージをインストールしています..."
    
    apt-get install -y \
        curl \
        wget \
        jq \
        netcat-openbsd \
        bc \
        mosquitto-clients \
        net-tools \
        dnsutils
    
    log_success "必要なパッケージのインストールが完了しました"
}

# ネットワーク接続テスト
test_network_connection() {
    log_info "ネットワーク接続をテストしています..."
    
    if ping -c 3 api.soracom.io > /dev/null 2>&1; then
        log_success "SORACOM APIサーバーに接続できました"
    else
        log_warning "SORACOM APIサーバーに接続できません"
    fi
    
    if ping -c 3 uni.soracom.io > /dev/null 2>&1; then
        log_success "SORACOM Beamサーバーに接続できました"
    else
        log_warning "SORACOM Beamサーバーに接続できません"
    fi
}

# vSIM設定ディレクトリの作成
create_vsim_config_dir() {
    log_info "vSIM設定ディレクトリを作成しています..."
    
    mkdir -p /etc/soracom
    chmod 755 /etc/soracom
    
    log_success "vSIM設定ディレクトリの作成が完了しました"
}

# サンプルvSIM設定ファイルの作成
create_sample_vsim_config() {
    log_info "サンプルvSIM設定ファイルを作成しています..."
    
    cat > /etc/soracom/vsim_config.json.sample << EOF
{
  "imsi": "YOUR_IMSI",
  "passcode": "YOUR_PASSCODE"
}
EOF
    
    chmod 644 /etc/soracom/vsim_config.json.sample
    
    log_success "サンプルvSIM設定ファイルの作成が完了しました"
    log_info "実際のvSIMを設定する場合は、/etc/soracom/vsim_config.jsonを作成し、IMSIとパスコードを設定してください"
}

# メイン処理
main() {
    echo "================================================"
    echo "  Raspberry Piセットアップスクリプト"
    echo "  SORACOMハンズオン用"
    echo "================================================"
    
    # ルート権限チェック
    check_root
    
    # システム情報の表示
    show_system_info
    
    echo "================================================"
    
    # パッケージの更新
    update_packages
    
    # 必要なパッケージのインストール
    install_required_packages
    
    # ネットワーク接続テスト
    test_network_connection
    
    # vSIM設定ディレクトリの作成
    create_vsim_config_dir
    
    # サンプルvSIM設定ファイルの作成
    create_sample_vsim_config
    
    echo "================================================"
    log_success "セットアップが完了しました"
    echo "================================================"
}

# スクリプトの実行
main