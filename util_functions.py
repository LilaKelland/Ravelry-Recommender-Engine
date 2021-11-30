import pandas as pd
import numpy as np
import ast
import streamlit

#------------------------------------------------
def get_name_permalink_from_url(pattern_url):
    print(f'permalink: {name_permalink}')
    return pattern_url.rsplit('/', 1)[-1]
    
def get_metadata_from_name_permalink(name_permalink, df):
    try:
        return df[df['name_permalink'] ==name_permalink]
    except:
        print("pattern not found in dataframe - making api call to gather data")
        #get metadata

def get_pattern_metadata_from_url(pattern_url, df):
    name_permalink = get_name_permalink_from_url(pattern_url)
    return get_metadata_from_name_permalink(name_permalink)

def get_url_from_name_permalink(name_permalink):
    return("https://www.ravelry.com/patterns/library/" + name_permalink)

def get_index_from_name_permalink(name_permalink, df):
    return df[df['name_permalink'] ==name_permalink].index[0]


def get_url_from_index(idx, df):
    name_permalink = df.iloc[idx]['name_permalink']
    pattern_url = get_url_from_name_permalink(name_permalink)
    return pattern_url
# ------------------------------------------------
def list_top_popular_patterns(df):
    name_permalink_list = []
    image_url = []
    url = []
    for i in range(df.shape[0]):
        name_permalink_list.append(df.name_permalink.iloc[i])
        image_url.append(df.photos_url.iloc[i])
        url.append('https://www.ravelry.com/patterns/library/' +df.name_permalink.iloc[i])
    return name_permalink_list, image_url, url

def print_top_popular(name_permalink_list, image_url, url):
    for i in range(len(name_permalink_list)):
        print(f'{name_permalink_list[i]}, {url[i]}')
        
# def st_print_top_popular(name_permalink_list, image_url, url):
#     for i in range(len(name_permalink_list)):
#         st.write(f'{name_permalink_list[i]}, {url[i]}')

def get_popularity(df):
    """ Adds together favorites_count and projects_count as a populartiy metric.
    Used for output in simple recommender. """
    
    df['popularity'] = df.favorites_count+ df.projects_count
    df = df.sort_values("popularity", ascending =False)
    return df
#------------------------------------------------------------

class DataframeFunctionTransformer():
    """ Allows for functions on whole dataframe (like ones that take in more than one column to operate on """
    def __init__(self, func):
        self.func = func

    def transform(self, input_df, **transform_params):
        return self.func(input_df)

    def fit(self, X, y=None, **fit_params):
        return self
    
class ToDenseTransformer():
    """ Transforms sparse matrix (in the case of count vectorizing) to a dense one 
    (filled with zeros).  Used to ensure proper dimensions in order to feature union in pipeline"""
    # here you define the operation it should perform
    def transform(self, X, y=None, **fit_params):
        return X.todense()

    # just return self
    def fit(self, X, y=None, **fit_params):
        return self
    
def consolidate_gauge(df):
    """ takes in gauge columns and normalizes them all to stiches per inch """
    try:
        df['gauge_per_inch'] = df.loc[:,'gauge']/df.loc[:,'gauge_divisor']
    except:
        print("Error occured when consolidating gauge")
    return df


def encode_yarn_weights(df):
    """ uses yarn_weight_description to convert weights correspnding actual relative thicknesses
    indstry standards splits into 7 categories, but this goes more ganually """
    yarn_weights = {'Lace' : 1,
                    'Thread':1,
                    'Cobweb':1,
                    'Light Fingering':1.5,
                    'Fingering (14 wpi)': 2,
                    'Sport (12 wpi)': 3,
                    'DK / Sport' : 4,
                    'DK (11 wpi)' : 5,
                    'Worsted (9 wpi)':6,
                    'Aran / Worsted': 7,
                    'Aran (8 wpi)': 8,
                    'Bulky (7 wpi)':9,
                    'Super Bulky (5-6 wpi)':10,
                    'Jumbo (0-4 wpi)':11,
                    'No weight specified':5,
                    'Any gauge - designed for any gauge':5}
    try:
        df = df.replace({'yarn_weight_description':yarn_weights}) 
    except:
        print("okay - check out yarn_weight_description, something went wrong with the encoding")
    return df


def use_avg_yardage(df):
    df['yardage_max'] = df['yardage_max'].fillna(df['yardage'])
    df['yardage_avg'] = (df['yardage'] + df['yardage_max'])/2
    return df

# year -------------------------------------
def split_date_released(df):
    """ Takes 'generally_available' datetime column (containing when the pattern was released) and splits it into separate month and year columns (to take into account seasonal purchases, and yearly impacts)"""
    try:
        df['generally_available'] = pd.to_datetime(df['generally_available'], utc=True)
        df['month_avail'] = pd.to_numeric(df.generally_available.dt.month)
        df['year_avail'] = pd.to_numeric(df.generally_available.dt.year)
    except:
        "print - Error occured when trying to split dates"
    return df

def group_years(x):
    """ Reduce number of years into """
    if x < 2000:
        x = 1
    if (2000<=x) &(x<=2005):
        x = 2 
    if (x >= 2006)&(x<2011):
        x = 3
    if 2011 <= x<2017:
        x = 4
    elif x >= 2017:
        x = 5
    return x


def code_years(df):
    """ Convert ordinal years into a categorical feature.  (To be one-hot encoded in pipeline) """
    df = split_date_released(df)
    df['coded_year'] = df['year_avail'].apply(lambda x: str(group_years(x)))
    return df


def group_months(x):
    """ A binning function to reduce the number of months patterns are released. """
    if x < 3:
        x = 1
    if 3 <= x< 5:
        x = 2 
    if 5 <= x< 7:
        x = 3
    if 7 <= x< 9:
        x = 4
    if 9 <= x< 11:
        x = 5 
    elif 11 <= x< 13:
        x = 5 
    return x


def code_months(df):
    """ Convert ordinal months into a categorical feature.  (To be one-hot encoded in pipeline) """
    df = split_date_released(df)
    df['coded_month'] = df['month_avail'].apply(lambda x: str(group_months(x)))
    return df
#---------------------------------------------


# needles
def get_list_metric_needles(x):
    """Get the list of metric needle sizes for knitting (can have several needle sizes for various parts of the pattern and crochet hooks for finishing.  Generally the largest needle is the one used for the main body (or largest portion of the project) """
    n=[]
    for i in range(len(x)):
        if x[i]['knitting'] == True:
            n.append(x[i]['metric'])
    return n

def get_needle_size(df):
    try:
        df['needle_sizes']= df['pattern_needle_sizes'].apply(lambda x: ast.literal_eval(x))
        df['needle_sizes'] = df['needle_sizes'].apply(lambda x: get_list_metric_needles(x))
        df['needle_sizes']= df['needle_sizes'].apply(lambda x: max(x) if (len(x)>=1) else None)
    except:
        print('something went wrong with the Needle size conversion - please take a look.')
    return df
#----------------------------------------------

def parse_out_single_category(df):
    df['categories'] = df['categories'].apply(lambda x: ast.literal_eval(x))
    df['categories'] = df['categories'].apply(lambda x: x[0])
    return df

#-----------------------------------------------

def to_sentence(x):
    sentence = ' '.join(x)
    sentence =  sentence.replace('-', '')
    return sentence

def filter_words(x):
    list_attributes_to_keep = [ 'intarsia','lace','felted','fair-isle','eyelets', 'entrelac','duplicate-stitch','doll-size', 'buttoned','asymmetric','beads','bobble-or-popcorn','brioche-tuck', 'cables','ribbed','amigurumi','bias','double-knit','short-rows', 'slipped-stitches', 'stripes','thrums','short-rows', 'zipper', 'stranded', 'baby']#, 'icord',]
    new_words = list(filter(lambda w: w in list_attributes_to_keep, x))
    return new_words

def filter_attributes(df):   
    try:
        df['pattern_attributes'] = df['pattern_attributes'].apply(lambda x: ast.literal_eval(x))
    except:
        print("something went wrong with removing extra string from pattern attributes")
    df['pattern_attributes'] = df['pattern_attributes'].apply(lambda x: filter_words(x))
    df['pattern_attributes'] = df['pattern_attributes'].apply(lambda x: to_sentence(x))
    return df

def get_corpus(df):
    df = filter_attributes(df)
    corpus = df['pattern_attributes'].tolist()
    return corpus 


