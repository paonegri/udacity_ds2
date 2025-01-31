'''
TRAIN CLASSIFIER
> python train_classifier.py ../data/disaster_dataset.db classifier.pkl
input:
    1) SQLite db path (containing pre-processed data)
    2) pickle file name to save ML model
'''

# import libraries
import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, f1_score, make_scorer
from sklearn.decomposition import TruncatedSVD
import pickle


def load_data(database_filepath):
    '''
    input:
        database_filepath: path to SQLite db
    output:
        X: feature DataFrame
        Y: label DataFrame
        category_names: used for data visualization (app)
    '''
    # load data from database
    engine = create_engine('sqlite:///'+database_filepath)
    df = pd.read_sql_table('df',engine)
    X = df['message']
    Y = df.iloc[:,4:]
    category_names = Y.columns
    return X, Y, category_names


def tokenize(text):
    '''
    input:
        text: list of text messages (english)
    output:
        clean_tokens: tokenized text, clean for ML modeling
    '''
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
    return clean_tokens


def build_model():
    '''
    input:
        N/A
    output:
        returns the model
    '''
    pipeline = Pipeline([
       ('vect', CountVectorizer(tokenizer=tokenize)),
       ('tfidf', TfidfTransformer()),
       ('clf', MultiOutputClassifier(RandomForestClassifier()))])

    parameters =  {
        'tfidf__use_idf': (True, False),
        'clf__estimator__n_estimators': [50, 100],
        'clf__estimator__min_samples_split': [2, 4]
        }

    model = GridSearchCV(pipeline, param_grid=parameters)

    return model


def evaluate_model(model, X_test, Y_test, category_names):
    '''
    input:
        model: Scikit ML Pipeline
        X_test: test features
        Y_test: test labels
        category_names: label names (multi-output)
    output:
        print accuracy, f1 score
    '''
    y_pred = model.predict(X_test)
    for i, col in enumerate(category_names):
        print (col)
        print(classification_report(Y_test[col], y_pred[:,i]))

    overall_accuracy = (y_pred == Y_test).mean().mean()
    print('overall accuracy {0:.4f} \n'.format(overall_accuracy))


def save_model(model, model_filepath):
    '''
    input:
        model and the file path to save the model
    output:
        save the model as pickle file in the give filepath
    '''
    pickle.dump(model, open(model_filepath, 'wb'))


def main():
    if len(sys.argv) == 3:
        database_filepath, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)

        print('Building model...')
        model = build_model()

        print('Training model...')
        model.fit(X_train, Y_train)

        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()
