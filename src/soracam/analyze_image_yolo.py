#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YOLOを使用して画像内の物体を検出するスクリプト
"""

import os
import sys
import argparse
import json
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

def parse_args():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(description='YOLOを使用して画像内の物体を検出するスクリプト')
    
    # 画像ファイルの指定
    parser.add_argument('--image', required=True, help='解析する画像ファイルのパス')
    
    parser.add_argument('--output', required=True, help='解析結果を保存するファイルのパス')
    parser.add_argument('--model', default='yolov8n.pt', help='使用するモデル（例: yolov8n.pt, yolov8s.pt）')
    parser.add_argument('--conf', type=float, default=0.25, help='信頼度のしきい値（0-1）')
    parser.add_argument('--save-txt', action='store_true', help='検出結果をテキストファイルに保存する')
    
    return parser.parse_args()

# 出力ディレクトリの定義
DETECTION_RESULTS_DIR = os.path.join('runs', 'detect')

def load_model(model_name):
    """YOLOモデルを読み込む"""
    input("Enterキーを押すと、モデルを読み込みます...")
    print(f"モデル {model_name} を読み込み中...")
    
    try:
        # ultralyticsのYOLOクラスを使用してモデルを読み込む
        model = YOLO(model_name)
        print(f"モデルを正常に読み込みました: {model_name}")
        print(f"検出可能なオブジェクト: {model.names}")
        print(f"検出可能なオブジェクト数: {len(model.names)}")
        return model
    except Exception as e:
        print(f"モデルの読み込みに失敗しました: {str(e)}")
        raise Exception(f"モデル {model_name} の読み込みに失敗しました。")

def detect_objects(model, image_path, conf_threshold=0.25):
    """画像内の物体を検出する"""
    input("Enterキーを押すと、画像を解析します...")
    print(f"画像 {image_path} を解析中...")
    
    try:
        # 推論を実行
        results = model(image_path, conf=conf_threshold, save=True)
        
        # 検出結果を集計
        type_dict = {}
        for result in results:
            # 検出されたオブジェクトごとに処理
            for box in result.boxes:
                cls_id = int(box.cls.item())
                conf = box.conf.item()
                
                # クラス名を取得
                cls_name = model.names[cls_id]
                
                # 結果を表示
                print(f"検出: {cls_name}, 信頼度: {conf:.2f}")
                
                # 集計
                if cls_name in type_dict:
                    type_dict[cls_name] += 1
                else:
                    type_dict[cls_name] = 1
        
        print(f"検出結果の集計: {json.dumps(type_dict, indent=4, ensure_ascii=False)}")
        return results
    except Exception as e:
        print(f"物体検出に失敗しました: {str(e)}")
        raise Exception(f"画像 {image_path} の物体検出に失敗しました。")

def save_results(results, output_path, save_txt=False):
    """検出結果を保存する"""
    try:
        # 結果は既にsave=Trueで保存されているため、ここでは何もしない
        # 保存先は runs/detect/predict/ ディレクトリ
        
        # 保存されたファイルを指定の場所にコピー
        predict_dir = os.path.join('runs', 'detect', 'predict')
        if os.path.exists(predict_dir):
            # 最新の結果ファイルを探す
            result_files = [f for f in os.listdir(predict_dir) if f.endswith('.jpg') or f.endswith('.png')]
            if result_files:
                latest_file = os.path.join(predict_dir, result_files[0])
                # 結果をコピー
                import shutil
                shutil.copy(latest_file, output_path)
                print(f"解析結果を保存しました: {output_path}")
        
        # テキスト形式でも保存する場合
        if save_txt:
            txt_path = os.path.splitext(output_path)[0] + '.txt'
            try:
                with open(txt_path, 'w') as f:
                    for result in results:
                        for box in result.boxes:
                            cls_id = int(box.cls.item())
                            conf = box.conf.item()
                            xyxy = box.xyxy.tolist()[0]  # x1, y1, x2, y2
                            
                            # クラス名を取得
                            cls_name = results[0].names[cls_id]
                            
                            # クラス、信頼度、座標を保存
                            f.write(f"{cls_name} {conf:.4f} {xyxy[0]:.1f} {xyxy[1]:.1f} {xyxy[2]:.1f} {xyxy[3]:.1f}\n")
                print(f"検出結果をテキストファイルに保存しました: {txt_path}")
            except Exception as e:
                print(f"テキストファイルの保存中にエラーが発生しました: {str(e)}")
        
        return True
    except Exception as e:
        print(f"結果の保存に失敗しました: {str(e)}")
        return False

def print_detection_summary(results):
    """検出結果の概要を表示する"""
    try:
        # 検出されたオブジェクトの数をカウント
        type_dict = {}
        total_detections = 0
        
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                cls_name = result.names[cls_id]
                
                if cls_name in type_dict:
                    type_dict[cls_name] += 1
                else:
                    type_dict[cls_name] = 1
                
                total_detections += 1
        
        if total_detections == 0:
            print("物体は検出されませんでした。")
            return
        
        print("\n検出結果の概要:")
        print(f"合計 {total_detections} 個の物体を検出しました")
        
        for cls, count in type_dict.items():
            print(f"- {cls}: {count}個")
    except Exception as e:
        print(f"検出結果の表示中にエラーが発生しました: {str(e)}")

def main():
    """メイン関数"""
    args = parse_args()
    
    # 画像ファイルパスの設定
    image_path = args.image
    
    # 入力ファイルの存在確認
    if not os.path.isfile(image_path):
        print(f"エラー: 画像ファイル {image_path} が見つかりません")
        sys.exit(1)
    
    # 出力ディレクトリが存在しない場合は作成
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # モデルを読み込む
    model = load_model(args.model)
    
    input("Enterキーを押すと、物体検出を実行します...")
    # 物体検出を実行
    results = detect_objects(model, image_path, args.conf)
    
    # 検出結果の概要を表示
    print_detection_summary(results)
    
    # 結果を保存
    save_results(results, args.output, args.save_txt)
    
    print("解析が完了しました")

if __name__ == "__main__":
    main()