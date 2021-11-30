import streamlit as st
import pandas as pd
import numpy as np
import requests
from util_functions import *
# KNN
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

# Load the data
@st.cache(allow_output_mutation=True)
def load_data():
    data = pd.read_csv('data/patterns_cleaned.csv', low_memory=False)
    return data
df = load_data()

# Popularity dataframe
popular_df = get_popularity(df)
name_permalink_list, image_url, url = list_top_popular_patterns(popular_df[0:20])

# knn
df_knn = pd.read_csv('data/less_sparse_users_patterns.csv', low_memory=False)
metadata = df[df['pattern_id'].isin(df_knn.pattern_ids.values)]

# utility matrix for knn
user_knit = df_knn.copy()
user_knit = user_knit.drop_duplicates(['user_id', 'pattern_ids'])  

user_knit_pivot = user_knit.pivot(index='pattern_ids', columns='user_id', values='has_knit').fillna(0)
user_knit_matrix = csr_matrix(user_knit_pivot.values)

model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(user_knit_matrix)


st.title("Ravelry Recommender Engine Demo")
st.subheader("Recommender SYSTEMS IMAGE GOES HERE!")
st.write("Recommender engines usually are a hybrid of content based and colaborative filters.  Feel free to ... For this demo, only item-item...  Not all patterns have been modeled - for content based, if the pattern is not in the will be pulled through api and processed which may take some time.  Thank you for your patience. ")
# st.header("This is a header")
# st.subheader("This is a header")
# st.write("This is regular text")
st.sidebar.title("Recommendation Type")
option = st.sidebar.selectbox('',('Simple Recommender', 'Filter Based'))

if option == 'Simple Recommender':
    st.header('Recommendations Based on Popularity')
    st.write('These recommendations are based on a combination of favourites (likes) counts and number of projects made counts per pattern. These are independent of user behaviour or pattern details.')
    
    if st.checkbox('View Raw Data'):
        st.dataframe(popular_df[0:100])

    for i in range(len(name_permalink_list)):
        st.write(f'{i+1}. {name_permalink_list[i]}, {url[i]}')
        st.image(image_url[i])


if option == 'Filter Based':

    st.write("Some pattern examples to try are: alaska-6,  ")
    st.write("Alternatively you can go check out the website and find something you like.  Please note to prevent 'cold start'; for this system, the chosen pattern needs at least 300 completed projects for collaborative filtering.")
    text_input = st.text_input("Enter pattern url endpoint (https://www.ravelry.com/patterns/library/_______): ")
    st.markdown(f"Your selected pattern for recommendations is:  https://www.ravelry.com/patterns/library/{text_input}")
    
    # st.sidebar.subheader("Content Based Filter") # or title instead of write
    filter_slider = st.sidebar.slider('Content Filter <-----------------> Colaborative Filter',0.,1.,0.)
    st.sidebar.write('Slider in the fully left position will give recommendations based on pattern feature (i.e. needle size, yarn weight, description) similarties.  Fully right slider recommendations will be based on user-pattern behaviours ("people that knit this pattern also knit these other patterns"). A slider in between will result in a hybrid weighted result.') 
    if filter_slider ==1.0:
        st.subheader('Colaborative Filtering Recommendations:')

        chosen_name_permalink = 'eunice'
        query_pattern_id = get_pattern_id_from_name(chosen_name_permalink)
        distances, indices = model_knn.kneighbors(user_knit_pivot.loc[query_pattern_id,:].values.reshape(1, -1), n_neighbors = 10)  

        # give recomendations for the pattern selected
        pattern_ids=[]
        pattern_indices = []
        pattern_name= []
        for i in range(0, len(distances.flatten())):
            if i == 0:
                st.write('Recommendations for {0}:\n'.format(get_pattern_name_from_index(get_index_from_pattern_id(int(query_pattern_id)))))

        else:
            pattern_id = int(user_knit_pivot.index[indices.flatten()[i]])
            pattern_metadata_index = get_index_from_pattern_id(pattern_id)
            pattern_name = get_pattern_name_from_index(pattern_metadata_index)
            pattern_indices.append(pattern_metadata_index)
            st.write('{0}: {1} {2}, with distance of: {3}'
                    .format(i, pattern_id, pattern_name, distances.flatten()[i]))
    
        closest_df_knn = metadata.loc[pattern_indices]

        # check number of patterns - make sure it will work - if not print out diff subheader and note
    elif filter_slider ==0.0:
        st.subheader('Content Based Recommendations:')
        # check number of patterns - make sure it will work - if not print out diff subheader and note
    else:
        st.subheader('Hybrid Recommendations:')

    if st.checkbox('View Raw Data'):
        st.dataframe(popular_df[0:100])
   
# """ 
# # header
# This is markdown
# """


 
# df = pd.DataFrame(np.random.randn(50,20), columns=('col %d' % i for i in range(20)))
# df = load_data
# df = pd.read_csv('data/patterns_cleaned.csv', low_memory=False)
# st.dataframe(df[0:100]) # displays whole 
# #  st.image(<imageurl>)
 
# def slider_inputs():
#     data = {'simple_filter':simple_filter_slider,
#     'content_filter': content_filter_slider,
#     'colaborative_filter':colaborative_filter_slider
#      }
#     sliding_weights = pd.DataFrame(data, index=[0])
#     return sliding_weights

# st.sidebar.header("Filter Weights")
# df = slider_inputs()
# st.sidebar.write(df)



                                                   
# /*if option =="Email":
#         st.subheader("twitter dashboard logic")
#         r = requests.get("https://api....")
#                                                    data = r.json()
#                                                    st.write(data)
#                                                    st.image['user']['avatar_url']*/

st.write("Note: This project is not associated with Ravelry. Data was graciously provided by Ravelry through public api.")