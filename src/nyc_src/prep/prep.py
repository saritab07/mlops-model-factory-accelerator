import argparse
from pathlib import Path
from typing_extensions import Concatenate
from uuid import uuid4
from datetime import datetime
import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pickle



def main(raw_data, prep_data):
    print("hello training world...")

    lines = [
        f"Raw data path: {raw_data}",
        f"Data output path: {prep_data}",
    ]

    for line in lines:
        print(line)

    print("mounted_path files: ")
    arr = os.listdir(raw_data)
    print(arr)

    df_list = []
    for filename in arr:
        print("reading file: %s ..." % filename)
        with open(os.path.join(raw_data, filename), "r") as handle:
            input_df = pd.read_csv((Path(raw_data) / filename))
            df_list.append(input_df)

    # Prep the green and yellow taxi data
    green_data = df_list[0]
    yellow_data = df_list[1]

    data_prep(green_data, yellow_data)


def data_prep(green_data, yellow_data):
    # Define useful columns needed for the Azure Machine Learning NYC Taxi tutorial

    useful_columns = str(
        [
            "cost",
            "distance",
            "dropoff_datetime",
            "dropoff_latitude",
            "dropoff_longitude",
            "passengers",
            "pickup_datetime",
            "pickup_latitude",
            "pickup_longitude",
            "store_forward",
            "vendor",
        ]
    ).replace(",", ";")
    print(useful_columns)

    # Rename columns as per Azure Machine Learning NYC Taxi tutorial
    green_columns = str(
        {
            "vendorID": "vendor",
            "lpepPickupDatetime": "pickup_datetime",
            "lpepDropoffDatetime": "dropoff_datetime",
            "storeAndFwdFlag": "store_forward",
            "pickupLongitude": "pickup_longitude",
            "pickupLatitude": "pickup_latitude",
            "dropoffLongitude": "dropoff_longitude",
            "dropoffLatitude": "dropoff_latitude",
            "passengerCount": "passengers",
            "fareAmount": "cost",
            "tripDistance": "distance",
        }
    ).replace(",", ";")

    yellow_columns = str(
        {
            "vendorID": "vendor",
            "tpepPickupDateTime": "pickup_datetime",
            "tpepDropoffDateTime": "dropoff_datetime",
            "storeAndFwdFlag": "store_forward",
            "startLon": "pickup_longitude",
            "startLat": "pickup_latitude",
            "endLon": "dropoff_longitude",
            "endLat": "dropoff_latitude",
            "passengerCount": "passengers",
            "fareAmount": "cost",
            "tripDistance": "distance",
        }
    ).replace(",", ";")

    print("green_columns: " + green_columns)
    print("yellow_columns: " + yellow_columns)

    green_data_clean = cleanseData(green_data, green_columns, useful_columns)
    yellow_data_clean = cleanseData(yellow_data, yellow_columns, useful_columns)

    # Append yellow data to green data
    combined_df = green_data_clean._append(yellow_data_clean, ignore_index=True)
    combined_df.reset_index(inplace=True, drop=True)

    output_green = green_data_clean.to_csv(
        os.path.join(prep_data, "green_prep_data.csv")
    )
    output_yellow = yellow_data_clean.to_csv(
        os.path.join(prep_data, "yellow_prep_data.csv")
    )
    merged_data = combined_df.to_csv(os.path.join(prep_data, "merged_data.csv"))

    print("Finish")


# These functions ensure that null data is removed from the dataset,
# which will help increase machine learning model accuracy.


def get_dict(dict_str):
    pairs = dict_str.strip("{}").split(";")
    new_dict = {}
    for pair in pairs:
        print(pair)
        key, value = pair.strip().split(":")
        new_dict[key.strip().strip("'")] = value.strip().strip("'")
    return new_dict


def cleanseData(data, columns, useful_columns):
    useful_columns = [
        s.strip().strip("'") for s in useful_columns.strip("[]").split(";")
    ]
    new_columns = get_dict(columns)

    new_df = (data.dropna(how="all").rename(columns=new_columns))[useful_columns]

    new_df.reset_index(inplace=True, drop=True)
    return new_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--raw_data",
        type=str,
        default="../data/raw_data",
        help="Path to raw data",
    )
    parser.add_argument(
        "--prep_data", type=str, default="../data/prep_data", help="Path to prep data"
    )

    args = parser.parse_args()
    raw_data = args.raw_data
    prep_data = args.prep_data

    main(raw_data, prep_data)
