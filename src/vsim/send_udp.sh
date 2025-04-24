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
  
  echo "$data" | nc -u -w1 uni.soracom.io 23080
    
  echo -e "\n送信完了: $(date)"
}

# メイン処理
echo "UDP経由でセンサーデータを送信します..."
send_data