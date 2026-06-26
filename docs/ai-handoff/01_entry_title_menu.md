# 入口/タイトル/特訓メニュー 引き継ぎ

## 担当ファイル

- `index.html`
- `nv_dft_viewer.html`
- 画像: `assets/title-idols/`, `assets/title-idols/backgrounds/`, `assets/chibis/`, `assets/ui/login-pop.svg`

## 役割

最初に開く画面です。女性アイドルのタイトル背景、ログインカレンダー、日誌、バックアップ、共有URL、特訓メニューへの入口をまとめています。

## 見るべきコード位置

- タイトル画面CSS: `index.html` の `.splash`, `.guide-portrait`, `.splash-copy`, `.login-panel`
- 特訓メニューCSS: `.training-hub`, `.training-grid`, `.training-card`
- タイトルキャラ定義: `TITLE_IDOLS`
- メニュー遷移先: `TRAINING_OPTIONS`
- カレンダー保存: `LOGIN_STORE_KEY`, `stampToday`, `renderLoginCalendar`, `copyLoginShareUrl`
- メニュー起動: `showTrainingHub`
- メニュークリック: `handleTrainingChoice`

## 重要仕様

- 「始める」はビューア直行ではなく、特訓メニューを開きます。
- 特訓メニューは1クリックでページへ入ります。以前の「1回目で説明、2回目で開始」には戻さない方針です。
- カレンダーと日誌は `localStorage` に保存します。
- 共有URLはハッシュにログインデータを入れる方式です。静的HTMLで完結させるため、サーバー保存はしていません。
- `index.html` を直したら `nv_dft_viewer.html` も同じ状態にしてください。

## よく壊れる点

- カレンダーがタイトル画像の顔を隠しすぎる。
- スマホ幅でタイトル、カレンダー、ボタンが縦にはみ出す。
- メニューカードの画像に白い膜をかけすぎて薄く見える。
- `TRAINING_OPTIONS.simulation` はURL遷移ではなく `startViewer()` を呼ぶ特別扱いです。

## 次に改修するなら

- タイトル背景キャラを増やす場合は `TITLE_IDOLS` に名前、画像パス、顔位置、セリフを足します。
- メニューを増やす場合は `TRAINING_OPTIONS` と `.training-grid` のカードHTMLを両方追加します。
- データ保存を強くするなら、JSONバックアップと共有URLの導線を目立たせます。
