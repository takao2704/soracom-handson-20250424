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
2. sshクライアントで、pi@raspberrypi.localに接続します。

```bash
ssh pi@raspberrypi.local
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
sudo apt install wireguard
```

## 2.2 vSIMの発行

### SORACOMコンソールでのvSIM発行

こちらの手順に従って、プライマリサブスクリプションのバーチャル SIM/Subscriberを発行します。

https://users.soracom.io/ja-jp/docs/arc/create-virtual-sim-and-connect-with-wireguard/

### Raspberry PiへのvSIM設定

1. 発行したvSIMの接続情報を、
`/etc/wireguard/wg0.conf`に保存します。

2. wireguardインターフェースを作成し、SORACOMに接続します。
```bash
sudo wg-quick up wg0
```

### 接続テスト

1. 以下のコマンドを実行して、vSIMの接続をテストします：

```bash
ping pong.soracom.io
```

2. 正常にレスポンスが返ってくることを確認します。

## 2.3 SORACOMへのセンサ模擬データ送信（HTTP）

### SORACOM Harvest Dataの有効化
1. 下記のガイドに従って、SORACOM Harvest Dataを有効化します：

https://users.soracom.io/ja-jp/docs/harvest/enable-data/

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
  "lat": $lat,
  "lon": $lon
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
    http://uni.soracom.io:80
    
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
  "lat": $lat,
  "lon": $lon
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

1. 以下のコマンドを実行して、HTTPでFunnelにデータを送信します：
（先ほどと同じ）
```bash
bash src/vsim/send_http.sh
```

## 2.5 SORACOM Funnelを介したデータ送信（HTTP to HTTPS）

### HTTP to HTTPS SORACOM Funnelの設定

1. SORACOMコンソールにログインします。
2. 下記を参考にHTTP to HTTPSのSORACOM Funnelを設定します：
https://users.soracom.io/ja-jp/docs/funnel/aws-iot/#%e3%82%b9%e3%83%86%e3%83%83%e3%83%97-3-funnel-%e3%82%92%e3%82%bb%e3%83%83%e3%83%88%e3%82%a2%e3%83%83%e3%83%97%e3%81%99%e3%82%8b

### AWSでの確認

1. AWSマネジメントコンソールにログインします。
2. テストクライアントで確認します。

## 2.6 SORACOM Beamを介したデータ送信（UDP to HTTPS）(+alpha)

### UDP to HTTPS変換のSORACOM Funnelの設定

1. SORACOMコンソールにログインします。
2. 下記を参考にUDP to HTTPSのSORACOM Funnelを設定します：
https://users.soracom.io/ja-jp/docs/funnel/aws-iot/#%e3%82%b9%e3%83%86%e3%83%83%e3%83%97-3-funnel-%e3%82%92%e3%82%bb%e3%83%83%e3%83%88%e3%82%a2%e3%83%83%e3%83%97%e3%81%99%e3%82%8b


### データの送信

1. 以下のコマンドを実行して、UDP経由でBeamにデータを送信します：
（先ほどと同じ）
```bash
bash src/vsim/send_udp.sh
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