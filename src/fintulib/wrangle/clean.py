import pandas as pd
from fintulib import common


def cast_columns_categorical(dfs, col_categorical=[]):
    """Convert columns to categorical, considering their levels across many dataframes.
    Dataframes passed to this function are modified in place.

    Arguments:
    dfs -- a list of pd.DataFrames
    col_categorical -- a list of colum names
    """
    for cat in col_categorical:
        # find all levels across dataframes
        cat_levels = [df[cat].unique().tolist() for df in dfs if cat in df]
        cat_levels = list(set(common.lists.flatten_list(cat_levels)))
        for df in dfs:
            if cat in df:
                df[cat] = pd.Categorical(df[cat], categories=cat_levels)


def fill_na(df, col_to_fill=[],
            fill_value='NA_FILL_STRING',
            strings_consider_na=['nan', 'NaN', 'NA', 'N/A']):
    """Fill NaN values in given non-numeric columns with given string value.
    Modifies the passed dataframe in place.
    Arguments:
    df -- DataFrame
    col_to_fill -- list of column names to fill
    strings_consider_na -- consider these strings to be nan and replace them as  well
    """
    for col in col_to_fill:
        if df[col].dtype.name == 'category':
            # need to add our NAN value as a categroy level before filling
            df[col].cat.add_categories([fill_value])
            df[col].fillna(fill_value, inplace=True)
        elif df[col].dtype.name == 'object':
            # non-numeric columns -- there must be a cleaner way to find string columns
            df.loc[df[col].isin(strings_consider_na), col] = fill_value


def cast_columns_date(df, col_date=[]):
    """Convert given column names to datetime
    Modifies the passed dataframe in place.
    """
    df[col_date] = df[col_date].apply(pd.to_datetime)


def extract_ymd(df, col_name):
    """Extract year, month and date from column 'col_name'
    and subsequently drops 'col_name'.

    Doesn't mutate the original dataframe but returns a new dataframe.
    """
    df_res = df.copy()
    df_res[col_name+"_year"] = df_res[col_name].dt.year
    df_res[col_name+"_month"] = df_res[col_name].dt.month
    df_res[col_name+"_day"] = df_res[col_name].dt.day
    return df_res.drop(columns=[col_name])


class Mapping:
    """A mapping between categorical string variables and integer variables.
    """

    def __init__(self, name, data):
        self.name = name
        mymap = {}
        i = 1
        for cat in data:
            mymap[cat] = i
            i = i+1
        self.map = mymap
        self.invmap = {v: k for k, v in mymap.items()}

    def apply(self, df, col_name=None):
        """Apply the mapping to a dataframe.
        Note that if 'col_name' is not specified, the original col_name is used.

        Doesn't mutate the original dataframe but returns a new dataframe.
        """
        return self._apply(self.map, df, col_name)

    def apply_inverse(self, df, col_name=None):
        """Apply the inverse mapping to a dataframe, restoring original content.
        Note that if 'col_name' is not specified, the original col_name is used.

        Doesn't mutate the original dataframe but returns a new dataframe.
        """
        return self._apply(self.invmap, df, col_name)

    def _apply(self, mapping, df, col_name=None):
        if col_name == None:
            col_name = self.name
        result = df.copy()
        result[col_name] = result[col_name].apply(lambda x: mapping[x])
        return result


def create_integer_mapping(dfs, col_name):
    """Create a mapping to integers for categorical string variables.
    Works with one or more dataframes.
    Returns the mapping and reverse mapping.
    """
    if type(dfs) is list:
        categories_sets = [set(df[col_name].unique().tolist()) for df in dfs]
        categories = set.union(*categories_sets)
    else:
        categories = dfs[col_name].unique()
    return Mapping(col_name, categories)

def add_separate_value(df,col_name):
    """Add a truly separate value (high distance) to a numerical column 

    Doesn't mutate the original dataframe but returns a new dataframe.
    """
    newval = df[col_name].max() + (df[col_name].max()-df[col_name].min()) + 1
    result = df.copy()
    result[col_name] = df[col_name].fillna(newval)
    return result, newval

def fillna_column(df,col_name,val):
    """Replace all N/As in a given column with a given value.

    Doesn't mutate the original dataframe but returns a new dataframe.
    """
    result = df.copy()
    result[col_name] = result[col_name].fillna(val)
    return result