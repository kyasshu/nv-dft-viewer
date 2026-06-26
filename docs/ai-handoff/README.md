# AI引き継ぎ書インデックス

このフォルダは、他のAIに `nv-dft-viewer-standalone` を編集させるための入口です。

## まず見る場所

- 公開用プロジェクト本体: `C:\Users\22345\OneDrive\ドキュメント\nv-dft-viewer-standalone`
- 入口ページ: `index.html`
- 同期用入口ページ: `nv_dft_viewer.html`
- 個別ページ: `pages/`
- 画像素材: `assets/`
- DFT/QE入力: `qe/`, `scripts/`

## アプリ別引き継ぎ書

- [01_entry_title_menu.md](01_entry_title_menu.md): タイトル、ログインカレンダー、特訓メニュー
- [02_nv_simulation_viewer.md](02_nv_simulation_viewer.md): NV中心DFTモデル解析ビューア、3D/2Dシミュレーション
- [03_research_plan.md](03_research_plan.md): 研究計画ページ
- [04_references.md](04_references.md): 参考文献ツリー
- [05_equipment_manual.md](05_equipment_manual.md): 装置操作マニュアル
- [06_minigames.md](06_minigames.md): ミニゲーム
- [07_assets_and_style.md](07_assets_and_style.md): 画像素材、キャラ、UIトーン、生成素材の扱い

## 作業ルール

- このプロジェクトは静的HTML中心です。通常はビルド不要です。
- `index.html` を直したら、同じ内容を `nv_dft_viewer.html` に同期してください。
- 画像は `assets/` 以下に置き、`C:\Users\22345\.codex\generated_images\...` の生成元だけを参照しないでください。
- ミニゲームやタイトルのキャラは、既存の絵柄と服装を崩さない方針です。
- 研究内容の説明では、「Vが電子を捕まえてNを引き寄せる」という説明に戻さないでください。正しくは `N_i + V1 + V2` 欠陥複合体全体の励起、電荷状態/結合状態変化、ポテンシャル面変化、`N_i -> N_s` 再構成、隣接 `V2` が残ってNV中心形成、という流れです。

## 確認方法

ローカルサーバーが動いている場合:

```powershell
http://127.0.0.1:8777/index.html
```

サーバーがない場合は、プロジェクト直下で簡易サーバーを起動します。

```powershell
python -m http.server 8777
```

主な確認項目:

- タイトルから「始める」を押して特訓メニューへ入れる。
- 特訓メニューの各カードは1クリックで目的ページへ入る。
- `pages/minigames.html` はPC/スマホ幅で横にはみ出さない。
- シミュレーションは3D、完全2D、深さ表、式説明が表示される。
- 参考文献、研究計画、装置マニュアルの入力内容が `localStorage` に保存される。
