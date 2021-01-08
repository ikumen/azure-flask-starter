import logging

from backend.datastores import blob_store
from backend.models import User, Article

log = logging.getLogger(__name__)


class Service:
    """Encapsulates common SQLAlchemy specific operations to 
    implementing classes.
    """
    _model_ = None

    def init_app(self, app):
        pass

    def _before_update(self, kwargs):
        return kwargs

    def all(self):
        return self._model_.all()

    def create(self, **kwargs):
        return self._model_.create(**kwargs)

    def delete(self, id):
        return self._model_.delete(id)

    def update(self, model=None, id=None, **kwargs):
        if id is None and model is None:
            raise ValueError('Nothing to update, no model or id given')
        if model is None:
            model = self.get(id)
        for k, v in self._before_update(kwargs).items():
            setattr(model, k, v)
        return self._model_.save(model)

    def get(self, id):
        return self._model_.get(id)


class UserService(Service):
    """Encapsulates `User` model operations and any associated 
    business logic.
    """
    _model_ = User

    def delete(self, id):
        # TODO: let ORM cascade delete for us
        Article.query.filter_by(user_id=id).delete()
        super().delete(id)


class ArticleService(Service):
    """Encapsulates `Article` model operations and any associated
    business logic.
    """
    _model_ = Article

    def init_app(self, app):
        self.asset_container_name = app.config['CONTAINER_ARTICLE_ASSETS']

    def create(self, image=None, **kwargs):
        filename = None
        try:
            if image:
                filename = blob_store.upload(file=image,
                    container_name=self.asset_container_name)
            return super().create(image_filename=filename, **kwargs)
        except Exception as e:
            if filename:
                # Rolling back the blob we just uploaded
                blob_store.delete(blob_filename=filename,
                    container_name=self.asset_container_name)
            raise e

    def delete(self, id):
        article = super().delete(id)
        blob_store.delete(blob_filename=article.image_filename,
            container_name=self.asset_container_name)
        

article_service = ArticleService()
user_service = UserService()


