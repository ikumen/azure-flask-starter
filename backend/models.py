from datetime import datetime
from backend.datastores import db

class ModelMixin:
    @classmethod
    def _process_params(cls, kwargs):
        return kwargs
        
    @classmethod
    def save(cls, model):
        db.session.add(model)
        db.session.commit()
        return model

    @classmethod
    def create(cls, **kwargs):
        model = cls(**cls._process_params(kwargs))
        return cls.save(model)

    @classmethod
    def all(cls):
        return [model for model in cls.query.all()]

    @classmethod
    def delete(cls, id):
        model = cls.query.get(id)
        db.session.delete(model)
        db.session.commit()
        return model

    @classmethod
    def get(cls, id):
        return cls.query.get(id)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class User(ModelMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)

    @classmethod
    def delete(cls, id):
        # TODO: let ORM cascade delete for us
        Article.query.filter_by(user_id=id).delete()
        super().delete(id)


class Article(db.Model, ModelMixin):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    image_filename = db.Column(db.String(42))
    content = db.Column(db.String(None))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.ForeignKey('users.id'))


