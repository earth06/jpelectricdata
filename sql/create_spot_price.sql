DROP TABLE IF EXISTS spot_price;
CREATE TABLE spot_price(
date_time TEXT, --受渡日	
slot INTEGER,--時刻コード	
sell_amount REAL,--売り入札量(kWh)
buy_amount REAL,--買い入札量(kWh)
contract_amount REAL, --約定総量(kWh)
system_price REAL,--システムプライス(円/kWh)
area_price_hokkaido REAL,--エリアプライス北海道(円/kWh)
area_price_tohoku REAL,--エリアプライス東北(円/kWh)
area_price_tokyo REAL,--エリアプライス東京(円/kWh)
area_price_chubu REAL,--エリアプライス中部(円/kWh)
area_price_hokuriku REAL,--エリアプライス北陸(円/kWh)
area_price_kansai REAL,--エリアプライス関西(円/kWh)
area_price_chugoku REAL,--エリアプライス中国(円/kWh)
area_price_shikoku REAL,--エリアプライス四国(円/kWh)
area_price_kyusyu REAL,--エリアプライス九州(円/kWh)
sell_block_amount REAL,--売りブロック入札総量(kWh)
sell_block_contract_amount REAL,--売りブロック約定総量(kWh)
buy_block_amount REAL,--買いブロック入札総量(kWh)
buy_block_contract_amount REAL,--買いブロック約定総量(kWh)
    PRIMARY KEY(date_time)
);
