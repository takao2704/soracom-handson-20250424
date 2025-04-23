# vSIMを使ったAWSへのデータ送信ガイド

このガイドでは、SORACOMのvSIMを使用してRaspberry PiからAWSにセンサーデータを送信する方法を説明します。

## 前提条件

- SORACOMアカウントとAPIキー（setup-guide.mdを参照）
- OSインストール済みのRaspberry Pi
- SORACOMのvSIM
- インターネット接続環境

## 2.1 Raspberry Piのセットアップ

### OSの確認

1. Raspberry Piの電源を入れ、OSが正常に起動することを確認します。
2. ターミナルを開き、以下のコマンドでOSのバージョンを確認します：

```bash
cat /etc/os-release
```

### ネットワーク設定

1. 以下のコマンドを実行して、ネットワーク設定を確認します：

```bash
ip addr
```

2. Wi-FiまたはEthernetが正常に接続されていることを確認します。

### 必要なライブラリのインストール

1. 以下のコマンドを実行して、必要なパッケージをインストールします：

```bash
sudo apt update
sudo apt install -y curl netcat-openbsd jq
```

### セットアップスクリプトの実行

1. 以下のコマンドを実行して、セットアップスクリプトを実行します：

```bash
bash src/vsim/setup_raspi.sh
```

2. スクリプトが正常に完了したことを確認します。

## 2.2 vSIMの発行

### SORACOMコンソールでのvSIM発行

1. [SORACOMコンソール](https://console.soracom.io/)にログインします。
2. 左側のメニューから「SIM管理」を選択します。
3. 「SIMを登録」ボタンをクリックします。
4. 「仮想SIM（vSIM）を作成」を選択します。
5. 必要な情報を入力し、「登録」ボタンをクリックします。
6. 発行されたvSIMの情報（IMSI、パスコード）をメモします。

### Raspberry PiへのvSIM設定

1. 以下のコマンドを実行して、vSIMの設定ファイルを作成します：

```bash
cat > vsim_config.json << EOF
{
  "imsi": "あなたのIMSI",
  "passcode": "あなたのパスコード"
}
EOF
```

2. 設定ファイルを適切な場所に移動します：

```bash
sudo mkdir -p /etc/soracom
sudo mv vsim_config.json /etc/soracom/
```

### 接続テスト

1. 以下のコマンドを実行して、vSIMの接続をテストします：

```bash
curl -s https://api.soracom.io/v1/subscribers/$(cat /etc/soracom/vsim_config.json | jq -r .imsi) \
  -H "X-Soracom-API-Key: ${SORACOM_AUTH_KEY_ID}" \
  -H "X-Soracom-Token: ${SORACOM_AUTH_KEY}"
```

2. 正常にレスポンスが返ってくることを確認します。

## 2.3 SORACOMへのセンサ模擬データ送信（HTTP）

### センサーデータの生成と送信

1. 以下のコマンドを実行して、センサーデータを生成し送信します：

```bash
bash src/vsim/send_http.sh
```

2. スクリプトの内容は以下の通りです：

```bash
#!/bin/bash

# センサーデータの生成
generate_sensor_data() {
  local temp=$(echo "scale=2; 20 + $(od -An -N1 -i /dev/urandom) % 10" | bc)
  local humidity=$(echo "scale=2; 40 + $(od -An -N1 -i /dev/urandom) % 30" | bc)
  local lat="35.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  local lon="139.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  
  cat << EOF
{
  "temperature": $temp,
  "humidity": $humidity,
  "location": {
    "lat": $lat,
    "lon": $lon
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# データの送信
send_data() {
  local data=$(generate_sensor_data)
  echo "送信データ: $data"
  
  curl -X POST \
    -H "Content-Type: application/json" \
    -d "$data" \
    https://api.soracom.io/v1/devices/data
    
  echo -e "\n送信完了: $(date)"
}

# メイン処理
echo "HTTP経由でセンサーデータを送信します..."
send_data
```

### データ送信の確認

1. SORACOMコンソールにログインします。
2. 左側のメニューから「デバイス」を選択します。
3. 送信したデータが表示されていることを確認します。

## 2.4 SORACOMへのセンサ模擬データ送信（UDP）(+alpha)

### UDPプロトコルの基本

UDPは軽量で低遅延の通信プロトコルです。接続確立のオーバーヘッドがなく、IoTデバイスに適しています。

### データの送信

1. 以下のコマンドを実行して、UDPでセンサーデータを送信します：

```bash
bash src/vsim/send_udp.sh
```

2. スクリプトの内容は以下の通りです：

```bash
#!/bin/bash

# センサーデータの生成
generate_sensor_data() {
  local temp=$(echo "scale=2; 20 + $(od -An -N1 -i /dev/urandom) % 10" | bc)
  local humidity=$(echo "scale=2; 40 + $(od -An -N1 -i /dev/urandom) % 30" | bc)
  local lat="35.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  local lon="139.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  
  cat << EOF
{
  "temperature": $temp,
  "humidity": $humidity,
  "location": {
    "lat": $lat,
    "lon": $lon
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# データの送信
send_data() {
  local data=$(generate_sensor_data)
  echo "送信データ: $data"
  
  echo "$data" | nc -u -w1 udp.soracom.io 23080
    
  echo -e "\n送信完了: $(date)"
}

# メイン処理
echo "UDP経由でセンサーデータを送信します..."
send_data
```

### 送信確認

1. SORACOMコンソールにログインします。
2. 左側のメニューから「ログ」を選択します。
3. UDPで送信したデータのログが表示されていることを確認します。

## 2.5 SORACOM Beamを介したデータ送信（HTTP to HTTPS）

### SORACOM Beamの設定

1. SORACOMコンソールにログインします。
2. 左側のメニューから「グループ」を選択します。
3. 使用するグループを選択するか、新しいグループを作成します。
4. 「SORACOM Beam設定」を選択します。
5. 「追加」ボタンをクリックします。
6. 以下の設定を行います：
   - エントリ名: 任意の名前
   - 転送先サービス: AWS IoT
   - 転送先URL: AWSから提供されたエンドポイント
   - 認証情報: AWSから提供された認証情報
7. 「保存」ボタンをクリックします。

### データの送信

1. 以下のコマンドを実行して、Beam経由でデータを送信します：

```bash
bash src/vsim/send_beam_http.sh
```

2. スクリプトの内容は以下の通りです：

```bash
#!/bin/bash

# センサーデータの生成
generate_sensor_data() {
  local temp=$(echo "scale=2; 20 + $(od -An -N1 -i /dev/urandom) % 10" | bc)
  local humidity=$(echo "scale=2; 40 + $(od -An -N1 -i /dev/urandom) % 30" | bc)
  local lat="35.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  local lon="139.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  
  cat << EOF
{
  "temperature": $temp,
  "humidity": $humidity,
  "location": {
    "lat": $lat,
    "lon": $lon
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# データの送信
send_data() {
  local data=$(generate_sensor_data)
  echo "送信データ: $data"
  
  curl -X POST \
    -H "Content-Type: application/json" \
    -d "$data" \
    https://uni.soracom.io/
    
  echo -e "\n送信完了: $(date)"
}

# メイン処理
echo "SORACOM Beam経由でセンサーデータを送信します..."
send_data
```

### AWSでの確認

1. AWSマネジメントコンソールにログインします。
2. 提供されたAWSサービス（DynamoDB、S3など）にアクセスします。
3. 送信したデータが保存されていることを確認します。

## 2.6 SORACOM Beamを介したデータ送信（UDP to HTTPS）(+alpha)

### UDP to HTTPS変換の設定

1. SORACOMコンソールにログインします。
2. 左側のメニューから「グループ」を選択します。
3. 使用するグループを選択します。
4. 「SORACOM Beam設定」を選択します。
5. 「追加」ボタンをクリックします。
6. 以下の設定を行います：
   - エントリ名: 任意の名前
   - プロトコル: UDP
   - 転送先サービス: AWS IoT
   - 転送先URL: AWSから提供されたエンドポイント
   - 認証情報: AWSから提供された認証情報
7. 「保存」ボタンをクリックします。

### データの送信

1. 以下のコマンドを実行して、UDP経由でBeamにデータを送信します：

```bash
bash src/vsim/send_beam_udp.sh
```

2. スクリプトの内容は以下の通りです：

```bash
#!/bin/bash

# センサーデータの生成
generate_sensor_data() {
  local temp=$(echo "scale=2; 20 + $(od -An -N1 -i /dev/urandom) % 10" | bc)
  local humidity=$(echo "scale=2; 40 + $(od -An -N1 -i /dev/urandom) % 30" | bc)
  local lat="35.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  local lon="139.$(od -An -N2 -i /dev/urandom | tr -d ' ')"
  
  cat << EOF
{
  "temperature": $temp,
  "humidity": $humidity,
  "location": {
    "lat": $lat,
    "lon": $lon
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# データの送信
send_data() {
  local data=$(generate_sensor_data)
  echo "送信データ: $data"
  
  echo "$data" | nc -u -w1 uni.soracom.io 23080
    
  echo -e "\n送信完了: $(date)"
}

# メイン処理
echo "UDP経由でSORACOM Beamにセンサーデータを送信します..."
send_data
```

### 応用例

- 複数のセンサーデータを定期的に送信する
- バッテリー残量や信号強度などの追加情報を含める
- 異常値検出時に特別なフラグを立てる

## トラブルシューティング

### vSIM接続エラー

- vSIMの設定が正しいか確認してください。
- vSIMが有効化されているか確認してください。
- ネットワーク接続を確認してください。

### データ送信エラー

- エンドポイントが正しいか確認してください。
- データ形式が正しいか確認してください。
- SORACOM Beamの設定が正しいか確認してください。

### AWSでのデータ確認エラー

- AWSの認証情報が正しいか確認してください。
- SORACOM BeamからAWSへの接続が正しく設定されているか確認してください。
- AWSのサービス（DynamoDB、S3など）が正しく設定されているか確認してください。