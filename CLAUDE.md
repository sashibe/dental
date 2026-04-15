# CLAUDE.md — KIREI 歯科3Dデータ研究プロジェクト

## リポジトリ

https://github.com/sashibe/dental.git

## プロジェクト概要

KIREIは歯科医向けの矯正シミュレーション営業ツール。
その技術基盤（口腔内3Dスキャンデータの取得・保存・AI処理）を活用し、
**災害時の個人識別（法歯科学）** への展開を研究する。

共同パートナー: 山田正人先生（山田兄弟歯科院長）

## ゴール

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
    matching/            # 照合アルゴリズム
    evaluation/          # 評価スクリプト
  notebooks/             # 実験用Jupyter Notebook
  docs/                  # 資料（企画書、研究ノートなど）
  results/               # 実験結果
```

## 技術スタック

- Python 3.10+
- 3Dメッシュ処理: trimesh, open3d, pyvista
- 機械学習: PyTorch, PyTorch3D
- 可視化: matplotlib, plotly, meshlab（外部）
- データ管理: pandas, numpy

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
