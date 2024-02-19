from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import pandas as pd
import os

class AIModel:
    def __init__(self):
        # Initialize your model and any required components here
        self.classifiers = [
            ('Random Forest', RandomForestClassifier()),
            ('Gradient Boosting', GradientBoostingClassifier()),
            ('Logistic Regression', LogisticRegression()),
            ('SVM', SVC()),
            ('Naive Bayes', GaussianNB()),
            ('K-Nearest Neighbors', KNeighborsClassifier())
        ]
        self.voting_classifier = VotingClassifier(estimators=self.classifiers, voting='hard')
        self.encoder = LabelEncoder()
        self.scaler = StandardScaler()


    def preprocess_data(self, data, is_train=True):
        # Remove redundant columns
        # data = self.remove_constant_columns(data)

        # Scaling numerical attributes
        cols = data.select_dtypes(include=['float64', 'int64']).columns
        sc_data = self.scaler.fit_transform(data.select_dtypes(include=['float64', 'int64']))
        sc_df = pd.DataFrame(sc_data, columns=cols)

        # Encoding categorical attributes
        if is_train:
            cat_data = data.select_dtypes(include=['object']).copy()
            enc_data = cat_data.apply(self.encoder.fit_transform)
            enctrain = enc_data.drop(['class'], axis=1)
            cat_Ytrain = enc_data[['class']].copy()
            result_df = pd.concat([sc_df, enctrain], axis=1)
            return result_df, data['class']
        else:
            enc_data = data.select_dtypes(include=['object']).apply(self.encoder.fit_transform)
            result_df = pd.concat([sc_df, enc_data], axis=1)
            return result_df
        
    def train_model(self, train_data):
        # Train the ensemble model
        X_train, y_train = self.preprocess_data(train_data)
        self.voting_classifier.fit(X_train, y_train)


    def predict(self, test_data):
        # Make predictions on the test data
        test_data_processed = self.preprocess_data(test_data, is_train=False)
        predictions = self.voting_classifier.predict(test_data_processed)

        # Add predictions to the test data
        test_data['prediction'] = predictions

        # Save the results to a CSV file
        result_file_path = os.path.join('uploads', 'test_results.csv')
        test_data.to_csv(result_file_path, index=False)

        return result_file_path
    
    # the remove_constant_columns method is only an addition to the model, 
    # which can be used only when the column is constant in both the train dataset and the test dataset
    # if the column is constant in only one of the datasets it will bring error: "Feature names unseen at fit time:" 
    # since we cannot prove that, we can not use this method, however if the client can prove this with their dataset
    # the feature can be activated with some minimal changes to the code
    @staticmethod
    def remove_constant_columns(data, excluded_columns=None):
        if excluded_columns is None:
            excluded_columns = []
        constant_columns = [col for col in data.columns if col not in excluded_columns and data[col].nunique() == 1]
        data.drop(columns=constant_columns, inplace=True)
        return data
    
    # the following methods are a good way to continue developing the project
    # by saving and loading a flagged internal status of the model
    """def save_model(self, model_path='trained_model.joblib'):
        joblib.dump(self.model, model_path)

    def load_model(self, model_path='trained_model.joblib'):
        self.model = joblib.load(model_path)"""
    
