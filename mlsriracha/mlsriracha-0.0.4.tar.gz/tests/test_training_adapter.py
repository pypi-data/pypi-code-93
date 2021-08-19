from unittest import mock
import unittest

from mlsriracha.plugins.azureml.train import AzureMlTrain
from mlsriracha.plugins.gcpvertex.train import GcpVertexTrain
from mlsriracha.plugins.awssagemaker.train import AwsSageMakerTrain


class TestTrainingAdapter(unittest.TestCase):

    # @mock.patch('mlsriracha.plugins.awssagemaker.train.Path.mkdir', return_value=[Tru])
    def test_awssagemaker_plugin(self):
        with mock.patch('mlsriracha.plugins.awssagemaker.train.Path.mkdir', autospec=True) as mock_mkdir:
            mock_mkdir.return_value = True
            plugin = AwsSageMakerTrain()
            
        response = plugin.finish()
        self.assertTrue(response)
    
    
    def test_awssagemaker_data(self):
         with mock.patch('mlsriracha.plugins.awssagemaker.train.Path.mkdir', autospec=True) as mock_mkdir:
            with mock.patch('mlsriracha.plugins.awssagemaker.train.glob.glob', autospec=True) as mock_glob:
                mock_mkdir.return_value = True
                mock_glob.return_value = ['./static/data/data.csv']
                plugin = AwsSageMakerTrain()
               
                response = plugin.input_as_dataframe(channel='training')
                # print(response.size)
                self.assertTrue(response.size == 15)

    def test_awssagemaker_folder(self):
         with mock.patch('mlsriracha.plugins.awssagemaker.train.Path.mkdir', autospec=True) as mock_mkdir:
                mock_mkdir.return_value = True
                plugin = AwsSageMakerTrain()
               
                response = plugin.log_artifact('model.pkl')
                print(response)
                self.assertTrue(response == '/opt/ml/model/model.pkl')

    def test_azureml_plugin(self):
        with mock.patch('mlsriracha.plugins.azureml.train.Path.mkdir', autospec=True) as mock_mkdir:
            mock_mkdir.return_value = True
            plugin = AzureMlTrain()
        
        response = plugin.finish()
        self.assertTrue(response)

    def test_azureml_data(self):
         with mock.patch('mlsriracha.plugins.azureml.train.Path.mkdir', autospec=True) as mock_mkdir:
            with mock.patch('mlsriracha.plugins.azureml.train.os.environ.get', autospec=True) as mock_env:
                mock_mkdir.return_value = True
                mock_env.return_value = './static/data/data.csv'
                plugin = AzureMlTrain()
               
                response = plugin.input_as_dataframe(channel='training')
                # print(response.size)
                self.assertTrue(response.size == 15)

    def test_azureml_folder(self):
         with mock.patch('mlsriracha.plugins.azureml.train.Path.mkdir', autospec=True) as mock_mkdir:
                mock_mkdir.return_value = True
                plugin = AzureMlTrain()
               
                response = plugin.log_artifact('model.pkl')
                print(response)
                self.assertTrue(response.find('/outputs/model/model.pkl') != -1)

    # def test_gcpvertex_plugin(self):
    #     plugin = AwsSageMakerTrain()
    #     response = plugin.finish()
    #     self.assertTrue(response)