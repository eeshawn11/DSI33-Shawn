from flask import Flask,render_template,request
import joblib
from string import punctuation
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk import WordNetLemmatizer
import re

def clean_text(text):
    '''
    Prepare text for modelling
    
    Parameters
    ----------
    text : str
        String text to clean, lemmatize and drop stopwords
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

    # convert to lower case, remove URLs and tags in [] or ()
    text = re.sub(r"/\[.+\]|\(.+\)|https?:\/\/.+\b", "", text.lower())
    # remove punctuation
    text_nopunct = "".join([char for char in text if char not in punctuation])
    # tokenize
    tokens = re.split(r"\W+", text_nopunct)
    # lemmatize
    tokens_lm = [wn.lemmatize(token) for token in tokens if len(token)]
    # drop stopwords
    text_cleaned = " ".join(
        [token for token in tokens_lm if token not in custom_stopwords]
    )
    return text_cleaned if len(text_cleaned) else ""

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/', methods=['POST'])
def predict():
	# load model
	pipe = joblib.load('subreddit_model.pkl')

	if request.method == 'POST':
		message = request.form['message']
		if not message:
			error = 'Please input your message.'
			return render_template("home.html", error=error)
		elif message:
			data = clean_text(message)
			if data == "":
				error = 'Sorry, no keywords found. Please try again with a different message.'
				return render_template("home.html", error=error)
			elif data:
				my_prediction = pipe.predict([data])
				return render_template("home.html", prediction=my_prediction, message=data)


if __name__ == '__main__':
	app.run(debug=True)