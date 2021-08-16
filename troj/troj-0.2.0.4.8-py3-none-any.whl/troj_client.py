import requests
from typing import Optional, Dict, List
from .utils import (
    assert_valid_name,
    raise_resp_exception_error,
    requests_retry,
    _upload_local_files,
    _upload_local_zip,
)
import json


class TrojClient:
    def __init__(
        self,
        *,
        api_endpoint: str = "https://wct55o2t7c.execute-api.ca-central-1.amazonaws.com/prod/api/v1",
        # api_endpoint: str = "http://localhost:8080/api/v1",
        # api_endpoint: str = "https://wuw1nar7mf.execute-api.ca-central-1.amazonaws.com/dev/api/v1",
        **kwargs,
    ) -> "Client":
        # self._creds_id_token = None
        self._creds_refresh_token = None
        self._creds_api_key = None
        self.api_endpoint = api_endpoint
        # self.cognito_client_id = "46ca3qqhhkos18k3hjqn10b4uc"
        self.cognito_client_id = "643hgaovbhf36dol8ihpfr6513"
        requests_retry.hooks["response"].append(
            self.reauth
        )  # https://github.com/psf/requests/issues/4747 - Important for Retry vs urllib3

    def _get_creds_headers(self):
        """
        Get appropriate request headers for the currently set credentials.

        Raises:
            Exception: No credentials set.
        """
        if self._creds_id_token:
            return {
                "Authorization": f"Bearer {self._creds_id_token}",
                "x-api-key": f"{self._creds_api_key}",
            }
        else:
            raise Exception("No credentials set.")

    def set_credentials(
        self,
        *,
        id_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Set credentials for the client.

        Args:
            id_token (str, optional): Used by the client to authenticate the user. Defaults to None.
            refresh_token (str, optional): Used to refresh the ID Token. Defaults to None.
            api_key (str, optional): Used to gain access to API
        Raises:
            Exception: Invalid credential combination provided.
        """

        # TODO: Change to require id_token and api_key together
        if id_token is not None:
            self._creds_id_token = id_token
        else:
            raise Exception("Please provide an ID Token.")
        if refresh_token is not None:
            self._creds_refresh_token = refresh_token
        else:
            raise Exception("Please provide a Refresh Token.")
        if api_key is not None:
            self._creds_api_key = api_key
        else:
            raise Exception("Please provide an API Key.")

    def test_api_endpoint(self):
        try:
            r = requests_retry.get(
                "https://wuw1nar7mf.execute-api.ca-central-1.amazonaws.com/dev/ping"
            )
            return r.status_code
        except Exception as exc:
            raise Exception(f"test_api_endpoint error: {exc}")

    def create_project(self, project_name: str):
        """
        Create a new project via the REST API.

        Args:
            project_name (str): Name you want to give your project
        """

        assert_valid_name(project_name)

        data = {"project_name": project_name}

        r = requests_retry.post(
            f"{self.api_endpoint}/projects",
            headers=self._get_creds_headers(),
            json=data,
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def get_projects(self):
        """
        Get data about the users projects
        """

        r = requests_retry.get(
            f"{self.api_endpoint}/projects",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def project_exists(self, project_name: str):
        """
        Check if a project exists.

        Args:
            project_name (str): Project name

        Returns:
            Dict[int, dict]: dict(data) will either be False or the project itself
        """

        r = requests_retry.get(
            f"{self.api_endpoint}/projects/{project_name}",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def delete_project(self, project_name: str):
        """
        Try to delete a project

        Args:
            project_name (str): Name of the project to be deleted
        """

        if self.project_exists(project_name)["data"] is False:
            raise Exception(f"Project '{project_name}' does not exist.")

        r = requests_retry.delete(
            f"{self.api_endpoint}/projects/{project_name}",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def create_dataset(self, project_name: str, dataset_name: str):
        # TODO: Add task choice when creating dataset
        assert_valid_name(dataset_name)
        project_data = self.project_exists(project_name)

        data = {
            "project_uuid": project_data["data"]["project_uuid"],
            "dataset_name": dataset_name,
        }

        r = requests_retry.post(
            f"{self.api_endpoint}/datasets",
            headers=self._get_creds_headers(),
            json=data,
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}
        # End of create_dataset()

    def get_project_datasets(self, project_name: str):
        """
        Get info about existing datasets for a specific project

        Args:
            project_name (str): Name of the project you want to find datasets under
        """

        r = requests_retry.get(
            f"{self.api_endpoint}/projects/{project_name}/datasets",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def dataset_exists(self, project_name: str, dataset_name: str):
        """
        Check if a dataset exists.

        Args:
            project_name (str): Project name
            dataset_name (str): Dataset name

        Returns:
            Dict[int, dict]: dict(data) will either be False or the dataset itself
        """
        if self.project_exists(project_name)["data"] is False:
            raise Exception(f"Project '{project_name}' does not exist.")

        r = requests_retry.get(
            f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def delete_dataset(self, project_name: str, dataset_name: str):
        if self.dataset_exists(project_name, dataset_name)["data"] is False:
            raise Exception(
                f"Dataset '{dataset_name}' does not exist in project '{project_name}'."
            )

        r = requests_retry.delete(
            f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}",
            headers=self._get_creds_headers(),
        )

        raise_resp_exception_error(r)
        return {"status_code": r.status_code, "data": r.json()}

    def upload_dataset_files(
        self, image_filepaths: List, project_name: str, dataset_name: str
    ):
        download_urls = []
        get_upload_path = f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}/fetch_upload_dataset_url"

        download_urls = _upload_local_files(
            image_filepaths,
            get_upload_path,
            self._get_creds_headers(),
            "",  # suffix
            "",  # prefix
            delete_after_upload=False,
        )

        return download_urls

    def upload_dataset_files_zipped(
        self, zip_filepath: str, project_name: str, dataset_name: str
    ):
        download_urls = []
        get_upload_path = f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}/fetch_upload_dataset_url_zip"
        complete_upload_path = f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}/fetch_upload_dataset_url_zip/complete"
        download_urls = _upload_local_zip(
            zip_filepath,
            get_upload_path,
            complete_upload_path,
            self._get_creds_headers(),
            "",  # suffix
            "",  # prefix
            delete_after_upload=False,
        )

        return download_urls

    def upload_df_results(self, project_name: str, dataset_name: str, dataframe: dict):
        """
        Uploads dataframe results to database.

        Args:
            project_name (str): Project name
            dataset_name (str): Dataset name
            dataframe (dict): JSONified dataframe

        Returns:
            Dict[int, bool]: status_code and bool whether success/fail to upload
        """
        try:
            dataset = self.dataset_exists(project_name, dataset_name)["data"]

            if dataset is not False:
                r = requests_retry.post(
                    f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}/fetch_upload_dataframe_url",
                    headers=self._get_creds_headers(),
                )

                raise_resp_exception_error(r)

                s3_payload_dict = r.json()

                file_to_save = json.dumps(dataframe).encode("utf-8")
                file_name_on_s3 = s3_payload_dict["fields"]["key"]

                files = {"file": (file_name_on_s3, file_to_save)}
                upload_response = requests.post(
                    s3_payload_dict["url"], data=s3_payload_dict["fields"], files=files
                )

                print(f"Upload response: {upload_response.status_code}")

                return {"status_code": upload_response.status_code}
            else:
                raise Exception(
                    "Something went wrong. Double check the project and dataset names."
                )
        except Exception as exc:
            raise Exception(f"post_dataframe error: {exc}")

    def refresh_tokens(self):

        url = "https://troj.auth.ca-central-1.amazoncognito.com/oauth2/token"

        payload = f"grant_type=refresh_token&client_id={self.cognito_client_id}&refresh_token={self._creds_refresh_token}"
        requests.utils.quote(payload)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print("res:", response.json())
        self._creds_id_token = json.loads(response.text)["id_token"]

        return response

    def reauth(self, res, *args, **kwargs):
        """Hook to re-authenticate whenever authentication expires."""
        if res.status_code == requests.codes.forbidden:
            if res.request.headers.get("REATTEMPT"):
                res.raise_for_status()
            self.refresh_tokens()
            req = res.request
            req.headers["REATTEMPT"] = 1
            req = self.auth_inside_hook(req)
            res = requests_retry.send(req)
            return res

    def auth_inside_hook(self, req):
        """Set the authentication token for the premade request during reauth attempts inside the retry hook."""
        req.headers["Authorization"] = f"Bearer {self._creds_id_token}"
        return req

    def train_model(
        self,
        project_name: str,
        dataset_name: str = "Bark-Imagenet-Format",
        username: Optional[str] = "fake_user",
        dset_prefix: Optional[str] = None,
        user_model_prefix: Optional[str] = "None",
        architecture_name: Optional[str] = "resnet18",
        pretrained: Optional[bool] = True,
        num_classes: Optional[int] = 1000,
        global_pool: Optional[str] = None,
        finetune: Optional[bool] = True,
        resume_from_checkpoint: Optional[bool] = False,
        load_previous_model: Optional[str] = None,
        s3_bucket: Optional[str] = "fake-deploy-bucket",
        optimizer: Optional[str] = "Adam",
        learning_rate: Optional[float] = 0.001,
        momentum: Optional[float] = 0.9,
        dampening: Optional[float] = 0,
        weight_decay: Optional[float] = 5e-4,
        nesterov: Optional[bool] = False,
        betas: Optional[tuple] = (0.9, 0.999),
        adam_eps: Optional[float] = 1e-08,
        amsgrad: Optional[bool] = False,
        lr_scheduler: Optional[str] = "cosine",
        T_0: Optional[int] = 10,
        T_mult: Optional[int] = 1,
        eta_min: Optional[float] = 0,
        factor: Optional[float] = 0.1,
        patience: Optional[int] = 10,
        threshold: Optional[float] = 0.0001,
        cooldown: Optional[int] = 0,
        min_lr: Optional[float] = 0,
        normalization_stats: Optional[str] = None,
        batch_size: Optional[int] = 64,
        model_name: Optional[str] = None,
        early_stop_patience: Optional[int] = 7,
        num_epochs: Optional[int] = 50,
        log_interval: Optional[int] = 100,
        use_workers: Optional[bool] = False,
        log_wandb: Optional[bool] = True,
        wandb_key: Optional[str] = "3e0dfb6b5f7f5d658accfb7026551d1339b671e2",
    ):
        """
        Transfer learns a model? Or something of the sort..

        Args:
            project_name (str): Project name
            dataset_name (str): Dataset name
            username, default='fake_user', help='Username for folder.')
            (dataset_name)dset_name, default='Bark-Imagenet-Format', help='User dataset.')
            dset_prefix, default=None, help='Dataset prefix in S3. Set to None to use internal testing datasets')
            user_model_prefix, default=None, help='Folder for loading and saving model data in S3.')
            architecture_name, default='resnet18', help="Name of the input model architecture", type=str)
            pretrained, default=True, help='Whether or not to use pretrained weights for model', type=bool)
            num_classes, default=1000, type=int, help='Number of classes for the model')
            global_pool, default=None, metavar='POOL', help='Global pool type, one of (fast, avg, max, avgmax, avgmaxc). Model default if None.')
            finetune, default=True, type=bool, help='whether or not to only train a new output layer')
            resume_from_checkpoint, default=False, help='If true, the loaded model file in the laod previous model is expected to containing an optimizer and epoch as well as the state dict.')
            load_previous_model, default=None, help='If to load a model state dict (not from a checkpoint), set to model weights path.')
            s3_bucket, default='fake-deploy-bucket', help='s3 bucket to load and save data to. If None, paths are expected to be local.')
            optimizer, default='Adam', type=str, help='Optimizer to use')
            learning_rate, default=0.001, type=float, help='Initial Learning Rate')
            momentum, default=0.9, type=float, help='Momentum for SGD')
            dampening, default=0, type=float, help='Dampening for SGD')
            weight_decay, default=5e-4, type=float, help='Weight Decay for SGD')
            nesterov, default=False, type=bool, help='Whether or not to use Nesterov momentum for SGD')
            betas, default=(0.9, 0.999), type=tuple, help='Beta values for Adam/AdamW')
            adam_eps, default=1e-08, type=float, help='epsilon values for Adam/AdamW')
            amsgrad, default=False, type=bool, help='Whether or not to use AMSgrad when using Adam/AdamW')
            lr_scheduler, default='cosine', help='Learning rate scheduler. Options are None, plateu, cosine, and one_cycle')
            T_0, default=10, type=int, help='Number of iterations for original cosine annealing schedule')
            T_mult, default=1, type=int, help='')
            eta_min, default=0, type=float,)
            factor, default=0.1, type=float, help='Plateu decay factor')
            patience, default=10, type=int, help='Plateu decay patience')
            threshold, default=0.0001, type=float, help=' Threshold for measuring the new optimum')
            cooldown, default=0, type=int, help='Number of epochs to wait before resuming normal operation after lr has been reduced.')
            min_lr, default=0, type=float, help='Minimum LR allowed from plateu decay')
            normalization_stats, default=None, help='If model is not pretrained, stats to use for normalization. Either None, a pickle of two lists, or -1. If -1, we compute them. If using pretrained model, we use the default normalization.')
            batch_size, default=64, type=int, help='Size of training batches')
            model_name, default=None, help='The name to save the model as. If None, name is autogenerated')
            early_stop_patience, default=7, type=int, help='How many epochs before stopping when loss no longer decreases')
            num_epochs, default=50, type=int, help='Number of training epochs')
            log_interval, default=100, type=int, help='Number of batches between data logs')
            use_workers, default=False, type=bool, help='Whether or not to use multiple workers. On Windows, must be false.')
            log_wandb, default=True, type=bool, help='Logging for testing purposes')
            wandb_key, default='3e0dfb6b5f7f5d658accfb7026551d1339b671e2', help='wandb key for logging.')
        Returns:
            Status code and response of batch submit_job
        """

        # dataset = self.dataset_exists(project_name, dataset_name)["data"]
        dataset = True

        if dataset is not False:
            data = {
                "project_name": project_name,
                "dataset_name": dataset_name,
                "username": username,
                "dset_prefix": dset_prefix,
                "user_model_prefix": user_model_prefix,
                "architecture_name": architecture_name,
                "pretrained": pretrained,
                "num_classes": num_classes,
                "global_pool": global_pool,
                "finetune": finetune,
                "resume_from_checkpoint": resume_from_checkpoint,
                "load_previous_model": load_previous_model,
                "s3_bucket": s3_bucket,
                "optimizer": optimizer,
                "learning_rate": learning_rate,
                "momentum": momentum,
                "dampening": dampening,
                "weight_decay": weight_decay,
                "nesterov": nesterov,
                "betas": betas,
                "adam_eps": adam_eps,
                "amsgrad": amsgrad,
                "lr_scheduler": lr_scheduler,
                "t_0": T_0,
                "t_mult": T_mult,
                "eta_min": eta_min,
                "factor": factor,
                "patience": patience,
                "threshold": threshold,
                "cooldown": cooldown,
                "min_lr": min_lr,
                "normalization_stats": normalization_stats,
                "batch_size": batch_size,
                "model_name": model_name,
                "early_stop_patience": early_stop_patience,
                "num_epochs": num_epochs,
                "log_interval": log_interval,
                "use_workers": use_workers,
                "log_wandb": log_wandb,
                "wandb_key": wandb_key,
            }

            r = requests_retry.post(
                f"{self.api_endpoint}/projects/{project_name}/datasets/{dataset_name}/train",
                headers=self._get_creds_headers(),
                params=data,
            )

            raise_resp_exception_error(r)
            return {"status_code": r.status_code, "data": r.json()}
        else:
            raise Exception(
                "Something went wrong. Double check the project and dataset names."
            )
