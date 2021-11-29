import streamlit as st
import pandas as pd
import numpy as np
import requests
from util_functions import *


# Load the data
@st.cache(allow_output_mutation=True)
def load_data():
    data = pd.read_csv('data/patterns_cleaned.csv', low_memory=False)
    return data
df = load_data()

# Popularity dataframe
popular_df = get_popularity(df)

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

if option == 'Filter Based':
    text_input = st.text_input("Enter pattern url endpoint: ")
    st.write("eg http etc etc")
    st.markdown(f"my input is:, {text_input}")
    
    # st.sidebar.subheader("Content Based Filter") # or title instead of write
    filter_slider = st.sidebar.slider('Content Filter <-----------------> Colaborative Filter',0.,1.,0.)
    st.sidebar.write('Slider in the fully left position will give recommendations based on pattern feature (i.e. needle size, yarn weight, description) similarties.  Fully right slider recommendations will be based on user-pattern behaviours ("people that knit this pattern also knit these other patterns"). A slider in between will result in a hybrid weighted result.') 
    if filter_slider ==1.0:
        st.write('Colaborative Filtering Recommendations:')
    elif filter_slider ==0.0:
        st.write('Content Based Recommendations:')
    else:
        st.write('Hybrid Filtering Recommendations:')

   
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