# CLAUDE.md — KIREI 歯科3Dデータ研究プロジェクト

## リポジトリ

https://github.com/sashibe/dental.git

## プロジェクト概要

KIREIは歯科医向けの矯正シミュレーション営業ツール。
その技術基盤（口腔内3Dスキャンデータの取得・保存・AI処理）を活用し、
**災害時の個人識別（法歯科学）** への展開を研究する。

共同パートナー: 山田正人先生（山田兄弟歯科院長）

## プロダクトビジョン（3レイヤー構想）

### Layer 1: 矯正シミュレーション営業ツール（0-6ヶ月）
- **最重要差別化: ClinCheck級の精度 × SmileFy AVA級の顔貌動画**

#### 入力データ（2段階）
- **2D入力（標準）**: 口腔内カメラ写真（9枚構成: 正面・左右・上下咬合面など）+ パノラマレントゲン
  - 3Dスキャナーを持っていない歯科医院でもシミュレーション可能
  - 68,000院すべてが潜在顧客になる
- **3D入力（高精度）**: 口腔内3Dスキャンデータ（STL/PLY/OBJ）
  - 3Dスキャナー導入済み医院ではさらに精度が向上
  - 全メーカー対応（Medit, iTero, 3Shape TRIOS, その他）

#### 処理フロー
- 2D/3Dデータ取込 → AI歯牙識別 → 矯正シミュレーション → ホワイトニング → 顔貌動画生成

#### 顔貌シミュレーション動画
- 口腔内データ（2Dまたは3D）から歯の移動を計算
- その結果を患者の顔写真に反映（モーフィング）して動画を生成
- 競合（SmileFy AVA等）は顔写真だけで合成 → 口腔内データ不使用、根拠なし
- KIREIは「実際のあなたの歯から計算した予測」と説明できる唯一のツール
- 治療前→1ヶ月→3ヶ月→...→完了の顔貌変化を動画で出力
- 患者がスマホで見返せる・家族に共有できる動画

### Layer 2: 治療経過トラッキング（6-12ヶ月）
- 毎月の健診時に3Dスキャン+顔写真を記録、タイムラインで経過を可視化
- 治療計画との差分アラート、SmileCheck連携

### Layer 3: 診療プラットフォーム（12ヶ月-）
- 会話録音 → Whisper文字起こし → Claude APIカルテ生成 → ORCA連携 → 会計
- 蓄積された3Dデータを防災インフラとして自治体・警察と連携（別途研究）

## 競合環境と差別化戦略

### 主要競合
| サービス | 入力 | 機能 | KIREIとの差 |
|---------|------|------|-----------|
| ClinCheck (Align) | iTero 3Dスキャン | 3D歯列矯正アニメーション | 精密だが口腔内3Dのみ。顔貌動画なし。iTero+インビザライン専用 |
| SmileFy AVA | 顔写真のみ | AI顔貌シミュレーション動画 | 動画品質は高いが口腔内データ不使用。根拠なし、盛り過ぎる |
| denta.bot | 顔写真のみ | AI Smile Simulator + 動画 | 同上。写真だけで合成 |
| Medit Smile Design | 2D顔写真 | スマイルデザイン（無料） | 静止画のみ、Medit Link内アプリ |
| Medit Ortho Simulation | 3Dスキャン | 歯列移動シミュレーション（無料） | 簡易的、顔貌なし |
| 3Shape Smile Design | TRIOS 3Dスキャン | スマイルデザイン | 3Shape専用、高価 |
| **KIREI** | **2D写真 or 3Dスキャン** | **口腔内データ連動の顔貌動画** | **両方対応は唯一** |

### KIREIの差別化ポイント
1. **ClinCheck級の精度 × SmileFy AVA級の顔貌動画**
   - ClinCheck: 治療計画として精密だが口の中の3Dモデルしか見せられない
   - SmileFy AVA: きれいな顔貌動画は出るが、顔写真だけが入力で口腔内データ不使用。歯科医学的根拠がなく"盛り過ぎ"になる
   - KIREI: 口腔内データ（2Dまたは3D）から歯の移動を計算し、その物理的な結果を顔貌動画として出力。「実際のあなたの歯から計算した予測」と説明できる
   - 歯科医にとっては営業ツールであると同時に、臨床的に誠実なツール
2. **2D画像でも動作** — 口腔内写真+レントゲンがあればシミュレーション可能。3Dスキャナー不要で68,000院すべてが潜在顧客
3. **全スキャナー対応** — 3Dデータがあれば精度向上。STL/PLY/OBJを出力できる全メーカーに対応。特定ハードウェアに依存しない
4. **日本市場特化** — 日本語UI、日本人顔貌AIモデル、ORCA連携
5. **Layer 2・3** — 治療経過トラッキング、音声カルテ生成は競合にない

### ハードウェア戦略
- **スキャナー非依存**: 2D画像（口腔内写真+レントゲン）でも動作 → 全歯科医院が対象
- **全メーカー対応**: STL/PLY/OBJを出力できる全スキャナーに対応（Medit, iTero, 3Shape TRIOS, Planmeca, Shining 3D等）
- **推奨スキャナー**: Medit i900 / i900M（iPad対応、オープンデータ、コスパ良）
- iTeroはAlignのデータ囲い込み（Invisalignモードでエクスポート不可）があるが、iRecordモードなら対応可
- Medit日本代理店: トクヤマデンタル → デモ機貸出を打診予定
- Medit提携が成功すれば公式アプリ採用の可能性もあるが、汎用性を優先し特定メーカーに依存しない設計とする

## ゴール

### KIREI プロダクト
1. 3Dスキャンデータ+顔写真から顔貌シミュレーション動画を生成するプロトタイプ開発
2. 矯正の全ステージ（月次）を顔貌変化として動画出力する機能の実装
3. 山田兄弟歯科での実症例PoCと効果測定

### 研究（災害時個人識別）
1. 口腔内3Dスキャンデータ（STL/OBJ）を用いた個人識別の技術検証（PoC）
2. 生前スキャン（AM: ante mortem）と死後スキャン（PM: post mortem）の自動照合アルゴリズムの開発
3. 将来的に歯科医院のデータをDB化し、自治体・警察との連携基盤を構築

## 使用データセット

### Teeth3DS+（メイン）
- 出典: MICCAI 2022/2024 チャレンジ公式データ
- 規模: 900名 / 1,800スキャン / 23,999本の歯（アノテーション付き）
- 形式: STL, OBJ, JSON（セグメンテーションラベル+FDI番号）
- 保存先: `datasets/teeth3ds/`
- URL: https://osf.io/xctdy/

### 矯正前後ペアデータ（サブ）
- 出典: Scientific Data (Nature) 論文付属データ
- 規模: 435名 / 1,060ペア（治療前後）
- 形式: STL
- 保存先: `datasets/ortho_pairs/`
- URL: https://zenodo.org/records/11392406
- 備考: DUA承認制（清華大学 Liu教授宛に申請済み）

### 参考データセット（将来の拡張候補）

#### マルチモーダル歯科データセット
- 出典: Scientific Data (Nature), 2024
- 規模: 169名 / CBCT 329スキャン + パノラマX線 + 根尖X線
- 用途: AM（口腔内スキャン）× PM（CBCT）のクロスモダリティ照合研究
- URL: https://doi.org/10.13026/s5z3-2766

#### MMDental
- 出典: Scientific Data (Nature), 2025
- 規模: 660名 / 3D CBCT + 詳細な医療記録（診断・フォローアップ）
- 用途: 歯の経年変化モデリング、治療歴と3D形状の対応学習
- URL: https://www.nature.com/articles/s41597-025-05398-7

#### STS-Tooth
- 出典: Scientific Data (Nature), 2025
- 規模: パノラマX線 4,000枚 + CBCT 148,400スキャン（アノテーション付き）
- 用途: セグメンテーションモデルの大規模事前学習
- URL: https://www.nature.com/articles/s41597-024-04306-9

#### FDTooth
- 出典: Scientific Data (Nature), 2025
- 規模: 口腔内写真 + CBCT ペアデータ
- 用途: 2D-3Dマッチング手法の参考、歯のセグメンテーション・レジストレーション
- URL: https://www.nature.com/articles/s41597-025-05348-3

## ディレクトリ構成

```
~/dental/                # https://github.com/sashibe/dental.git
  CLAUDE.md              # このファイル
  datasets/
    teeth3ds/            # Teeth3DS+ データ（メイン）
      Upper/
      Lower/
    ortho_pairs/         # 矯正前後ペアデータ（DUA承認待ち）
  pretrained/
    meshmae/             # MeshMAE事前学習済みモデル
  external/
    TADPM/               # 拡散モデル参考実装
  src/                   # ソースコード
    preprocessing/       # データ前処理（STL読み込み、メッシュ正規化）
      prepare_demo_mesh.py  # デモ用メッシュ簡略化・結合
    image_analysis/      # 2D画像解析（口腔内写真・レントゲンからの歯牙検出）
    matching/            # 照合アルゴリズム
    simulation/          # 矯正シミュレーション（ステージ別歯列生成）
    face_morphing/       # 顔貌モーフィング（3D→顔写真反映）
    video_gen/           # 顔貌シミュレーション動画生成
    evaluation/          # 評価スクリプト
  docs/                  # 資料（企画書、デモ、研究ノートなど）
    kirei_demo.html      # デモHTML（5ステップ）
    images/              # デモ用顔画像（Before/After各3アングル）
    demo_rebuild_plan.md # デモ設計仕様
  notebooks/             # 実験用Jupyter Notebook
  results/               # 実験結果
```

## 技術スタック

- Python 3.10+
- 3Dメッシュ処理: trimesh, open3d, pyvista
- 2D画像解析: OpenCV、歯牙セグメンテーション（SAM/YOLO等）
- 2D→3D復元: 口腔内写真からの歯列3D推定（将来検討: NeRF, Gaussian Splatting等）
- 機械学習: PyTorch, PyTorch3D
- 顔貌処理: MediaPipe（顔ランドマーク）、dlib
- 動画生成: OpenCV、ffmpeg、将来的にAI動画生成（Stable Video Diffusion等）
- 可視化: matplotlib, plotly, meshlab（外部）、Three.js（デモ用）
- データ管理: pandas, numpy
- カルテ生成（Layer 3）: Whisper API、Claude API

## コーディング規約

- 言語: Python（コード内コメントは英語、docstringは英語）
- ドキュメント・READMEは日本語OK
- 型ヒント必須
- フォーマッター: black
- リンター: ruff
- テスト: pytest
- STLファイルのパスはハードコードせず、設定ファイルまたは引数で渡す

## 注意事項

- 3Dスキャンデータは患者データ（匿名化済み）を含むため、公開リポジトリにデータ自体をpushしない
- `.gitignore` に `datasets/`, `pretrained/`, `external/` を必ず含める
- 実験結果のメトリクスは `results/` にJSON形式で保存し、再現可能にする

## 開発ロードマップ

### Phase 1: デモ・PoC（0-3ヶ月） ← 現在ここ
- [x] Teeth3DS+データでの3D歯列表示デモ
- [x] AI歯牙識別（FDIラベルによる色分け表示）
- [x] 矯正シミュレーション（歯の移動アニメーション）
- [x] ホワイトニングシミュレーション（10段階シェード）
- [x] 顔貌プレビュー（Before/Afterスライダー、3アングル）
- [ ] 矯正ステージ別タイムラインアニメーション（月次）
- [ ] 3Dスキャン→顔写真モーフィング連動
- [ ] 顔貌シミュレーション動画出力（MP4）
- [ ] 山田兄弟歯科での実症例PoC

### Phase 2: MVP開発（3-6ヶ月）
- [ ] AI動画生成の統合（表情の動きを付加）
- [ ] Meditスキャナー連携（STL直接インポート）
- [ ] 患者向け動画共有リンク生成
- [ ] 治療経過タイムライン（Layer 2基盤）
- [ ] ベータテスト（5-10院）

### Phase 3: 正式ローンチ（6-12ヶ月）
- [ ] SaaS提供開始
- [ ] ORCA連携（Layer 3基盤）
- [ ] 音声カルテ生成（Whisper + Claude API）
- [ ] 学会・展示会PR

## 参考論文

### 法歯科学・3D照合
- DoC+SHOT keypoint matching for forensic odontology identification (ScienceDirect, 2025.04)
- Automatic soft tissue removal from 3D dental scans (Scientific Reports, 2024.05)
- 3D imaging for dental identification using segmentation (Springer Nature, 2025.03)
- 3D dental superimposition approaches: a scoping review (Forensic Science International, 2024.12)
- Dental identification using 3D printed teeth following a mass fatality incident (J Forensic Radiol Imag, 2019)
- Forensic odontology in DVI: current practice and recent advances (Forensic Sciences Research, 2019)

### データセット・ベンチマーク
- Ben-Hamadou et al., "Teeth3DS+: an extended benchmark for intraoral 3D scans analysis" (MICCAI 2022/2024)
- Wang et al., "A 3D dental model dataset with pre/post-orthodontic treatment" (Scientific Data, 2024)
- Lei et al., "Automatic tooth arrangement with joint features via diffusion probabilistic models" (CAGD, 2024)

### 事前学習モデル
- MeshMAE: ShapeNet事前学習済みバックボーン（`pretrained/meshmae/`に保存済み）
- TADPM: 拡散モデルによる歯列矯正シミュレーション（`external/TADPM/`にクローン済み）

### 競合・参考サービス
- ClinCheck (Align Technology): インビザライン専用3Dシミュレーション、世界100カ国・1,000万症例データ
- SmileFy AVA: 写真→AI動画シミュレーション生成（年$900-$3,999）
- denta.bot: AI Smile Simulator + 動画生成、ホワイトラベル対応
- Medit Smile Design: 2D顔写真ベースのスマイルデザイン（Medit Link無料アプリ）
- Medit Ortho Simulation: 歯列移動シミュレーション（Medit Link無料アプリ）
- 3Shape Smile Design: TRIOS連携スマイルデザイン + Treatment Simulator
- Smilecloud: AI動画シミュレーション + チームコラボ機能
- DentalMonitoring: 遠隔モニタリングAI（ユニコーン企業）
