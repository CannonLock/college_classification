import pandas as pd
from util import calculate_lat, calculate_lon, get_ospool_project_institutions

df = pd.read_excel("CCIHE2021-PublicData.xlsx", "Data")[["unitid", "name", "city", "hbcu", "tribal", "msi", "iclevel"]]

geo_map = pd.read_excel("EDGE_GEOCODE_POSTSECSCH_2122.xlsx", 0)[["UNITID", "LON", "LAT"]]

topo_f = pd.read_csv("institutions_final.csv")

final = topo_f.merge(geo_map, how="left", left_on="IPEDS", right_on="UNITID")
final = final.merge(df, how="left", left_on="UNITID", right_on="unitid")

# Define some classification helper functions
hbcu_or_tribal = lambda row: row['hbcu'] == 1 or row['tribal'] == 1
not_hbcu_or_tribal_but_msi = lambda row: not (row['hbcu'] == 1 or row['tribal'] == 1) and row['msi'] == 1
not_msi_and_not_iclevel_1 = lambda row: row['msi'] == 0 and row['iclevel'] != 1

final["hbcu_or_tribal_resource"] = final.apply(lambda row: row["Has Resource(s)"] and hbcu_or_tribal(row), axis=1)
final["not_hbcu_or_tribal_but_msi_resource"] = final.apply(lambda row: row["Has Resource(s)"] and not_hbcu_or_tribal_but_msi(row), axis=1)
final["not_msi_and_not_iclevel_1_resource"] = final.apply(lambda row: row["Has Resource(s)"] and not_msi_and_not_iclevel_1(row), axis=1)

final["LAT"] = final.apply(calculate_lat, axis=1)
final["LON"] = final.apply(calculate_lon, axis=1)

final = final[~final.duplicated(subset=["IPEDS", "Has Project(s)", "Has Resource(s)"], keep="first") | final["IPEDS"].isna()]

ospool_institutions = get_ospool_project_institutions()
final["active_project_in_ospool"] = final.apply(lambda x: x['Institution Name'] in ospool_institutions, axis=1)

final["hbcu_or_tribal_project"] = final.apply(lambda row: row["active_project_in_ospool"] and hbcu_or_tribal(row), axis=1)
final["not_hbcu_or_tribal_but_msi_project"] = final.apply(lambda row: row["active_project_in_ospool"] and not_hbcu_or_tribal_but_msi(row), axis=1)
final["not_msi_and_not_iclevel_1_project"] = final.apply(lambda row: row["active_project_in_ospool"] and not_msi_and_not_iclevel_1(row), axis=1)


final.to_json("end_of_the_line.json", orient="records")
final.to_csv("end_of_the_line.csv")

## Create some exploratory tables based on these functions
cat_1 = df[df.apply(hbcu_or_tribal, axis=1)]
cat_1_set = set(cat_1["unitid"].unique())

cat_2 = df[df.apply(not_hbcu_or_tribal_but_msi, axis=1)]
cat_2_set = set(cat_2["unitid"].unique())

cat_3 = df[df.apply(not_msi_and_not_iclevel_1, axis=1)]
cat_3_set = set(cat_3["unitid"].unique())