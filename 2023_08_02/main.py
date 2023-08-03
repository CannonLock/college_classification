import pandas as pd
from util import calculate_lat, calculate_lon, get_ospool_project_institutions, ColumnRandomizer

# The initial merge of the previous spreadsheet with the new spreadsheet

production = pd.read_csv('data/2023_08_02_institutions.csv')
collected = pd.read_csv('data/institutions_final.csv')

df = production.merge(collected, how="left", on="Institution Name", suffixes=("", "_collected"), indicator=True)

df.drop(["Has Resource(s)_collected", "Has Project(s)_collected"], axis=1, inplace=True)

df.to_csv("data/2023_08_02_joined.csv", index=False)

# At this point you have to manually look at the spreadsheet and geo map and ipeds map

# Now you can merge in the supplemental data that includes the college classifications

df = pd.read_excel("./data/CCIHE2021-PublicData.xlsx", "Data")[["unitid", "name", "city", "hbcu", "tribal", "msi", "iclevel"]]

geo_map = pd.read_excel("./data/EDGE_GEOCODE_POSTSECSCH_2122.xlsx", 0)[["UNITID", "LON", "LAT"]]

topo_f = pd.read_csv("./data/2023_08_02_joined_final.csv")

final = topo_f.merge(geo_map, how="left", left_on="IPEDS", right_on="UNITID")
final = final.merge(df, how="left", left_on="IPEDS", right_on="unitid")

final["LAT"] = final.apply(calculate_lat, axis=1)
final["LON"] = final.apply(calculate_lon, axis=1)


def is_one(x):
    if x == 1:
        return True
    elif not pd.isna(x):
        return False

    return x


def ic_level_classification(x):
    if x == 1:
        return "Four or more years"
    if not pd.isna(x):
        return "At least 2 but less than 4 years"

    return x




final['hbcu'] = final['hbcu'].apply(is_one)
final['tribal'] = final['tribal'].apply(is_one)
final['msi'] = final['msi'].apply(is_one)
final['iclevel'] = final['iclevel'].apply(ic_level_classification)

final.to_json("final_w_supplemental.json", orient="records")
final.to_csv("final_w_supplemental.csv", index=False)
