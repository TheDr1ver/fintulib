
def print_all_category_levels(df):
    """Print levels of all categoric columns in dataframe"""
    for cat in df.columns:
        if df[cat].dtypes.name == 'category':
            print(df[cat].cat.categories)
            if df[cat].hasnans:
                print(f"Nans found  in category {cat}!")
