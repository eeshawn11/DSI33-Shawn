from flask import Flask,render_template,url_for,request
import joblib
from sklearn.pipeline import Pipeline
from string import punctuation
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from nltk import WordNetLemmatizer
import re
wn = WordNetLemmatizer()

def clean_text(text):
    # remove URLs and tags in [] or ()
    text = re.sub(r'/\[.+\]|\(.+\)|https?:\/\/.+\b', "", text.lower()) 
    text_nopunct = "".join([char for char in text if char not in punctuation])
    tokens = re.split(r'\W+', text_nopunct)
    # lemmatize words before dropping stopwords
    tokens_lm = [wn.lemmatize(token) for token in tokens if len(token)]
    text_cleaned = [token for token in tokens_lm if token not in ENGLISH_STOP_WORDS]
    return text_cleaned if len(text_cleaned) else None

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/', methods=['POST'])
def predict():
	# df= pd.read_csv("records_adhd_anxiety.csv")
	# # Features and Labels
	# df['label'] = df['class'].map({'ham': 0, 'spam': 1})
	# X = df['message']
	# y = df['label']
	
	# # Extract Feature With CountVectorizer
	# cv = CountVectorizer()
	# X = cv.fit_transform(X) # Fit the Data
	# from sklearn.model_selection import train_test_split
	# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
	# #Naive Bayes Classifier

	# clf = MultinomialNB()
	# clf.fit(X_train,y_train)
	# clf.score(X_test,y_test)
	#Alternative Usage of Saved Model
	# joblib.dump(clf, 'NB_spam_model.pkl')
	# NB_spam_model = open('NB_spam_model.pkl','rb')
	pipe = joblib.load('subreddit_model.pkl')

	if request.method == 'POST':
		message = request.form['message']
		data = clean_text(message)
		# include the clean text function here?
		my_prediction = pipe.predict(data)
	return render_template("home.html", prediction=my_prediction)

if __name__ == '__main__':
	app.run(debug=True)