import pandas as pd
import numpy as np

from fuzzywuzzy import fuzz


def string_to_list(string):
    string_arr = string.replace("]", "").replace("[", "").split(",")
    ret_arr = []
    for item in string_arr:
        ret_arr.append(float(item))

    return ret_arr


def twe_input_clean():
    twe_df = pd.read_csv("./data/TWE_stock.csv")

    # here we convert the '[ x, y, z]' string into [x,y,z] float list
    twe_df["prices"] = twe_df.apply(lambda row: string_to_list(row["prices"]), axis=1)
    # add to dataframe
    twe_df[["current", "previous", "quantity"]] = pd.DataFrame(
        twe_df["prices"].to_list()
    )
    # remove old column from df
    twe_df.drop("prices", axis=1, inplace=True)

    return twe_df


def etennis_input_clean(fname):
    etennis_df = pd.read_csv(fname)
    # change to lower case before setting as index
    etennis_df["Name"] = etennis_df["Name"].str.lower()

    # drop name in greek
    etennis_df.drop(etennis_df.columns[2], axis=1, inplace=True)

    return etennis_df


#############################################################################
# So this section is a way to match the same products from both tennis sites
# first we find the similarity ratio on a row by row basis,
# and record then index of each match above a certain threshold
# after which the matched row is joined to its corresponding matcher row
#############################################################################
def likeness_score_row(df, name, threshold=90):
    matches = df.apply(
        lambda row: (fuzz.token_set_ratio(row["name"], name) >= 95), axis=1
    )
    return [i for i, x in enumerate(matches) if x]


def join_on_likeness(df_main, df_match):
    match_arr = df_main.apply(
        lambda row: likeness_score_row(df_match, row["Name"]), axis=1
    )

    df = []
    # better not be out of bounds
    # since these are just used to get the column values
    column_names = np.append(df_main.loc[0].index, df_match.loc[0].index)
    for i, row in enumerate(match_arr):
        if len(row) == 0:
            tmp = np.append(
                [df_main.loc[i].values], np.zeros(shape=[df_match.shape[1]])
            )
            df.append(tmp)
        for num in row:
            entry = np.append(df_main.loc[i].values, df_match.loc[num].values)
            df.append(entry)

    final_df = pd.DataFrame(df, columns=column_names)

    return final_df


def color_same_name(color1, color2):
    # initialise colors to use
    color1 = color1
    color2 = color2
    color = color1

    def color_changer(row):
        # closure to keep last color state
        nonlocal color1
        nonlocal color2
        nonlocal color
        if row["Name"] != row["Name_shift_1"]:
            # is same as last row
            color = color1 if color == color2 else color2

        return [f"background-color: {color}"] * len(row)

    return color_changer


def output_to_excel(df, drop_cols=[6, 11, 12, 13, 17]):

    # some background colors
    hex1 = "#add8e6"
    hex2 = "#ff9999"
    # first drop uneeded columns
    df = df.drop(df.columns[drop_cols], axis=1)
    df["Name_shift_1"] = df["Name"].shift(1)

    # init  closure
    color_flip_on_name = color_same_name(hex1, hex2)

    df.style.apply(lambda row: color_flip_on_name(row), axis=1).to_excel(
        "./data/styled_output.xlsx", engine="openpyxl"
    )
    return df


def main(fname):

    # import dataframes
    twe_df = twe_input_clean()

    etennis_df = etennis_input_clean(fname)

    # join them
    df = join_on_likeness(etennis_df, twe_df)

    output_to_excel(df)
    print("done")


if __name__ == "__main__":
    print("enter file name to compare: ")
    fname = input()
    main(fname)
