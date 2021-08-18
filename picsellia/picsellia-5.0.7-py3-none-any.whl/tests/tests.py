import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from picsellia import client, pxl_exceptions
import shutil

api_token  = "587be091f931a00868d7fd60faedaf0b42ad2525"

class TestInitCreate(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()

    def test_init_normal(self):
        clt = client.Client(api_token=self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertEqual(clt.host, self.host)
        self.assertIn('username', dir(clt))
        self.assertIn('sdk_version', dir(clt))
        self.assertIn('organization_id', dir(clt))
        self.assertIn('organization_name', dir(clt))
        self.assertIsNone(clt.project_name_list)
        self.assertIsNone(clt.project_token)
        self.assertIsNone(clt.project_id)
        self.assertIsNone(clt.project_infos)
        self.assertIsNone(clt.project_name)
        self.assertIsNone(clt.project_type)
        self.assertEqual(clt.supported_img_types, ("png", "jpg", "jpeg", "JPG", "JPEG", "PNG"))
        self.assertIsNone(clt.png_dir)
        self.assertIsNone(clt.base_dir)
        self.assertIsNone(clt.metrics_dir)
        self.assertIsNone(clt.checkpoint_dir)
        self.assertIsNone(clt.record_dir)
        self.assertIsNone(clt.config_dir)
        self.assertIsNone(clt.results_dir)
        self.assertIsNone(clt.exported_model_dir)
        self.assertIsNone(clt.experiment_id)
        self.assertIsNone(clt.exp_name)
        self.assertIsNone(clt.exp_description)
        self.assertIsNone(clt.exp_status)
        self.assertIsNone(clt.exp_parameters)
        self.assertEqual(clt.line_nb, 0)
        self.assertIsNone(clt.annotation_type)
        self.assertEqual(clt.dict_annotations, {})
        self.assertIsNone(clt.train_list_id)
        self.assertIsNone(clt.eval_list_id)
        self.assertIsNone(clt.train_list)
        self.assertIsNone(clt.eval_list)
        self.assertIsNone(clt.index_url)
        self.assertIsNone(clt.label_path)
        self.assertIsNone(clt.label_map)
        self.assertTrue(clt.interactive)
    
    def test_init_environ_token(self):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_no_environ_token(self):
        del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client(host=self.host)

    def test_init_project(self,):
        clt = client.Client.Project(self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertIsNotNone(clt.organization_name)
        self.assertIsNone(clt.name)
        self.assertIsNone(clt.project_token)
        self.assertEqual(clt.infos, {})
        self.assertEqual(clt.project_list, [])
    
    def test_init_project_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Project(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_project_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Project(host=self.host)

    def test_project(self,):
        clt = client.Client.Project(self.token, host=self.host)
        print(clt) # test __str__ methd before fetch
        project = clt.create("test_project_1")
        with self.assertRaises(pxl_exceptions.InvalidQueryError, msg="Project name can't be empty"):
            proj = clt.create()
        with self.assertRaises(pxl_exceptions.InvalidQueryError, msg="You must specify the dataset like this -> <dataset_name>/<version>"):
            proj = project.attach_dataset("test_push_dataset_test")
        self.assertEqual(project.name, "test_project_1")
        project_list = clt.list()
        project_list = [proj["project_name"] for proj in project_list]
        self.assertIn(project.name, project_list)
        project = clt.get("test_project_1")
        self.assertEqual(project.name, "test_project_1")
        resp = clt.update(description="test project description")
        self.assertEqual(resp.infos["description"], "test project description")
    

class TestDatalake(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()
    
    def test_init_datalake(self,):
        clt = client.Client.Datalake(self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertEqual(clt.fetched_pictures, [])
    
    def test_init_datalake_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Datalake(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_datalake_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Datalake(host=self.host)


class TestPictureInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()
    
    def test_init_picture(self,):
        clt = client.Client.Datalake.Picture(self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertEqual(clt.fetched_pictures, [])

    def test_init_picture_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Datalake.Picture(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_picture_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Datalake.Picture(host=self.host)

    def test_upload_pictures(self,):
        clt = client.Client.Datalake.Picture(self.token, host=self.host)
        files = os.listdir('tests/test_image_dir')
        files = ['tests/test_image_dir/'+fle for fle in files]
        clt.upload(files, ['test_test']) # test upload multiple files
        clt.upload('tests/test.png', ["test_test_single"]) # test upload single file


class TestPicture(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()

    def test_picture_list(self,):
        picture = client.Client.Datalake.Picture(self.token, host=self.host)
        picture.status() # test status with no fetched pictures
        picture.list()
        self.assertTrue(len(picture.fetched_pictures)>0)
        picture.status() # test status with fetched pictures
    
    def test_fetch_pictures(self,):
        picture = client.Client.Datalake.Picture(self.token, host=self.host)
        print(picture) # test __str__ method before fetch
        picture.fetch(1, ["certainly not a tag"])
        picture.delete() # no fetched pictures
        picture.add_tags() # no fetched pictures 
        picture.remove_tags() # no fetched pictures and no tags
        picture.fetch(6, ["test_test"])
        print(picture) # test __str__ method after fetch
        picture.add_tags() # no tags
        picture.remove_tags() # no tags
        picture.add_tags(tags=["test_test_tag"])
        picture.remove_tags(tags=["test_test_tag"])


class TestDatasetInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()
    
    def test_init_dataset(self,):
        clt = client.Client.Datalake.Dataset(self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertEqual(clt.fetched_dataset, {})
        self.assertIsNone(clt.dataset_id)

    def test_init_dataset_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Datalake.Dataset(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_dataset_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Datalake.Dataset(host=self.host)
        
    def test_create_dataset(self,):
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        picture = client.Client.Datalake.Picture(self.token, host=self.host)
        picture.fetch(6, ["test_test"])
        dataset.create(name="test_dataset_test") # test with no pictures
        dataset.create(name="test_dataset_test", pictures=picture.fetched_pictures) # test with pictures



class TestDataset(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()
    
    def test_list_dataset(self,):
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        dataset.list()
    
    def test_fetch_dataset(self,):
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        print(dataset) # test __str__ method before fetch
        dataset.fetch() # test no name
        dataset = dataset.fetch("test_dataset_test")
        self.assertEqual(dataset.fetched_dataset["dataset_name"], "test_dataset_test")
    
    def test_new_version_add_data_labels_and_delete(self,):
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        dataset.new_version(name="test_dataset_test", version="2")
        picture = client.Client.Datalake.Picture(self.token, host=self.host)
        picture.fetch(1, ["test_test_single"])
        dataset.add_data("test_dataset_test", "2")  # test no pictures
        dataset.add_data("test_dataset_test", "2", picture.fetched_pictures)
        dataset.create_labels("car", 'polygon')
        dataset.delete("test_dataset_test", "2")
    
    def test_push_dataset(self,):
        datalake = client.Client.Datalake(self.token, host=self.host)
        with self.assertRaises(pxl_exceptions.InvalidQueryError):
            datalake.upload("test_dataset_test_3", ann_path="tests/not_a_file.json", imgdir="tests/test_push_dataset_dir", ann_format="PICSELLIA") # test no json
        datalake.upload("test_dataset_test_3", ann_path="tests/test_annotations.json", imgdir="tests/test_push_dataset_dir", tags=["test_push"], ann_format="PICSELLIA") # test normal
        picture = client.Client.Datalake.Picture(self.token, host=self.host)
        picture.fetch(2, ["test_push"])
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        dataset.create(name="test_push_dataset_test", pictures=picture.fetched_pictures)
        datalake.upload(name="test_push_dataset_test", ann_path="tests/test_annotations.json", ann_format="PICSELLIA") # test annotation only
        with self.assertRaises(pxl_exceptions.InvalidQueryError):
            datalake.upload(name="test_dataset_test_3", ann_path="tests/not_a_file.json") # test no json
        with self.assertRaises(pxl_exceptions.ResourceNotFoundError):
            datalake.upload(name="test_dataset_test_3", ann_path="tests/test_annotations_wrong.json", imgdir="", ann_format="PICSELLIA") # missing images 'key' in json


    def test_download_dataset(self,):
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        dataset.download("test_dataset_test/first")
        shutil.rmtree("test_dataset_test")
        os.mkdir("test_dataset_test")
        dataset.download("test_dataset_test/first")
        shutil.rmtree("test_dataset_test")
        dataset.download("test_dataset_test/first", "tests/test_dl_dataset")
        shutil.rmtree("tests/test_dl_dataset")
    
    def test_labels_and_annotation(self,):
        dataset = client.Client.Datalake.Dataset(self.token, host=self.host)
        with self.assertRaises(Exception):
            dataset.create_labels() # test invalidqueryerror
        with self.assertRaises(pxl_exceptions.InvalidQueryError):
            dataset.delete_annotations() # test invalidqueryerror
        dataset.fetch("test_dataset_test", "first")
        dataset.create_labels("car", 'rectangle')
        dataset.create_labels("bird", 'rectangle')

class TestExperimentCrud(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()

    def test_init_experiment(self,):
        clt = client.Client.Experiment(self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertEqual(clt.experiment_name, "")
        self.assertTrue(clt.interactive)
        self.assertEqual(clt.project_token, None)
        self.assertEqual(clt.base_dir, "")
        self.assertEqual(clt.png_dir, 'images')
        self.assertEqual(clt.line_nb, 0)
        self.assertEqual(clt.buffer_length, 1)
        self.assertIsNone(clt.run)
    
    def test_init_experiment_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Experiment(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test__init_experiment_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Experiment(host=self.host)

    def test_init_experiment_with_name(self,):
        clt = client.Client.Experiment(self.token, host=self.host, name="exp_1")
        self.assertEqual(clt.experiment_name, 'exp_1')
        clt = client.Client.Experiment(self.token, host=self.host, name="exp_1")
    
    def test_experiment(self,):
        project = client.Client.Project(self.token, host=self.host)
        project = project.get("test_project_1")
        experiment = client.Client.Experiment(self.token, self.host, project.project_token)
        print(experiment) # test __str__ method before fetch
        experiment = experiment.create("test_experiment_1")
        print(experiment) # test __str__ method after fetch
        self.assertEqual(experiment.experiment_name, "test_experiment_1")
        experiment_list = experiment.list()
        experiment_list = [exp["name"] for exp in experiment_list]
        self.assertIn("test_experiment_1", experiment_list)
        experiment.id = None
        experiment = experiment.checkout(name="test_experiment_1") # Test checkout with name
        experiment_id = experiment.id
        self.assertEqual(experiment.experiment_name, 'test_experiment_1')
        resp = experiment.update(description="test description")
        self.assertEqual(resp["description"], "test description")
        experiment.id = None
        experiment = experiment.checkout(id=experiment_id) # Test checkout with id
        project_token = project.project_token
        experiment.project_token = None
        experiment_list = experiment.list(project_token) # Test list with specified project token
        experiment.project_token = project_token
        experiment = experiment.checkout(id=experiment_id) # Test _get with uuid
        experiment.delete()
        experiment = experiment.create("test_experiment_1")
        experiment.delete_all()
        experiment = experiment.create("test_experiment_1")
        


class TestExperiment(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        project = client.Client.Project(cls.token, host=cls.host)
        project = project.get("test_project_1")
        cls.project_token = project.project_token
        project.attach_dataset("test_push_dataset_test/first")
        return super().setUpClass()

    def test_logging(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.checkout(name="test_experiment_1")
        experiment.start_logging_chapter("chapter 1")
        experiment.start_logging_buffer(5)
        experiment.end_logging_buffer()
        experiment.send_experiment_logging("chapter 1", "chapter 1")

    def test_update_job_status(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.checkout(name="test_experiment_1")
        experiment.update_job_status("success")

    def test_publish(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.checkout(name="test_experiment_1")
        experiment.publish("test_model_1")
        network = client.Client.Network(self.token, host=self.host)
        network = network.get("test_model_1")
        network.delete()
    
    def test_store_with_path_and_download(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.checkout(name="test_experiment_1")
        experiment.store("small_file", "tests/test_dir", True)
        experiment.store("large_file", "tests/lg_test_file.pb")
        os.remove("tests/test_dir.zip")
        experiment.download("small_file", "tests/dl_test_dir")
        self.assertTrue(os.path.isfile("tests/dl_test_dir/test_dir.zip"))
        os.remove("tests/dl_test_dir/test_dir.zip")
        experiment.download("large_file", "tests/dl_test_dir")
        self.assertTrue(os.path.isfile("tests/dl_test_dir/lg_test_file.pb"))
        os.remove("tests/dl_test_dir/lg_test_file.pb")
        experiment.store("small_file", "tests/sm_test_file.config") # test update file
        experiment.download("not_a_file")
        files = experiment.list_files()
        files = [fle["name"] for fle in files]
        self.assertIn("small_file", files)
        self.assertIn("large_file", files)
        experiment.checkout("test_experiment_1", with_file=True)
        shutil.rmtree("test_experiment_1")
        experiment.checkout("test_experiment_1", with_file=True, tree=True)
        shutil.rmtree("test_experiment_1")
        experiment.delete_file("small_file")
        experiment.delete_all_files()
    
    def test_checkout_experiment(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.checkout(name="test_experiment_1")
        experiment_id = experiment.id
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment.checkout(id=experiment_id) # test id not none
        experiment = client.Client.Experiment(self.token, self.host)
        experiment.checkout(name="test_experiment_1", project_token=self.project_token) # test project_token not none and name
        experiment = client.Client.Experiment(self.token, self.host)
        experiment.experiment_name = "test_experiment_1"
        experiment.checkout(project_token=self.project_token) # test project_token not none and experiment name
        experiment = client.Client.Experiment(self.token, self.host)
        with self.assertRaises(Exception):
            experiment.checkout() # test identifier none

    def test_log(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.checkout(name="test_experiment_1")
        experiment.log("value", 25, 'value')  # test log single value
        experiment.log("image", 'tests/test.png', 'image') # test log image
        experiment.log("line", [1, 2, 3, 4], "line") # test log line
        experiment.log("value", 26, "value", True) # test log replace value
        experiment.log("value", 26, "value") # test log update no replace value
        experiment.log("line", [5, 6, 7], "line") # test log append lines
        data_list = experiment.list_data()
        data_list = [dt["name"] for dt in data_list]
        self.assertIn("value", data_list)
        self.assertIn("line", data_list)
        self.assertIn("image", data_list)
        experiment.delete_data("value")
        experiment.delete_all_data()

    def test_dl_annotations_pic_train_test_split(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        experiment = experiment.create(name="test_experiment_2", dataset="test_push_dataset_test/first")
        experiment.dl_annotations()
        print(experiment.dict_annotations)
        experiment.png_dir = "tests/png_dir"
        experiment.dl_pictures()
        experiment.generate_labelmap()
        experiment.train_test_split()
        experiment = experiment.checkout("test_experiment_1")
        experiment.dict_annotations = {}
        experiment.base_dir = ""
        with self.assertRaises(pxl_exceptions.ResourceNotFoundError):
            experiment.generate_labelmap()# test no 'images' key in dict annotations
        with self.assertRaises(pxl_exceptions.ResourceNotFoundError):
            experiment.dl_pictures() # test no 'images' key in dict annotations
        with self.assertRaises(pxl_exceptions.ResourceNotFoundError):
            experiment.train_test_split()# test no 'images' key in dict annotations
        shutil.rmtree("tests/png_dir")
        os.remove("label_map.pbtxt")

    def test_init_scan(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'script': 'tests/__init__.py',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'data': ['tests/test.png'],
            'requirements': [
                {
                    'package': 'numpy',
                    'version': '0.0.1'
                }
            ]
        }
        resp = experiment.init_scan("test_scan", config)
        self.assertIn("success", resp)
        config["script"] = "tests/not_a_file.txt"
        with self.assertRaises(FileNotFoundError):
            experiment.init_scan("test_scan_no_file", config)

    def test_init_scan_large_script(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'script': 'tests/lg_test_file.pb',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
        }
        resp = experiment.init_scan("test_scan_large", config)
        self.assertIn("success", resp)

    def test_init_scan_2(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'requirements': 'tests/test_req.txt'
        }
        resp = experiment.init_scan("test_scan_2", config)
        self.assertIn("success", resp)

    def test_init_scan_error(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'requirements': {
                'package': 'numpy',
                'version': '0.0.1'
            }
        }
        with self.assertRaises(pxl_exceptions.InvalidQueryError):
            experiment.init_scan("test_scan_3", config)

    def test_init_scan_and_test_runs(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'image': 'picsellpn/simple-run:1.0',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
        }
        resp = experiment.init_scan("test_scan_run_1", config)
        self.assertIn("success", resp)
        run = experiment.get_next_run("test_scan_run_1")
        self.assertEqual(run["experiment"]["name"], "test_scan_run_1-0")
        run = experiment.get_run(run["id"])
        resp = experiment.update_run(status="success")
        self.assertEqual(resp["status"], 'success')
        self.assertTrue(experiment.end_run())

    def test_run_download_data_script_and_req(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'script': 'tests/__init__.py',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'data': ['tests/test.png'],
            'requirements': [
                {
                    'package': 'requests',
                    'version': '2.23.0'
                }
            ]
        }
        resp = experiment.init_scan("test_scan_run_2", config)
        self.assertIn("success", resp)
        experiment.get_next_run("test_scan_run_2")
        experiment.download_script()
        experiment.download_run_data()
        experiment.install_run_requirements() 
    
    def test_generate_requirements(self,):
        experiment = client.Client.Experiment(self.token, self.host, self.project_token)
        config = {
            'script': 'tests/__init__.py',
            'execution': {
                'type': 'agents'
            },
            'strategy': 'grid',
            'metric': {
                'name': 'Loss-total_loss',
                'goal': 'minimize'
            },
            'parameters': {
                'batch_size': {
                    'values': [2, 4, 8],
                },
            },
            'requirements': "tests/wrong_test_req.txt"
        }
        with self.assertRaises(pxl_exceptions.ResourceNotFoundError):
            resp = experiment.init_scan("test_scan_run_3", config) # wrong requirements path
        config["requirements"] = "tests/bad_test_req.txt"
        config["requirements"] = "tests/test_req.txt"
        resp = experiment.init_scan("test_scan_run_3", config) 



class TestNetworkInit(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()
    
    def test_init_network(self,):
        clt = client.Client.Network(self.token, host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
        self.assertIsNone(clt.network_id)
        self.assertEqual(clt.network_name, "")
    
    def test_init_network_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Network(host=self.host)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_network_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Network(host=self.host)

    def test_create_network_and_get_uuid(self,):
        network = client.Client.Network(self.token, host=self.host)
        with self.assertRaises(pxl_exceptions.InvalidQueryError, msg="You must specify a non-empty type for your network"):
            net = network.create("test_network_test")
        network = network.create("test_network_test", "detection")
        network_id = network.network_id
        network = network.get()
        network.network_id = None
        network = network.get(network_id)
        network = network.get(network.network_name)
        network = network.update(tag=["test_tag"])

class TestNetwork(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()

    def test_list_network(self,):
        network = client.Client.Network(self.token, host=self.host)
        network_list = network.list()
        network_list = [net["network_name"] for net in network_list]
        self.assertIn("test_network_test", network_list)

    def test_network_store(self,):
        network = client.Client.Network(self.token, host=self.host)
        print(network) # test __str__ method before fetch
        network = network.get("test_network_test")
        network.store('config ')  # test path is None
        network.store('config', 'tests/sm_test_file.config')
        network.store('config', 'tests/sm_test_file.config') # test file already stored
        network.store('model-latest', 'tests/test_dir', True)
        network.store('large_file', 'tests/lg_test_file.pb')
    
    def test_update_thumb(self,):
        network = client.Client.Network(self.token, host=self.host)
        network = network.get("test_network_test")
        network.update_thumb('tests/test.png')
    
    def test_network_labels(self,):
        network = client.Client.Network(self.token, host=self.host)
        network = network.get("test_network_test")
        labels = {
            '0': 'car',
            '1': 'bird'
        }
        network.labels(labels)


class TestWorker(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        project = client.Client.Project(cls.token, host=cls.host)
        project = project.get("test_project_1")
        cls.project_token = project.project_token
        return super().setUpClass()

    def test_init_worker(self,):
        clt = client.Client.Project.Worker(self.token, self.host, self.project_token)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_worker_no_project_token(self,):
        with self.assertRaises(Exception):
            clt = client.Client.Project.Worker(self.token, self.host)
    
    def test_init_worker_environ_token(self,):
        os.environ["PICSELLIA_TOKEN"] = self.token
        clt = client.Client.Project.Worker(host=self.host, project_token=self.project_token)
        self.assertEqual(clt.auth, {"Authorization": "Token " + self.token})
    
    def test_init_worker_no_environ_token(self,):
        if "PICSELLIA_TOKEN" in os.environ:
            del os.environ["PICSELLIA_TOKEN"]
        with self.assertRaises(Exception, msg="Please set up the PICSELLIA_TOKEN environement variable or specify your token"):
            client.Client.Project.Worker(host=self.host, project_token=self.project_token)

    def test_list_worker(self,):
        worker = client.Client.Project.Worker(self.token, self.host, self.project_token)
        worker_list = worker.list()
        self.assertTrue(len(worker_list["workers"])>0)


class TestDelete(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.host = "http://127.0.0.1:8000/sdk/v2/"
        cls.token = api_token
        return super().setUpClass()
    
    def test_delete_project(self,):
        clt = client.Client.Project(self.token, host=self.host)
        project = clt.get("test_project_1")
        resp = clt.delete()
        picture = client.Client.Datalake.Picture(self.token, host=self.host)
        picture.fetch(6, ["test_test"])
        picture.delete()
        picture.fetch(1, ["test_test_single"])
        picture.delete()
        picture.fetch(1, ["test_push"])
        picture.delete()
        network = client.Client.Network(self.token, host=self.host)
        network = network.get("test_network_test")
        network.delete()

if __name__ == '__main__':
    unittest.main()