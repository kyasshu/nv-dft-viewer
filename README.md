# DFT model: N interstitial / vacancy motion near an NV center in diamond

このフォルダは、低エネルギー電子照射で「格子間窒素 N_i が近くの炭素空孔 V_C に入り込む」「空孔が置換窒素 N_s の隣へ移動して NV センターになる」「置換窒素 N_s が隣接する V2 欠陥の片方へ移る」可能性を、DFT で調べるための研究モデルです。

まだ DFT 計算結果そのものではありません。Quantum ESPRESSO などを使って実際に走らせるための、構造、入力ファイル、判定基準、初心者向け説明をまとめた出発点です。

## まず結論の見取り図

低エネルギー電子、たとえば SEM の 2-30 keV 程度では、炭素や窒素原子を直接はじき飛ばす「ノックオン」は起こりにくいです。30 keV 電子が炭素原子へ直接渡せる最大エネルギーは数 eV 程度で、ダイヤモンドの原子変位しきい値としてよく使われる数十 eV より小さいためです。

そのため、調べるべき主仮説は次です。

1. 熱的な拡散だけで N_i が V_C に入るか。
2. 電子照射による電荷状態変化、電子励起、局所振動励起で障壁が下がるか。
3. そもそも観測される NV 増加は、N_i が入る動きではなく、N_s の近くで V_C が再配置する動きではないか。
4. V が2個ある欠陥複合体では、N_s が空孔サイトへ移る再構成経路も候補になるか。

この研究では 1、3、4 を通常の DFT/NEB で調べ、2 は電荷状態を変えた DFT と、必要なら制限付き DFT、TDDFT、または HSE06 で追試します。

## 用意したモデル

### Model A: `ni_to_vc`

格子間窒素 `N_i` が近くの炭素空孔 `V_C` に入るモデルです。

初期状態:

- ダイヤモンド 3x3x3 conventional supercell
- 中央付近に炭素空孔 `V_C`
- その近くの C-C 結合中心に窒素 `N_i`

終状態:

- 窒素が空孔位置へ移動し、置換窒素 `N_s` になる

注意: 空孔が 1 個だけなら、N_i が V_C に入ると空孔は消えます。つまり終状態は基本的に `N_s` であり、NV センターそのものではありません。NV センターにするには、窒素の隣にもう 1 個の空孔が必要です。

### Model B: `vacancy_hop_to_nv`

NV 形成として本命に近いモデルです。置換窒素 `N_s` の近くにある空孔が 1 回ホップして、窒素の隣に来るかを調べます。

初期状態:

- 中央付近の炭素を N に置換した `N_s`
- その第2近接程度に炭素空孔 `V_C`

終状態:

- 空孔が `N_s` の隣に来て `NV` 配置になる
- 実際の NEB では、隣接炭素が空孔へ移動することで、空孔が逆向きに動いたように表します

### Model C: `ns_to_divacancy`

置換窒素 `N_s` の隣に2個の炭素空孔が並ぶ `V-V` 欠陥複合体を置き、Nが近い空孔サイトへ移るかを調べます。

初期状態:

- 中央付近の炭素を N に置換した `N_s`
- その隣に、互いに隣接した炭素空孔が2個

終状態:

- N が片方の空孔サイトへ移動する
- N が元いた置換サイトが新しい空孔になる
- もう一つの空孔は近くに残る

注意: これは電子が N を直接押すモデルではありません。V2 欠陥複合体で、電子励起や電荷状態変化によって再構成障壁が下がるかを見るための仮説経路です。

## 使い方

Python だけで構造と Quantum ESPRESSO 入力を生成できます。

```powershell
python dft_nv_nitrogen_vacancy_model/scripts/build_qe_model.py `
  --out dft_nv_nitrogen_vacancy_model/qe `
  --supercell 3 `
  --charge 0 `
  --images 7
```

電子が原子へ直接渡せる最大エネルギーも確認できます。

```powershell
python dft_nv_nitrogen_vacancy_model/scripts/electron_transfer.py
```

NEB の出力から障壁をざっくり読む補助スクリプトもあります。

```powershell
python dft_nv_nitrogen_vacancy_model/scripts/parse_qe_neb_barrier.py path\to\neb.dat
```

## HTML解析ビューア

構造を目で確認するための静的HTMLビューアもあります。

```powershell
python -m http.server 8765
```

その後、ブラウザで次を開きます。

```text
http://localhost:8765/dft_nv_nitrogen_vacancy_model/nv_dft_viewer.html
```

詳しい読み方は `viewer_manual.md` を見てください。

## Quantum ESPRESSO で走らせる順番

1. 疑似ポテンシャルを用意する
   - `C.pbe-n-kjpaw_psl.1.0.0.UPF`
   - `N.pbe-n-kjpaw_psl.1.0.0.UPF`
   - ファイル名を変える場合は、生成された `.in` 内の `ATOMIC_SPECIES` を合わせてください。

2. 初期状態と終状態をそれぞれ緩和する

```bash
pw.x -in qe/ni_to_vc/relax_initial.in > qe/ni_to_vc/relax_initial.out
pw.x -in qe/ni_to_vc/relax_final.in   > qe/ni_to_vc/relax_final.out
```

3. 緩和後の座標を NEB 入力の `FIRST_IMAGE` / `LAST_IMAGE` に反映する

最初は生成された線形補間のままでも試せますが、論文・卒研レベルでは、緩和済み構造を端点に使ってください。

4. NEB を実行する

```bash
neb.x -in qe/ni_to_vc/neb.in > qe/ni_to_vc/neb.out
```

5. 電荷状態を変えて同じことをする

```powershell
python dft_nv_nitrogen_vacancy_model/scripts/build_qe_model.py --out dft_nv_nitrogen_vacancy_model/qe_charge_plus --charge 1
python dft_nv_nitrogen_vacancy_model/scripts/build_qe_model.py --out dft_nv_nitrogen_vacancy_model/qe_charge_minus --charge -1
```

QE では `tot_charge = -1` が電子を 1 個足す、`tot_charge = 1` が電子を 1 個抜く設定です。

## 判定基準

NEB で得た活性化障壁 `E_a` を使います。

- `E_a < 0.3 eV`: 室温でもかなり動きやすい候補。
- `0.3-1.0 eV`: 室温では遅いが、照射・励起・局所加熱で動く可能性あり。
- `1.0-2.5 eV`: 通常の室温熱拡散ではかなり厳しい。電子励起や電荷状態変化で大幅に下がるかを見る。
- `> 2.5 eV`: 低エネルギー電子照射だけで頻繁に起こる主過程とは考えにくい。

これは目安です。厳密には試料温度、照射量、捕獲断面積、試行周波数、電荷状態寿命が必要です。

## 初心者向け: DFT と NEB は何を見る計算か

DFT は、原子の並びを入れると「その形がどれくらい安定か」を量子力学で計算する方法です。山登りの地形図に例えると、原子配置ごとのエネルギーが標高です。

NEB は、初期状態から終状態へ移る道のりを何枚かの画像のように並べて、その途中で一番高い山、つまりエネルギー障壁を探す方法です。この山が低ければ反応・拡散は起こりやすく、高ければ起こりにくいです。

低エネルギー電子照射の難しい点は、電子ビームをそのまま普通の DFT に入れるわけではないことです。そこでまず、基底状態の障壁を出します。次に、電子が入った状態、電子が抜けた状態、スピンや励起状態を変えた状態で障壁が下がるかを見ます。

## このモデルの限界

- 3x3x3 conventional supercell はスクリーニング用です。論文化するなら 4x4x4 以上、またはサイズ収束確認が必要です。
- PBE は障壁の傾向を見るには便利ですが、ダイヤモンドのバンドギャップや欠陥準位を過小評価します。最後は HSE06 などで重要点を再計算してください。
- 荷電欠陥は有限サイズ補正が必要です。特に形成エネルギーを議論する場合は注意してください。
- 電子照射による非断熱過程そのものは、通常の静的 DFT/NEB だけでは証明できません。ここでは「起こりうる構造経路と障壁」を調べます。

## 最小の研究ストーリー

1. 30 keV 以下では直接ノックオンが難しいことを示す。
2. `ni_to_vc` の中性、正、負電荷状態の障壁を比較する。
3. `vacancy_hop_to_nv` の中性、正、負電荷状態の障壁を比較する。
4. `ns_to_divacancy` の中性、正、負電荷状態の障壁を比較する。
5. 障壁が低い経路を HSE06 または大きいセルで再計算する。
6. PL 実験で NV が増えているなら、どの経路が実験と整合するかを議論する。

もし `ni_to_vc` は高障壁で、`vacancy_hop_to_nv` や `ns_to_divacancy` の特定電荷状態だけ低障壁なら、「低エネルギー電子は N が物理的に押し込まれるというより、電子励起・電荷状態変化を通じて N-V/V2 複合体の再配置を助ける」と結論づけるのが自然です。
