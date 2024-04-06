DROP TABLE IF EXISTS detail_demand_supply;
CREATE TABLE detail_demand_supply(
    "date_time" TEXT,
    "area_name" TEXT,
    "area_demand" REAL,
    "nuclear" REAL,
    "thermal_lng" REAL,
    "thermal_coal" REAL,
    "thermal_oil" REAL,
    "thermal_others" REAL,
    "hydropower" REAL, 
    "geothermal" REAL, 
    "biomass" REAL, 
    "solarpower" REAL, 
    "soloarcontrol" REAL,
    "windpower" REAL,
    "windcontrol" REAL,
    "pumping_up" REAL,
    "battery" REAL,
    "connector" REAL,
    "others" REAL, 
    "total" REAL,
    PRIMARY KEY(date_time, area_name)
);
