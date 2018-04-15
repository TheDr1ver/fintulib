"""This module contains helpers to upload / download files and python objects to
Google Cloud Platform.

Python objects are serialized with pickle.

Note that Python objects need to fit in memory if uploaded directly. Otherwise,
a temporary local file is required.
"""

from typing import Any, Tuple
import io
import pickle
from google.cloud import storage
from urllib.parse import urlparse


def _parse_gcs_path(gcs_path: str) -> Tuple[str, str]:
    parsed_path = urlparse(gcs_path)
    if not parsed_path.scheme == "gs":
        raise NameError(
            "gcs_path must be a valid Google Cloud Storage Path (begins with gs://)")
    bucket_name = parsed_path.netloc
    object_name = parsed_path.path[1:]
    return bucket_name, object_name


def gcs_upload_object(python_object: Any, gcs_path: str, overwrite: bool = False, verbose: bool = True) -> None:
    """Upload a Python object to Google Cloud Storage (using pickle to serialize the object).

    Arguments:
    python_object: The Python object to upload (e.g. a Pandas DataFrame)
    gcs_path: The Google Cloud Storage path. Must start with 'gs://'
    overwrite: Set this to 'True' if you want to overwrite existing objects on GCS
    verbose: Set this to 'False' if you don't want this function to report success. Default is 'True'
    """
    bucket_name, object_name = _parse_gcs_path(gcs_path)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    if blob.exists() and not overwrite:
        raise FileExistsError(
            f"File gs://{bucket_name}/{object_name} already exists. Specify 'overwrite=True' if you want to overwrite.")
    pickle_bytes = pickle.dumps(python_object, pickle.HIGHEST_PROTOCOL)
    stream = io.BytesIO(pickle_bytes)
    blob.upload_from_file(stream)
    stream.close()
    if verbose:
        print(
            f"Successfully uploaded object to gs://{bucket_name}/{object_name}")
    return


def gcs_download_object(gcs_path: str, verbose: bool = True) -> Any:
    """Download a serialized Python object from Google Cloud Storage (using pickle to deserialize the object).

    Arguments:
    gcs_path: The Google Cloud Storage path. Must start with 'gs://'
    verbose: Set this to 'False' if you don't want this function to report success. Default is 'True'

    Returns:
    A Python object
    """
    bucket_name, object_name = _parse_gcs_path(gcs_path)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    if not blob.exists():
        raise FileNotFoundError(
            f"The file gs://{bucket_name}/{object_name} doesn't exist")
    downstream = io.BytesIO()
    blob.download_to_file(downstream)
    downstream.seek(0)
    down = downstream.read()
    if verbose:
        print(
            f"Successfully downloaded object from gs://{bucket_name}/{object_name}")
    return pickle.loads(down)


def gcs_upload_file(file_name: str, gcs_path: str, overwrite: bool = False, verbose: bool=True) -> None:
    """Upload a local file to Google Cloud Storage.

    Arguments:
    file_name: The local file name of the file to be uploaded
    gcs_path: The Google Cloud Storage path. Must start with 'gs://'
    overwrite: Set this to 'True' if you want to overwrite existing objects on GCS
    verbose: Set this to 'False' if you don't want this function to report success. Default is 'True'
    """
    bucket_name, object_name = _parse_gcs_path(gcs_path)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    if blob.exists() and not overwrite:
        raise FileExistsError(
            f"File gs://{bucket_name}/{object_name} already exists. Specify 'overwrite=True' if you want to overwrite.")
    f = open(file_name, mode="rb")
    blob.upload_from_file(f,)
    if verbose:
        print(f"Successfully uploaded file to gs://{bucket_name}/{object_name}")
    return


def gcs_download_file(gcs_path: str, file_name: str, verbose: bool=True) -> None:
    """Download a file from Google Cloud Storage.

    Arguments:
    gcs_path: The Google Cloud Storage path. Must start with 'gs://'
    file_name: The local file name where the downloaded file will be stored
    verbose: Set this to 'False' if you don't want this function to report success. Default is 'True'
    """
    bucket_name, object_name = _parse_gcs_path(gcs_path)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    if not blob.exists():
        raise FileNotFoundError(
            f"The file gs://{bucket_name}/{object_name} doesn't exist")
    f = open(file_name, mode="wb")
    blob.download_to_file(f)
    if verbose:
        print(
            f"Successfully downloaded file from gs://{bucket_name}/{object_name}")
    return
