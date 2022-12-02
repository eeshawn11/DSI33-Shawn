import streamlit as st
import joblib
import pandas as pd
import numpy as np
import re
from string import punctuation
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import nltk
nltk.download('wordnet')

wn = nltk.WordNetLemmatizer()

pipe = joblib.load('/app/dsi33-shawn/Project3/streamlit/subreddit_model.pkl')

def clean_text(text):
    '''
    Returns a string that has been cleaned and prepared to use with a vectoriser.
    '''
    wn = WordNetLemmatizer()
    # add extra stopwords
    extra_stopwords = [
        "im", "ve", "ive", "hello", "view",
        "poll", "dont", "know", "ampx200b",
        "wa", "ha", "just", "like",
        "got", "did", "bootcamp",
        "bootcamps", "boot", "camp",
        "feel", "free", "want", "thanks",
    ]
    custom_stopwords = ENGLISH_STOP_WORDS.union(extra_stopwords)

    text = re.sub(r"/\[.+\]|\(.+\)|https?:\/\/.+\b", "", text.lower())
    text_nopunct = "".join([char for char in text if char not in punctuation])
    tokens = re.split(r"\W+", text_nopunct)
    tokens_lm = [wn.lemmatize(token) for token in tokens if token]
    text_cleaned = " ".join(
        [token for token in tokens_lm if token not in custom_stopwords]
    )
    return text_cleaned if len(text_cleaned) else ""

def feature_importances_NB(clf, data):
    """
    Returns the importances of words present in data, as measured
    in their contribution to the difference in the log probabilities
    between the two classes.
    
    clf: a fitted MultiNomialNB classifier, with 2 classes
    data: a 1-D numpy array with counts
    
    returns: a 1-D numpy array of the size of data
    """
    # difference between \theta's for both classes
    delta_log_prob = clf.feature_log_prob_[1, :] - clf.feature_log_prob_[0, :]
    return np.multiply(data, delta_log_prob)

def get_top_N_features(pipe, text):
    """
    Returns a dataframe, with the token name and its feature importance to class 1
    relative to class 0 in terms of log-probabilities 
    (positive: contributes positively to the prediction for class 1)
    """
    if len(text.split(" ")) < 10:
        N = len(text.split(" "))
    else:
        N = 10
    data = np.asarray(pipe[0].transform([text]).todense()).reshape(-1) # Generate a non-sparse count vector
    feature_importances = feature_importances_NB(pipe[1], data)
    topN_features_idx = np.argsort(np.abs(feature_importances))[-N:]
    return pd.DataFrame([(pipe[0].get_feature_names_out()[i], 
                       '{:.3f}'.format(feature_importances[i]) 
                  ) for i in topN_features_idx[::-1]], columns=['Top Features', 'Feature Importance'])


st.title("Subreddit Classification Model")
st.markdown("""
        This is a simple web app deployment of a Reddit.com subreddit classifier, 
        built as part of General Assembly Singapore's Data Science Immersive program. 
        The model aims to use NLP to classify posts between two related subreddits: *r/codingbootcamp* and *r/csMajors*.
    """)

st.subheader("Model")
st.markdown("""
        Text input into the text box will be cleaned and lemmatised. 
        Using a sklearn pipeline consisting of a `CountVectorizer` and `Multinomial Naive Bayes` classifier, 
        the model will then attempt to predict which subreddit this post belongs to.
    """)
st.markdown("""
        - After prediction, we will return the top 10 features extracted from the input text.
        - A positive number indicates this feature contributes to the prediction for class 1 (r/codingbootcamp), while the magnitude indicates its importance.
        - 
    """)
st.markdown("---")

form = st.form(key='input text')
message = form.text_area('Enter your text here', height=50)
submit = form.form_submit_button('Predict')

if submit:
    # predictions
    text = clean_text(message)
    pred = pipe.predict([text])

    if text == "":
        st.error('Sorry, no tokens found. Please input some text and try again!')
    else:
        if pred == 1:
            subreddit = 'r/codingbootcamp'
            st.success(f'**Predicted Subreddit**: {subreddit}', icon='👍')
        elif pred == 0:
            subreddit = 'r/csMajors'
            st.warning(f'**Predicted Subreddit**: {subreddit}', icon='👎')
        st.write(get_top_N_features(pipe, text))

