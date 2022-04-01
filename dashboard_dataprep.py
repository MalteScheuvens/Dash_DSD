# Imports
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.api.types import CategoricalDtype
import pandas as pd
import numpy as np


# Load and prep country codes
def load_country_codes():
    file_path = 'data/country_code.csv'
    df = pd.read_csv(file_path, sep=';')
    # df.set_index(['country_code'], inplace=True)
    return df


weights = np.array([0.03, 0.06, 0.13, 0.26, 0.52 ])
def rolling_weight(group):
    return group.rolling(5).apply(lambda group: np.dot(group, weights))

df_terrorism['terrorism_index_rolling_weight'] = df_terrorism['terrorism_index'].groupby(by='country_code').apply(rolling_weight)
root = 20
min_per_year = df_terrorism.groupby(by='year').min()['terrorism_index_rolling_weight']
max_per_year = df_terrorism.groupby(by='year').max()['terrorism_index_rolling_weight']
range_per_year = 2 * (max_per_year - min_per_year)
score_per_year = range_per_year ** (1/root)
bands = [(x, x/2) for x in range(0,21, 1)]


def calc_scores(score):
    tmp = [(score ** x,lvl) for (x,lvl) in bands]
    tmp[0] = (0,0)
    return tmp

levels_per_year = score_per_year.apply(calc_scores)
tmp = df_terrorism.join(levels_per_year, lsuffix='', rsuffix='_r')


def assign_class(tmp):
    levels = tmp['terrorism_index_rolling_weight_r']
    weight = tmp['terrorism_index_rolling_weight']

    val = weight.values[0]

    if np.isnan(val):
        return 0

    levels = levels.values[0]

    for th, lvl in levels:
        if val < th:
            return lvl

    return 10


def calc_abs_impact_level_new(x):
    if x >= 8:
        return 'very_high'
    elif x >= 6:
        return 'high'
    elif x >= 4:
        return 'medium'
    elif x >= 2:
        return 'low'
    elif x > 0:
        return 'very_low'
    else:
        return 'no_impact'


df_terrorism['absolute_terrorism_score'] = pd.DataFrame(tmp.groupby(by=['country_code','year']).apply(assign_class)).rename(columns={0:'absolute_terrorism_score'})
df_terrorism['absolute_terrorism_impact'] = df_terrorism['absolute_terrorism_score'].apply(calc_abs_impact_level_new)

# Load and prep terrorism data set
def load_gtd_data():
    file_path = 'data/globalterrorismdb_0221dist.xlsx'
    df = pd.read_excel(file_path)
    return df


# Load and prep polity data set
def categorical_govern(row):
    if -6 >= row['polity'] >= -10:
        return 'Autocracy'
    if 5 >= row['polity'] >= -5:
        return 'Anocracy'
    if row['polity'] > 5:
        return 'Democracy'
    else:
        return 'Transitioning'


def categorical_fragment(row):
    if row['fragment'] == 1:
        return 'Slight Fragmentation (<10%)'
    if row['fragment'] == 2:
        return 'Moderate Fragmentation (10-25%)'
    if row['fragment'] == 3:
        return 'Serious Fragmentation (25-50%)'
    else:
        return 'No Fragmentation (0%)'


def load_polity():
    file_path = 'data/p5v2018.xls'
    sheet_name = 'p5v2018'
    df = pd.read_excel(file_path, sheet_name)
    polity_df = df[['flag', 'scode', 'country', 'year', 'fragment', 'democ', 'autoc', 'polity', 'polity2', 'durable']]

    country_codes = load_country_codes()
    # country_codes.reset_index(inplace=True)
    country_name_to_code = {row[1]: row[0] for row in country_codes.values.tolist()}

    # convert 'scode' to country code and set index
    polity_df['scode'] = df['country'].apply(lambda x: country_name_to_code[x])
    polity_df = polity_df.rename(columns={"scode": "country_code"})
    polity_df.drop(columns=['country'], inplace=True)
    polity_df = polity_df.set_index(['country_code', 'year'])

    # convert govern_type and cat_fragment to categorical values
    polity_cat = polity_df
    polity_cat['govern_type'] = polity_df.apply(lambda row: categorical_govern(row), axis=1)
    govern_cat = CategoricalDtype(categories=['Democracy', 'Anocracy', 'Autocracy', 'Transitioning'], ordered=True)
    polity_cat['govern_type'].astype(govern_cat)

    polity_cat['cat_fragment'] = polity_df.apply(lambda row: categorical_fragment(row), axis=1)
    fragment_cat = CategoricalDtype(
        categories=['No Fragmentation (0%)', 'Slight Fragmentation (<10%)', 'Moderate Fragmentation (10-25%)',
                    'Serious Fragmentation (25-50%)'], ordered=True)
    polity_cat['cat_fragment'].astype(fragment_cat)

    return polity_cat


def load_full_data():
    polity_df = load_polity()
    gtd_df = load_gtd_data()


    countries_for_regions = load_country_codes().drop(columns='country_name').reset_index().groupby(by='country_code').first()
    df_terrorism_with_regions = df_terrorism.join(countries_for_regions)

    print(df_terrorism_with_regions.isna().sum())

    # intermediate region is not used in here...
    df_terrorism_with_regions.drop(columns='intermediate_region', inplace=True)


    polity_terror = pd.merge(polity_df, df_terrorism_with_regions, how ='left', left_index = True, right_index = True)

    return gtd_data
