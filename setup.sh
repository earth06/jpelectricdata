#! /bin/bash
# cleanup database file
# run on workdir
if [ -e data/data.db  ];then
    rm ./data/data.db
fi

sqlite3 ./data/data.db  < ./sql/create_detail_demand_supply.sql
