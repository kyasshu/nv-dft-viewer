# ミニゲーム 引き継ぎ

## 担当ファイル

- `pages/minigames.html`
- 背景/説明画像: `assets/minigames/crops/`
- 透過キャラ/小物: `assets/minigames/transparent/`
- 生成元シート: `assets/minigames/sources/`

## 役割

研究アプリ内の息抜き/特訓ゲームです。現在は4種類あります。

- 走る特訓
- ジャンプリズム
- 刹那の見切り
- 四色記憶

## 見るべきコード位置

- ゲーム一覧: `GAMES`
- 画面切替: `showView`, `showSelect`, `showHowto`, `startSelectedGame`
- HUD: `renderHud`
- 走る特訓: `startRunner`
- ジャンプリズム: `startJump`
- 刹那の見切り: `startReflex`
- 四色記憶: `startMemory`
- クリック/タッチイベント: 最後の `document.addEventListener('click', ...)`

## 重要仕様

- ゲーム選択は1クリックで開始します。
- ボタン操作ではなく、マウス/タッチで完結する操作を優先します。
- ミニゲームは研究クイズ化しすぎず、遊びとして気持ちよく触れる方向を優先します。
- プレイ中は `body.playing` になり、ヘッダーを消して全画面ステージにします。
- 数値HUDは右側の別ウィンドウではなく、ステージ内の `.stage-hud` に重ねます。
- キャラは同一キャラのポーズ差分に見えるよう、`assets/minigames/transparent/idol-*.png` を使います。
- 選択画面はライブカード風で、`data-best` にベストスコアを表示します。
- 選択画面では `host-panel` でギャル担当の海崎リナを案内役にしています。
- `data-select-idea` のカードは追加ゲーム案です。クリックすると `showIdea` で企画メモを表示します。
- 選択画面上部の `#dailySummary` に今日のプレイ記録を表示します。
- 各ゲーム開始時は `showLessonStart` で短い開始演出を出します。
- 各ゲーム終了時は `showResult` でランク、キャラ一言、今日のベストを表示します。
- 今日の記録は `localStorage` の `nvDftMinigameDaily.v2` に保存します。
- プレイ中のスコア表示は下の白い帯にしないこと。`.stage-hud` は上部の透明HUDとして使います。
- 各ゲームには `coachName`, `coachLine`, `coach`, `chibi` を持たせ、担当キャラを変えています。
- 走る特訓は2レーンの計算選択ゲームです。左右に `+` と `×` のゲートが出て、頭上の `POWER` を伸ばします。
- 走る特訓は10回選択後に `FINAL BOSS` と戦い、`POWER >= BOSS HP` なら撃破です。
- `gatePlan` は低い数字では `+`、高い数字では `×` が強くなるように調整しています。難易度調整はここを触ります。
- 走る特訓では `.power-bubble`, `.gate-pair`, `.math-gate`, `.runner-boss` を使います。
- ジャンプリズムは長押しジャンプの障害物回避ゲームです。
- ジャンプリズムでは `jump-run-a.png` と `jump-run-b.png` を交互表示して走りモーションにし、空中だけ `jump-jump.png` に切り替えます。
- ジャンプリズムの高度は `startPress`, `endPress`, `holdMs`, `vy`, `y` で制御します。短押しは低く、長押しは高く飛びます。
- ジャンプリズムの障害物は `obstacles` 配列の `clear` が必要高度です。難易度は `clear`, `spawnGap`, `speed`, `finishDistance` を触ります。
- ジャンプリズムの専用画像は `assets/minigames/jump/` にあります。
- 刹那の見切りは `dojo-flash` と `slash-effect` で合図/斬撃の演出を入れています。
- 刹那の見切りは5勝でクリア、3ミスで終了します。
- 四色記憶は `light-rig` と `stage-light` でステージライトが順番に光ります。
- 四色記憶は5正解でクリア、3ミスで終了します。

## 画像ルール

- 丸く切り抜いた写真風画像をキャラに使わない。
- キャラ、小物は背景透過PNGを使う。
- 背景は `assets/minigames/crops/*-bg.png` を使う。
- 透過素材を増やす場合は `assets/minigames/transparent/` に保存し、HTMLからその相対パスを参照します。
- ジャンプリズムだけは専用フォルダ `assets/minigames/jump/` を使います。生成元は `jump-sprite-source.png`, `jump-obstacles-source.png`、透過化後の分割素材は `jump-run-a.png`, `jump-run-b.png`, `jump-jump.png`, `jump-obstacle-*.png` です。

## よく壊れる点

- ミニゲーム中に横スクロールが出る。
- HUDが画面外や別枠のように見える。
- 刹那の見切りが全画面にならない。
- キャラの服装/絵柄が別人に見える。
- スマホ幅でタップ領域が小さすぎる。

## 確認方法

- `pages/minigames.html` を開く。
- 各カードを1回押すと即ゲームが始まる。
- 選択画面に `.host-panel` と4つの `.idea-card` が表示される。
- ゲーム中に `.coach-badge` が表示され、ゲームごとに違うキャラ名になる。
- PC幅とスマホ幅で `document.documentElement.scrollWidth - window.innerWidth` が0。
- `.play-layout > .hud` が存在せず、`.arena .stage-hud` が存在する。`.stage-hud` は下部ではなく上部にある。
- ジャンプリズムで `#jumpPlayer` の `src` が地上で `jump-run-a.png` / `jump-run-b.png` を交互に変え、ジャンプ中だけ `jump-jump.png` になる。
- ジャンプリズムで長押しすると `.jump-charge-fill` が伸び、短押しより高く飛ぶ。
- ジャンプリズムで `.jump-obstacle` が右から流れ、接触すると `LIFE` が減る。
- 刹那の見切りで、構え、打つ、失敗、勝利のポーズが切り替わる。
- 刹那の見切りで3ミスすると `.result-overlay` が表示される。
- 選択画面に `.daily-card` が3つ表示される。
- コンソールエラーが出ていない。
- 走る特訓では `.power-bubble` と2つの `.math-gate` が表示され、最後に `.runner-boss.show` から `.result-overlay` へ進む。
- 刹那では `.dojo-flash` と `.slash-effect`、四色では `.stage-light` が存在する。
