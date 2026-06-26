# 研究計画ページ 引き継ぎ

## 担当ファイル

- `pages/research-plan.html`
- 画像: `assets/chibis/hinata-plan.png`

## 役割

研究テーマ、仮説、今日やること、観測/結果、次に確認することを保存する簡易ノートです。

## 見るべきコード位置

- 入力欄HTML: `topic`, `hypothesis`, `todo`, `result`, `next`
- 保存キー: `STORE_KEY = 'nvDftResearchPlan.v1'`
- 保存処理: `collect`, `fill`, `save`
- JSON出力: `exportBtn` のイベント
- 消去: `clearBtn` のイベント

## 重要仕様

- 入力は `localStorage` に自動保存します。
- JSON出力はブラウザ内でBlobを作ってダウンロードします。
- サーバー保存はありません。
- 他ページに戻る導線は `../index.html` と `../index.html#simulation` です。

## 改修候補

- 日付ごとに研究計画を複数保存する。
- 参考文献ページの論文IDと研究計画を紐づける。
- Markdown出力を追加する。

## 確認方法

- 入力後にリロードして内容が残る。
- JSON出力できる。
- 消去ボタンで `localStorage` の該当キーだけ消える。
