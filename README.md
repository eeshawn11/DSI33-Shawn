# General Assembly Data Science Immersive

Showcase of data science projects completed during the General Assembly Data Science Immersive program, as well as other side projects completed out of interest.

---

### [Project 4 - West Nile Virus Prediction Kaggle Challenge](https://github.com/eeshawn11/DSI33-Shawn/tree/main/Project4)

Creating a classification model that predicts the presence of West Nile virus to allow for effective allocation of city resources.

#### Skills demonstrated:

- Basic collaboration and version control with `git`
- Addressing class imbalance with `imblearn`, taking into account ideal evaluation metric
- Ensemble classification models with `scikit-learn`, e.g. Adaptive Boosting, Histogram-based Gradient Boosting

### [Project 3 - Subreddit Classifier](https://github.com/eeshawn11/DSI33-Shawn/tree/main/Project3)

Using NLP to create a classification model that is able to accurately classify a Reddit.com post between two subreddits: r/codingbootcamp and r/csMajors. Achieved an F1-score of 93% and deployed a demonstration web app via [streamlit](https://shawn-nlp-classifier.streamlit.app).

#### Skills demonstrated:

- Data extraction with [Pushshift API](https://github.com/pushshift/api) and `requests`
- Natural Language Processing using `NLTK` and `RegEx`
- Vectorisation with `scikit-learn` Count Vectorizer and TF-IDF Vectorizer
- Classification models with `scikit-learn`, e.g. Logistic Regression, Naive Bayes, Random Forest and Support Vector Machine
- Python web app deployment with [`Flask`](https://github.com/eeshawn11/DSI33-Shawn/blob/main/Project3/app/app.py) and [`streamlit`](https://shawn-nlp-classifier.streamlit.app)

### [Project 2 - Ames Housing Data and Kaggle Challenge](https://github.com/eeshawn11/DSI33-Shawn/tree/main/Project2)

Training and developing a regression model to predict the housing price of a property in Ames, Iowa. Achieved a 84.44% R2 using a Lasso Regression model.

#### Skills demonstrated:

- Feature Engineering and Selection with over 80 features in the dataset
- Regression models with `scikit-learn`, e.g. Linear, Lasso, Ridge
- Utilising machine learning `Pipeline` and `GridSearchCV` for hyperparameter tuning

### [Project 1 - Standardised Test Analysis](https://github.com/eeshawn11/DSI33-Shawn/tree/main/Project1)

An exploratory analysis into SAT 2019 performance in the state of California, United States, to identify districts with the lowest overall student performance so the California Department of Education can recommend programs and better allocate resources to such districts in need.

#### Skills demonstrated:

- Exploratory Data Analysis with `pandas`
- Data Visualisation with `matplotlib` and `seaborn`

---

### [HDB Resale Price Dashboard](https://github.com/eeshawn11/DSI33-Shawn/tree/main/Side_Projects/HDB_Resale_Price) [Ongoing]

Exploration of a data set from [Data.gov.sg](https://data.gov.sg/), in particular HDB resale prices from 2012, to create an interactive dashboard. I am also hopeful that any insights gleaned could be helpful to my own HDB purchase journey.

This is an ongoing project to document my learning with using Streamlit and various Python libraries. While such a dashboard could perhaps be more easily created using PowerBI or Tableau, I am also taking the opportunity to explore the various Python plotting libraries and understand their documentation.

#### Skills demonstrated:

- Data extraction from live Data.gov.sg API
- Data visualisation with `Vega-Altair` and `Plotly`
- Python web app deployment with [`streamlit`](https://shawn-hdb-resale-viz.streamlit.app/)

### [Naruto Hand Seals - Gesture Recognition](https://github.com/eeshawn11/DSI33-Shawn/tree/main/Side_Projects/Naruto_Gesture_Recognition) [WIP]

Training and deploying a machine learning model that can recognise 12 basic hand seals from the Naruto anime using TensorFlow's Object Detection API.

While the model appears to be able to detect and recognise the hand seals that I am making, it also recognises my face as a "rat" seal, so perhaps there's more to be done to overcome this. Next step would also include deploying the model online, so you could also give it a try!

#### Skills demonstrated:

- Collecting and building my own dataset using `OpenCV` and annotating the collected images with `LabelImg`
- Transfer learning using a pre-trained network with `TensorFlow` Object Detection API
