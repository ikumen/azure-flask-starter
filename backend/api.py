import json
import logging
import os

from flask import Blueprint, request, jsonify
from backend.services import user_service, article_service
from werkzeug.utils import secure_filename


log = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/articles', methods=['get'])
def list_articles():
    articles = [art.as_dict() for art in article_service.all()]
    return jsonify(articles)


@bp.route('/articles', methods=['post'])
def create_article():
    params = json.loads(request.form['data'])
    image = request.files['image']
    if image:
        image.filename = secure_filename(image.filename)
    article = article_service.create(image=image, **params)
    return jsonify(article.as_dict())

@bp.route('/articles/<id>', methods=['delete'])
def delete_article(id):
    article_service.delete(id)
    return {}, 204 

@bp.route('/users', methods=['get'])
def list_users():
    users = [u.as_dict() for u in user_service.all()]
    return jsonify(users)

@bp.route('/users', methods=['post'])
def create_user():
    params = request.get_json()
    user = user_service.create(**params)
    return jsonify(user.as_dict())

@bp.route('/users/<id>', methods=['delete'])
def delete_user(id):
    user_service.delete(id)
    return {}, 204