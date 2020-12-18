import logging
import os
import uuid

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobServiceClient, PublicAccess, BlobType, BlobProperties
from flask_sqlalchemy import SQLAlchemy

log = logging.getLogger(__name__)


class BlobStore:
    """Provides a simple interface to Azure's Blob Storage service and
    it operations on containers and blobs.
    """
    def init_app(self, app):
        self.client = BlobServiceClient(
            account_url=app.config['BLOB_STORE_URI'], 
            credential=app.config['BLOB_STORE_CREDENTIAL'])
        self._init_containers(app)

    def _init_containers(self, app):
        """Creates any missing containers needed by this application.
        """
        log.info(f"Initializing blob containers for {app.config['BLOB_STORE_URI']}")
        containers_names = [c['name'] for c in self.client.list_containers(include_metadata=True)]
        for name in app.config['BLOB_STORE_CONTAINERS']:
            if name not in containers_names:
                log.info(f"Creating container: {name}")
                self.client.create_container(name, public_access=PublicAccess.Container)        

    def upload(self, container_name, file, existing_blob=None):
        """Uploads the given to the specified container."""
        _, ext = os.path.splitext(file.filename)
        blob_filename = f"{str(uuid.uuid4())}{ext}"
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_filename)
        with file.stream as data:
            blob_client.upload_blob(data)
        return blob_filename

    def delete(self, container_name, blob_filename):
        """Deletes a blob wit the given filename in the specified container.
        """
        blob_client = self.client.get_blob_client(container=container_name, blob=blob_filename)
        blob_client.delete_blob(delete_snapshots="include")



db = SQLAlchemy()
blob_store = BlobStore()

