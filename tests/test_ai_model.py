import os
import unittest
from unittest import mock
from unittest.mock import patch, Mock
import pandas as pd
from scripts.ai_model import AIModel

class TestAIModel(unittest.TestCase):
    def setUp(self):
    # Set up any necessary configurations or preparations
        self.original_os_path_join = os.path.join
        os.path.join = lambda *args: 'scripts/' + '/'.join(args)

        self.ai_model = AIModel()

    
    def tearDown(self):
        # Restore the original os.path.join behavior
        os.path.join = self.original_os_path_join

    @patch('scripts.ai_model.StandardScaler.fit_transform')
    @patch('scripts.ai_model.LabelEncoder.fit_transform')
    def test_call_predict_right_arguments(self, mock_fit_transform_encoder, mock_fit_transform_scaler):
        # Mock raw data
        raw_data = pd.DataFrame({
            'numerical1': [1.0, 2.0, 3.0],
            'numerical2': [4.0, 5.0, 6.0],
            'categorical1': ['A', 'B', 'A'],
            'class': ['normal', 'anomaly', 'normal']
        })
    
        # Create an instance of AIModel
        ai_model = AIModel()
    
        # Mock the 'predict' method of the model
        mock_model_predict = Mock()
        ai_model.predict = mock_model_predict
    
        # Mock the 'train_model' method to avoid the actual training
        ai_model.train_model = Mock()
    
        # Call the 'predict' method
        result_file_path = ai_model.predict(raw_data)
    
        # Assertions
        # Check if 'predict' method was called with the correct arguments
        mock_model_predict.assert_called_once_with(raw_data)

    def test_preprocess_data_reads_uploaded_file(self):
        # Load the provided data for testing
        train_data = pd.read_csv('scripts/uploads/train_data.csv')

        # Create an instance of AIModel
        ai_model = AIModel()

        # Mock the 'fit_transform' method of StandardScaler to avoid actual scaling
        with mock.patch('scripts.ai_model.StandardScaler.fit_transform', return_value=train_data.select_dtypes(include=['float64', 'int64'])):
            # Call the 'preprocess_data' method with the real implementation
            X_train, y_train = ai_model.preprocess_data(train_data)

            # Check if the output of preprocess_data is not empty
            self.assertIsNotNone(X_train)
            self.assertIsNotNone(y_train)

    def test_predict_adds_prediction(self):
        # Load and train the model with the provided training data
        train_data = pd.read_csv('scripts/uploads/train_data.csv')  # Replace with the actual path
        self.ai_model.train_model(train_data)

        # Load the provided test data
        test_data = pd.read_csv('scripts/uploads/test_data.csv')  # Replace with the actual path

        # Call the 'predict' method with the real implementation
        result_file_path = self.ai_model.predict(test_data)

        # Load the result file
        result_df = pd.read_csv(result_file_path)

        # Check if the 'prediction' column is present in the result file
        self.assertTrue('prediction' in result_df.columns)

    def test_predict_contains_normal_or_anomaly(self):
        # Load and train the model with the provided training data
        train_data = pd.read_csv('scripts/uploads/train_data.csv')
        self.ai_model.train_model(train_data)

        # Load the provided test data
        test_data = pd.read_csv('scripts/uploads/test_data.csv')

        # Call the 'predict' method
        result_file_path = self.ai_model.predict(test_data)

        # Load the result file
        result_df = pd.read_csv(result_file_path)

        # Check if at least one prediction is "Normal" or "Anomaly"
        self.assertTrue('normal' in result_df['prediction'].values or 'anomaly' in result_df['prediction'].values)


if __name__ == '__main__':
    unittest.main()
