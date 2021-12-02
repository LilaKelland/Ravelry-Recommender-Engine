## This is NOT pretty, but gets a rough job done - will be cleaning/ fixing this up in near future (with pickles etc)

# Import the required plugins
from flask import Flask, request, jsonify, render_template
import flask.scaffold
flask.helpers._endpoint_from_view_func = flask.scaffold._endpoint_from_view_func
from flask_restful import Api, Resource, reqparse 
import pickle
import pandas as pd
import numpy as np
from util_functions import *
import ast

# For numerically encoding and preprocessing patterns in order to compare similarity
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, FeatureUnion

# similarity metrics 
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import pairwise_kernels
from sklearn.metrics.pairwise import euclidean_distances

# kNN 
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

app = Flask(__name__)
# api = Api(app) 

# get data
df = pd.read_csv('data/patterns_cleaned.csv', low_memory=False)


# kNN ----------------------------------------------------------------
def get_pattern_id_from_name(name_permalink):
    pattern_id = metadata[metadata.name_permalink == name_permalink]['pattern_id']
    return pattern_id[pattern_id.keys()[0]]

def get_index_from_pattern_id(pattern_id):
    return metadata[metadata.pattern_id == pattern_id].index[0]

def get_pattern_name_from_index(pattern_index):
    return metadata[metadata.index == pattern_index]["name_permalink"].values[0]

def get_image_from_index(pattern_index):
    return metadata[metadata.index == pattern_index]["photos_url"].values[0]

def get_pattern_name_from_pattern_id(pattern_id):
    name = metadata[metadata.pattern_id == pattern_id]['name_permalink']
    return name[name.keys()[0]]

def get_index_from_pattern_id(pattern_id):
    return metadata[metadata.pattern_id == pattern_id].index[0]





df_knn = pd.read_csv('data/less_sparse_users_patterns.csv', low_memory=False)
metadata = df[df['pattern_id'].isin(df_knn.pattern_ids.values)]

# utility matrix for knn
user_knit = df_knn.copy()
user_knit = user_knit.drop_duplicates(['user_id', 'pattern_ids'])  

user_knit_pivot = user_knit.pivot(index='pattern_ids', columns='user_id', values='has_knit').fillna(0)
user_knit_matrix = csr_matrix(user_knit_pivot.values)

model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(user_knit_matrix)
#-----------------------------------------------------------------
# Euclidean distances (content)-----------------------------------

# pipeline = pickle.load( open( "pipeline.pickle", "rb" ) )

categorical_features = ['free', 'pattern_type_names',  'coded_year']#,'downloadable', 'coded_month',]
numeric_features = ['yardage', 'difficulty_average','gauge_per_inch', 'yardage_avg',]
custom_function_pre_encoded_features = ['yarn_weight_description', 'needle_sizes']

custom_function_transformer = Pipeline(steps=[
                                    ("cosolidate_gauge", DataframeFunctionTransformer(consolidate_gauge)),
                                    ("use_avg_yardage", DataframeFunctionTransformer(use_avg_yardage)),
                                    ("encode_yarn_weights", DataframeFunctionTransformer(encode_yarn_weights)),
                                    ("get_needle_size", DataframeFunctionTransformer(get_needle_size)), 
#                                     ("encode_months",DataframeFunctionTransformer(code_months)), 
                                    ("encode_years",DataframeFunctionTransformer(code_years)), 
                              # NOTE NEED TO DOWNWEIGHT THESE!!
                                    ]) 

attributes_transformer = Pipeline(steps=[("get_corpus", FunctionTransformer(get_corpus)),
                                    ('count_vectorize_attributes', CountVectorizer()),
                                    ('to_dense', ToDenseTransformer())]) 


numeric_transformer = Pipeline(steps=[('impute_mode', SimpleImputer(strategy='median')), 
                                      ('scaling', StandardScaler())]) 


categorical_transformer = Pipeline(steps=[('impute_mode', SimpleImputer(strategy='most_frequent')), 
                                          ('one-hot-encode', OneHotEncoder(sparse=False))])

pre_encoded_feature_transformer = Pipeline(steps=[
                                    ('impute_mode', SimpleImputer(strategy='median'))])


preprocessor = ColumnTransformer(
               transformers=[('pre-ecoded_features', pre_encoded_feature_transformer, custom_function_pre_encoded_features),
                             ('numeric', numeric_transformer, numeric_features),
                             ('categorical', categorical_transformer, categorical_features)]) 


main_pipeline = Pipeline(steps = [('custom_feature_transform', custom_function_transformer),
                            ('preprocessor', preprocessor)])

pipeline = FeatureUnion([('main_pipeline', main_pipeline),
                            ('attributes', attributes_transformer)])

X = pipeline.fit_transform(df)

    
def find_top_eucliedean_recommendations_df(name_permalink):
  
    # Find index
    try:
        pattern_to_compare = X[get_index_from_name_permalink(name_permalink,df)] 
    except:
        # transform through preprocessing pipeline
        print("pattern wasn't processed yet - try to process it now")
        pattern_to_compare  = get_pattern_metadata_from_url(pattern_url, df)
#         need to download single pattern 
        pattern_to_compare = pipeline.transform(pattern_to_compare)
        pattern_to_compare = get_metadata_from_name_permalink(name_permalink, df)

    # Get distances from all other patterns
    distances = euclidean_distances(X, pattern_to_compare)
    distances = distances.reshape(-1)   
    df['distances'] = distances
    
    # Find N number of indices with the least distance to chosen pattern 
    ordered_indices = distances.argsort()
    closest_indices = ordered_indices[:20]

    # # Get the patterns for these indices

    closest_df = df.iloc[ordered_indices]
    closest_df['rank'] = df['distances'].rank()
    return closest_df

def list_top_euclidean_recommendations(df):
    df =df[0:10]

    recommendations = []
    for i in range(df.shape[0]):
        reco = {'name_permalink': df.name_permalink.iloc[i],
        'image_url':df.photos_url.iloc[i],
        'distances':df.distances.iloc[i],
        'url':'https://www.ravelry.com/patterns/library/' +df.name_permalink.iloc[i]}
        recommendations.append(reco)
    return recommendations

def print_top_euclidean_recommendations(name_permalink_list, image_url, url, distances):
    for i in range(len(name_permalink_list)):
        print(f'{name_permalink_list[i]},\t {url[i]}, \t {distances[i]:.4f}')
# ----------------------------------------------------------------

@app.route("/")
def home():
#         return {"hello":"world"}
    return render_template('index.html')

# class Recommend(Resource):

@app.route("/recommend/<name_permalink>")
def recommend(name_permalink):
    try:

        if name_permalink:
            greeting = f'Recommendations for pattern https://www.ravelry.com/patterns/{name_permalink}'
    #   kNN------------------------------------------------
            chosen_name_permalink = name_permalink
            query_pattern_id = get_pattern_id_from_name(chosen_name_permalink)
            distances, indices = model_knn.kneighbors(user_knit_pivot.loc[query_pattern_id,:].values.reshape(1, -1), n_neighbors = 10)  

            # give recomendations for the pattern selected
            recommendations_colab=[]
            pattern_ids=[]
            pattern_indices = []
            pattern_name= []
            for i in range(0, len(distances.flatten())):
                if i == 0:
                    print('Recommendations for {0}:\n'.format(get_pattern_name_from_index(get_index_from_pattern_id(int(query_pattern_id)))))

                else:
                    pattern_id = int(user_knit_pivot.index[indices.flatten()[i]])
                    pattern_metadata_index = get_index_from_pattern_id(pattern_id)
                    pattern_name = get_pattern_name_from_index(pattern_metadata_index)
                    pattern_indices.append(pattern_metadata_index)
                    print('{0}: {1} {2}, with distance of: {3}'
                            .format(i, pattern_id, pattern_name, distances.flatten()[i]))


                    reco = {'name_permalink': pattern_name,
                    'image_url':get_image_from_index(pattern_metadata_index),
                    'url':'https://www.ravelry.com/patterns/library/' +pattern_name}
                    recommendations_colab.append(reco)


    #             closest_df_knn = metadata.loc[pattern_indices]
    # ----------------------------------------------------
    # euclidean distance ---------------------------------

            recommended_df= find_top_eucliedean_recommendations_df(name_permalink)
            recommendations = list_top_euclidean_recommendations(recommended_df)
            #print_top_euclidean_recommendations(name_permalink_list,  image_url,  url, distances)
            return render_template('recommend.html', name_permalink=name_permalink, recommendations=recommendations, recommendations_colab=recommendations_colab)
        else:
            return( 'Please add a pattern name (the end point after https://www.ravelry.com/patterns/library)')
    except:
        
        return ("Sorry didn't have that pattern (still work in progress) please try a more popular one.)



if __name__ == '__main__': 
#     app.run(debug=True)
    app.run(host='0.0.0.0')