# 🚚 School Lunch Delivery Routing Optimization (学校給食 配送ルート最適化デモ)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://school-lunch-routing-opt-xn7z9qq5mrxqrafb8px7ly.streamlit.app/)

This project is a web-based simulation application that solves the **Multi-Depot Vehicle Routing Problem with Time Windows (MDVRPTW)**. It is specifically designed around a real-world business scenario: optimizing the school lunch delivery network for 28 schools in Tachikawa City, Tokyo.

[日本語版のREADMEはこちら](#-日本語版-japanese-version)

## 🌟 Key Features (English)

*   **Advanced AI Routing (OR-Tools)**: Utilizes Google's OR-Tools to solve the complex MDVRPTW in seconds, exploring millions of combinations to find the most cost-effective routes.
*   **Real-World Business Constraints**:
    *   **Time Windows**: Deliveries must be completed strictly between 11:00 and 11:30.
    *   **Hygiene Standards (2-Hour Rule)**: Trucks cannot depart before 10:30 to ensure food safety.
    *   **Service Time**: Accounts for a 10-minute unloading time at each school.
*   **Cost Savings Dashboard**: Automatically calculates and displays the estimated annual gasoline cost savings (and proportional CO2 emissions reduction) compared to naive round-trip deliveries.
*   **Interactive "What-If" Analysis**:
    *   Simulate bad weather conditions (e.g., 1.5x travel time during snow).
    *   Simulate driver shortages by dynamically adjusting the number of available trucks.
    *   Adjust AI computing time limits to see how it affects optimization quality.
*   **Beautiful Visualization**: Integrates Folium to draw interactive, color-coded routes directly on a real map.
*   **Bilingual UI**: Fully supports English and Japanese languages for global accessibility.

## 🛠️ Technology Stack
*   **Language**: Python 3.9+
*   **Frontend**: Streamlit, Streamlit-Folium
*   **Optimization Engine**: Google OR-Tools (`pywrapcp`)
*   **Data Processing**: Pandas, NumPy

## 🚀 How to Run Locally

1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run vrp_demo.py
   ```

---

# 🇯🇵 日本語版 (Japanese Version)

このプロジェクトは、**「時間枠付き複数拠点車両経路問題（MDVRPTW）」**を解くシミュレーションWebアプリケーションです。東京都立川市の学校給食配送ネットワーク（2拠点から28校への配送）という、極めて実務的なビジネスシナリオをベースに設計されています。

## 🌟 主な機能

*   **AIによる高度な経路最適化 (OR-Tools)**: Google OR-Toolsを活用し、数千万の組み合わせの中から最もコスト効率の良い配送ルートを数秒で探索します。
*   **現場のリアルな制約条件を完全再現**:
    *   **厳しい時間枠 (Time Windows)**: 11:00〜11:30の間に必ず配送を完了させる必要があります。
    *   **文科省の衛生管理基準**: 「調理完了から2時間以内の喫食」を守るため、10:30以降にしか出発できません。
    *   **作業時間の考慮**: 各学校での荷下ろし作業（10分間）もスケジュールに組み込んでいます。
*   **コスト削減額のダッシュボード可視化**: ピストン輸送を行った場合と比較した「年間のガソリン代節約額」をリアルタイムに計算し、ビジネスインパクト（ROI）を明確に提示します。
*   **What-If 分析（シミュレーション機能）**:
    *   天候悪化（雪で移動時間が1.5倍になる等）による遅延シミュレーション。
    *   ドライバー欠勤に伴う、稼働トラック数の動的変更とルート再構築。
    *   AIの探索時間（秒）を調整し、最適化の精度を動的に変更。
*   **インタラクティブな地図描画**: Foliumを使用し、東エリア・西エリアで色分けされた最適化ルートを地図上に美しく描画します。
*   **バイリンガル対応**: 日本語と英語のUI切り替え機能を完備しています。

## 🛠️ 技術スタック
*   **言語**: Python 3.9+
*   **フロントエンド**: Streamlit, Streamlit-Folium
*   **最適化エンジン**: Google OR-Tools (`pywrapcp`)
*   **データ処理**: Pandas, NumPy

## 🚀 ローカル環境での動かし方

1. リポジトリをクローンします。
2. 必要なライブラリをインストールします:
   ```bash
   pip install -r requirements.txt
   ```
3. Streamlitアプリを起動します:
   ```bash
   streamlit run vrp_demo.py
   ```
