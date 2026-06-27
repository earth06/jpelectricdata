# Webアプリ構成整理とFastAPI移行計画

## 目的

このドキュメントは、現行の Plotly + Dash + Flask で作成された `jpelectricdata` のWebアプリ構成、ページ遷移、入出力を整理し、次段階で FastAPI へ移行するための計画をまとめる。

移行先のディレクトリ構成は `~/Git/fastapi-template/` の構成を流用する前提とする。

## 現行アプリの概要

現行アプリは `app/app.py` をエントリポイントとする Dash アプリで、`dash.Dash(..., use_pages=True)` により `app/pages/` 配下のページを自動登録している。Dash が内部で持つ Flask server を `server = app.server` として公開し、追加で Flask route `/api` を定義している。

主な依存関係は次の通り。

| 分類 | 利用技術 | 用途 |
| --- | --- | --- |
| Webアプリ | Dash, Flask | 画面表示、callback、追加API route |
| グラフ | Plotly Express, Plotly Graph Objects | 折れ線グラフ、積み上げ面グラフ |
| データ処理 | pandas | SQLite結果のDataFrame化、整形 |
| DB | SQLite | `data/data.db` に需給・市場価格を保存 |
| CSS | Tailwind CDN, Font Awesome CDN, `assets/styles.css` | レイアウト、ナビゲーション、Dash部品の見た目調整 |

起動方法は `app/` に移動して `python app.py --host <host> --port <port>` を実行する方式。systemd 用の `run_server.sh` と uWSGI 用の `app/app.ini` も存在する。

## 現行ディレクトリ構成

```text
app/
  app.py                  Dash/Flaskエントリポイント、共通レイアウト、sidebar callback、/api
  datareader.py           SQLiteからpandas DataFrameを返すデータアクセス
  app.ini                 uWSGI設定
  pages/
    common.py             表示対象エリア、需給項目、色、ナビゲーション、Plotlyテーマ
    home.py               ホーム画面
    balance.py            需給バランス画面
    trend.py              1か月トレンド画面
    download.py           スポット価格ダウンロード画面
    publishapiurl.py      /api のURL生成画面
assets/
  styles.css              Dash assets自動ロード対象のCSS
sql/
  create_spot_price.sql
  create_detail_demand_supply.sql
src/
  scraping_electricity.py 需給データ収集・DB登録
  scraping_jepx.py        JEPXスポット価格取得・DB登録
```

## 共通レイアウトとページ遷移

`app/app.py` の `app.layout` が全ページ共通レイアウトを定義している。

共通レイアウトの構成:

| 部品 | Dash ID | 内容 |
| --- | --- | --- |
| URL監視 | `url` | `dcc.Location`。現在パスを保持し、ナビゲーションのactive表示に利用 |
| Sidebar状態 | `sidebar-collapsed` | `dcc.Store`。sidebarの折りたたみ状態を保持 |
| Sidebar | `sidebar` | `Config.navigation` からリンクを生成 |
| Toggle button | `sidebar-toggle` | sidebar開閉 |
| Page container | なし | `dash.page_container`。`app/pages/` 配下の登録ページを表示 |

ページ遷移は Dash Pages によるクライアント側ルーティングで実現している。ナビゲーション定義は `app/pages/common.py` の `Config.navigation` に集約されている。

| パス | ページモジュール | 表示名 | 主な用途 |
| --- | --- | --- | --- |
| `/` | `home.py` | ホーム | 7日間のスポット価格と需給指標を表示 |
| `/balance` | `balance.py` | 需給バランス | 7日間の市場価格とエリア別需給構成を表示 |
| `/download` | `download.py` | ダウンロード | 任意期間のスポット価格をDataTable表示しCSV出力 |
| `/publishapiurl` | `publishapiurl.py` | API URL発行 | `/api?begin=...&end=...` のURLを生成 |
| `/trend` | `trend.py` | 1か月トレンド | 30日間のスポット市場・需給トレンドを表示 |

補足:

- 明示的な一覧ページングは実装されていない。`download.py` の `dash_table.DataTable` も `page_size` や `page_action` を設定しておらず、Dash DataTable のデフォルト挙動に依存している。
- `home.py` と `balance.py` には「予測対象エリア」の `dcc.Checklist` があるが、IDがなく callback 入力にも接続されていないため、現状ではグラフ表示には影響しない。

## Dash callback一覧

### 共通callback

| 出力 | 入力 | 処理 |
| --- | --- | --- |
| `sidebar.className`, `sidebar.data-collapsed`, `sidebar-collapsed.data`, `sidebar-toggle-icon.className` | `sidebar-toggle.n_clicks`, `sidebar-collapsed.data` | sidebar開閉状態とアイコンを切り替える |
| 各 `nav-*` の `className` | `url.pathname` | 現在URLに応じてsidebarリンクをactive化する |

### ホーム `/`

| 出力 | 入力 | データ取得 | 表示 |
| --- | --- | --- | --- |
| `demand-graph.figure` | `plot_base_date.date`, `demand_supply_selector.value` | `read_demand_supply(base_date - 7日, base_date)` | エリア別の需給項目折れ線 |
| `price-graph.figure` | `plot_base_date.date` | `read_spot_price(base_date - 7日, base_date)` | `target_areas` のエリア価格折れ線 |

### 需給バランス `/balance`

| 出力 | 入力 | データ取得 | 表示 |
| --- | --- | --- | --- |
| `price-graph2.figure` | `plot_base_date.date` | `read_spot_price(base_date - 7日, base_date)` | `target_areas` のエリア価格折れ線 |
| `balance-graph.figure` | `plot_base_date.date`, `area_selector.value` | `read_demand_supply(..., ignore_negative_value=True)` 後、エリアで絞り込み | 供給項目の積み上げ面 + `area_demand` 折れ線 |

### 1か月トレンド `/trend`

| 出力 | 入力 | データ取得 | 表示 |
| --- | --- | --- | --- |
| `trend-price-graph.figure` | `plot_base_date.date`, `spot_selector.value` | `read_spot_price(base_date - 30日, base_date)` | 価格またはブロック取引量の折れ線。range sliderあり |
| `trend-graph.figure` | `plot_base_date.date`, `area_selector.value` | `read_demand_supply(..., ignore_negative_value=True)` | エリア別、または全国合算の積み上げ面 + `area_demand` 折れ線。range sliderあり |

### ダウンロード `/download`

| 出力 | 入力 | State | データ取得 | 表示 |
| --- | --- | --- | --- | --- |
| `table-container.children` | `submit-button.n_clicks` | `start-date.date`, `end-date.date` | `read_spot_price(start_date, end_date)` | `dash_table.DataTable`。CSV export有効 |

### API URL発行 `/publishapiurl`

| 出力 | 入力 | State | 処理 |
| --- | --- | --- | --- |
| `api-url-container.children` | `api-publish-button.n_clicks` | `start-date.date`, `end-date.date` | `http://<address>:<port>/api?begin=YYYYMMDD&end=YYYYMMDD` を生成し、Clipboardを表示 |

## 現行IO

### 画面入力

| 入力 | 利用ページ | 形式 | 用途 |
| --- | --- | --- | --- |
| `plot_base_date` | `/`, `/balance`, `/trend` | `YYYY-MM-DD` | グラフ対象期間の基準日 |
| `demand_supply_selector` | `/` | 需給列名 | ホームの需給折れ線対象 |
| `area_selector` | `/balance`, `/trend` | エリア名、`trend` のみ `all` あり | 需給バランス対象エリア |
| `spot_selector` | `/trend` | `price` / `block` | スポット市場グラフの指標切替 |
| `start-date`, `end-date` | `/download`, `/publishapiurl` | `YYYY-MM-DD` | 表示・API URL生成の期間 |

### 画面出力

| 出力 | 形式 | 備考 |
| --- | --- | --- |
| Plotlyグラフ | Dash `dcc.Graph.figure` | callbackが `plotly.graph_objects.Figure` を返す |
| テーブル | Dash DataTable | `/download` でスポット価格を表示 |
| CSV | Dash DataTable client export | サーバー側CSV endpointはない |
| API URL | 文字列 + Clipboard | `/api` のURLを生成 |

### HTTP API

現行のAPIは `app/app.py` で Flask route として定義されている。

| Method | Path | Query | 処理 | Response |
| --- | --- | --- | --- | --- |
| GET | `/api` | `begin=YYYYMMDD`, `end=YYYYMMDD` | `spot_price` を `begin 00:00` から `end 23:59` まで取得 | `date_time`, `area_price_chubu` の dict を `jsonify` |

注意点:

- `begin`, `end` のデフォルトはどちらも `20241201`。
- 日付形式が不正な場合のエラーハンドリングはない。
- レスポンスは `DataFrame.to_dict()` のデフォルト形式で、列ごとに行indexをキーにした辞書になる。一般的な `records` 形式ではない。

### DB入力

Webアプリは `app/datareader.py` 経由で SQLite を読み取る。

| テーブル | 主キー | 主な用途 |
| --- | --- | --- |
| `spot_price` | `date_time` | スポット価格、入札量、約定量、ブロック取引量 |
| `detail_demand_supply` | `date_time`, `area_name` | エリア別の需要、電源別供給、連系線、合計 |

DBファイルは `DataReader.DBPATH = "../data/data.db"` として相対パスで指定されている。このため起動ディレクトリは実質 `app/` 前提になっている。

## 現行実装上の移行リスク

| リスク | 内容 | FastAPI移行時の対応 |
| --- | --- | --- |
| SQL文字列補間 | `begin`, `end`, `area` 相当の値がSQLやDataFrame queryに直接入る | Pydanticで入力検証し、SQLAlchemy Coreまたはsqlite parameter bindingに置換 |
| DBパスが相対 | `../data/data.db` がカレントディレクトリ依存 | `app/core/config.py` で絶対パス化、環境変数で上書き可能にする |
| Dash callback依存 | UI状態変更とサーバー処理がDash callbackに密結合 | API endpoint + HTML/JSのイベント処理へ分離 |
| Plotly figure生成場所 | Python側でFigureを生成してDashに返す | FastAPIでは `figure JSON` を返すか、API dataを返してPlotly.jsで描画するか判断が必要 |
| CDN依存 | Tailwind/Font Awesomeを外部CDNから読む | 本番方針に応じてCDN継続か静的ファイル同梱にする |
| APIレスポンス形状 | `/api` が列指向dictで用途が限定的 | 互換APIを残すか、`records` 形式のv1 APIへ移行するか判断が必要 |
| 未接続UI | `target_areas` Checklistがcallbackに接続されていない | 移行時に削除するか、グラフ対象エリア選択として実装する |

## FastAPI移行後の推奨構成

`~/Git/fastapi-template/` の構成をベースに、次のように配置する。

```text
app/
  main.py
  core/
    config.py              DBパス、環境設定、定数
    chart_config.py        エリア、需給項目、色、表示名、Plotlyテーマ相当
  db/
    session.py             SQLite接続/SQLAlchemy engine/session
    base.py
  data_access/
    electric_data.py       spot_price/detail_demand_supply のSQL取得
  schemas/
    electric.py            API request/response、期間、エリア、指標のPydanticモデル
  services/
    electric_service.py    期間計算、負値補正、全国合算、グラフ用データ整形
    chart_service.py       Plotly figure JSON生成を採用する場合のFigure生成
  api/
    v1/
      routers/
        spot_price.py      スポット価格API
        demand_supply.py   需給API
        charts.py          グラフ描画用API
        export.py          CSVダウンロードAPI
  web/
    routes.py              HTMLページのrouter
    templates/
      base.html
      home.html
      balance.html
      trend.html
      download.html
      publishapiurl.html
      partials/
        sidebar.html
  static/
    css/
      styles.css           現行 assets/styles.css を移植
    js/
      app.js               sidebar、共通UI
      charts.js            Plotly.js描画、API呼び出し
      download.js          テーブル表示、CSV取得
```

## FastAPI API設計案

Dash callbackを直接置き換えるため、画面用APIとデータ取得APIを分ける。

| Method | Path | Query | 用途 |
| --- | --- | --- | --- |
| GET | `/api/v1/spot-prices` | `begin`, `end`, `areas`, `fields` | スポット価格データ取得 |
| GET | `/api/v1/demand-supply` | `begin`, `end`, `area`, `fields`, `ignore_negative` | 需給データ取得 |
| GET | `/api/v1/charts/home/price` | `base_date`, `areas` | ホーム価格グラフ |
| GET | `/api/v1/charts/home/demand` | `base_date`, `field` | ホーム需給グラフ |
| GET | `/api/v1/charts/balance/price` | `base_date`, `areas` | 需給バランス価格グラフ |
| GET | `/api/v1/charts/balance/supply` | `base_date`, `area` | 需給積み上げグラフ |
| GET | `/api/v1/charts/trend/spot` | `base_date`, `spot_type` | 30日スポット市場グラフ |
| GET | `/api/v1/charts/trend/supply` | `base_date`, `area` | 30日需給トレンドグラフ |
| GET | `/api/v1/export/spot-prices.csv` | `begin`, `end` | CSVダウンロード |
| GET | `/api` | `begin=YYYYMMDD`, `end=YYYYMMDD` | 既存互換API。必要な場合のみ残す |

`begin`, `end`, `base_date` は ISO date (`YYYY-MM-DD`) を標準にする。ただし既存 `/api` 互換では `YYYYMMDD` を維持する。

## グラフレンダリング移行方針

Dashから移行する場合、Plotly自体は継続利用できる。移行方法は大きく2案ある。

### 案A: サーバーでPlotly Figure JSONを生成する

FastAPI endpointが Python の Plotly Figure を生成し、`fig.to_json()` または `fig.to_plotly_json()` を返す。フロントエンドは Plotly.js の `Plotly.react()` で描画する。

メリット:

- 現行 `px.line`, `px.area`, `go.Scatter`, テーマ処理を比較的そのまま移植できる。
- グラフ仕様の差分が小さい。

デメリット:

- APIレスポンスがPlotly依存になり、データAPIとしての再利用性は下がる。
- pandas + Plotly の処理がサーバー側に残る。

### 案B: APIは正規化データを返し、フロントエンドでPlotly.js描画する

FastAPI endpointは `records` 形式のJSONを返し、`static/js/charts.js` が trace/layout を組み立てる。

メリット:

- APIが汎用データとして利用しやすい。
- グラフ以外のUIや外部連携に展開しやすい。

デメリット:

- 現行の Python Plotly ロジックを JavaScript へ再実装する必要がある。
- テーマ、凡例、積み上げ面グラフなどの再現確認が増える。

推奨は段階移行しやすい案A。まず `chart_service.py` に現行Plotly生成処理を移し、画面から `figure JSON` を取得してPlotly.jsで描画する。APIの長期利用を重視する場合は、次段階で案BのデータAPIを主にし、chart endpointを薄くする。

## 移行手順

1. FastAPIプロジェクトの土台を作る
   - `~/Git/fastapi-template/` の構成を流用する。
   - `app/main.py` に `web.routes` と `api.v1.routers` を登録する。
   - `app/static` と `app/web/templates` を有効化する。

2. 共通設定を移植する
   - `Config` の `target_areas`, `areas`, `area2jparea`, `supply_names`, `supply_colors`, `demand_supply2_jpnames` を `app/core/chart_config.py` へ移す。
   - DBパスは `app/core/config.py` で管理し、デフォルトをリポジトリルートの `data/data.db` にする。

3. データアクセス層を作る
   - `DataReader` を `app/data_access/electric_data.py` へ移し、SQLはparameter bindingまたはSQLAlchemy Coreへ置き換える。
   - `read_spot_price`, `read_demand_supply` は `list[dict]` またはPydantic schemaに変換しやすい形で返す。

4. service層を作る
   - 7日/30日の期間計算、負値補正、全国合算、表示列選択を `app/services/electric_service.py` に集約する。
   - 案Aを採用する場合、現行のPlotly生成処理を `app/services/chart_service.py` に移す。

5. APIを実装する
   - `/api/v1/spot-prices`, `/api/v1/demand-supply`, `/api/v1/charts/*`, `/api/v1/export/spot-prices.csv` を追加する。
   - 既存 `/api` の互換が必要なら、同じpathで `YYYYMMDD` を受ける互換routerを残す。

6. Web画面をJinja2 + JavaScriptへ移行する
   - `base.html` にsidebar/header/main領域を定義する。
   - `home.html`, `balance.html`, `trend.html`, `download.html`, `publishapiurl.html` を作成する。
   - `DatePickerSingle`, `Dropdown`, `Checklist`, `DataTable` は標準HTML input/select/table と JavaScript へ置換する。
   - Plotly.jsを読み込み、APIレスポンスを `Plotly.react()` で描画する。

7. 静的ファイルを移植する
   - `assets/styles.css` を `app/static/css/styles.css` へ移す。
   - Dash固有セレクタはHTML実装に合わせて整理する。
   - sidebar開閉、active navigation、Clipboard、CSVダウンロード処理を `app/static/js/` に実装する。

8. テストと互換確認
   - data_accessの期間指定、負値補正、全国合算を単体テストする。
   - APIのバリデーション、CSV、既存 `/api` 互換をテストする。
   - 主要ページでグラフが非空、凡例、range slider、CSV出力が動作することを確認する。

## 判断が必要な質問

1. グラフAPIは、短期移行を優先して「サーバーでPlotly Figure JSONを生成する案A」にしますか。それとも将来のAPI再利用性を優先して「APIはデータのみ、フロントエンドでPlotly.js描画する案B」にしますか。

> 案Aを採用します。

2. 既存の `/api?begin=YYYYMMDD&end=YYYYMMDD` は外部利用者向けに互換維持が必要ですか。不要であれば `/api/v1/spot-prices` へ統合できます。

>api/v1/spot-pricesに統合してください。

3. `home.py` と `balance.py` の未接続の「予測対象エリア」Checklistは、移行時にグラフ対象エリア選択として実装しますか。それともUIから削除しますか。

> UIから削除します

4. CSV出力は現行のように画面上のテーブルからクライアント側でエクスポートしますか。それとも FastAPI の `/api/v1/export/spot-prices.csv` としてサーバー側CSVを正式機能にしますか。

> サーバー側CSVを正式機能にします。

5. SQLiteは当面継続しますか。将来的にPostgreSQLなどへ移す可能性があるなら、移行初期からSQLAlchemy Core/ORMを使う方がよい。

> SQliteの利用は継続しますがDBへのアクセスはSQLAlchemy Coreを使う方針とします。

6. Tailwind/Font Awesome/Plotly.js はCDN利用を継続しますか。本番環境で外部通信を避ける必要がある場合は静的ファイルとして同梱する設計にします。

> 静的ファイルとして同梱して下さい。　

## 移行実装メモ

回答方針に従い、FastAPI移行では次の設計で実装する。

- グラフAPIは案Aを採用し、FastAPIがPlotly Figure JSONを返す。
- 旧 `/api?begin=YYYYMMDD&end=YYYYMMDD` は作らず、`/api/v1/spot-prices?begin=YYYY-MM-DD&end=YYYY-MM-DD` に統合する。
- 旧Dash画面の未接続「予測対象エリア」Checklistは削除する。
- CSV出力は `/api/v1/export/spot-prices.csv` のサーバー側CSV endpointとして提供する。
- DBアクセスはSQLite継続、実装はSQLAlchemy Coreを使う。
- Tailwind、Font Awesome、Plotly.jsの外部CDNは使わない。CSS/JSは `app/static` から配信し、Plotly.jsはPythonの `plotly` パッケージに同梱される `plotly.min.js` をローカル配信する。


### webgis実装メモ

- Web画面は `/powermap` として追加する。
- タイル配信APIは `/api/v1/powermap/tilejson.json` と `/api/v1/powermap/tiles/{z}/{x}/{y}.pbf` とする。
- `data/power.mbtiles` はMBTilesのTMS tile rowで保存されているため、APIではXYZの `y` をTMS rowへ変換して取得する。
- MapLibre GL JSは `app/static/vendor/` に同梱し、外部CDNに依存しない。送電線などのタイル描画はMapLibreのWebGL layerで行い、空のdeck.gl overlayは使わない。
- ベースマップは国土地理院の地理院タイル pale (`https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png`) をMapLibreのraster sourceとして表示する。MapLibreのraster描画が環境依存で空になる場合に備え、`?fallback=dom` 指定時のみ同じpaleタイルを通常の `<img>` グリッドで背面表示するフォールバックを持つ。
- 地図の初期位置は名古屋駅付近 `[136.881537, 35.170915]`、初期ズームは `10` とする。
- 送電線は `power_lines` をMapLibreのline layerで描画し、`voltage` に応じて線幅と色を変える。現行の `power_lines` には管理事業者を示す属性がなく、正確な事業者色分けにはMBTiles生成時に `operator` などの属性を保持する必要がある。
- 鉄塔は `power_towers` をズーム12以上で表示し、MBTiles作成時のtippecanoe generalizationと表示ズーム制限により低ズームでの密度を抑える。
- ホバーpopupは `power_plants_points`, `power_plants_polygons`, `power_substations_points`, `power_substations_polygons` のみに限定する。
- 凡例はクリック可能なトグルとし、154kV以上、66kV以上、その他/不明、鉄塔、発電所、変電所の表示・非表示をMapLibre layer group単位で切り替える。

　
