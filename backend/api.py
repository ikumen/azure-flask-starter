import inspect
import logging

from functools import wraps
from flask import Blueprint, request, jsonify
from backend.services import user_service, article_service
from werkzeug.utils import secure_filename


log = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api')

def parse_params(required_params):
    """Depending on the content_type, try to extract the params. We take 
    application/json or multipart (when doing upload).
    
    Note we could strictly use application/json but upload file payload 
    will ~30% bigger due to base64 encoding."""
    params = (request.form if request.content_type.startswith('multipart') else request.get_json())
    missing_params = []
    for name in required_params:
        if params.get(name) is None:
            missing_params.append(name)
    return (params, missing_params)


def route(*args, required_params=None, **kwargs):
    """Hacky helper to parse/validate params and jsonify response."""
    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            # route defs with can ask for request params to be parse 
            # by specifying a params function argument
            if 'params' in inspect.getfullargspec(f).args:
                params, missing_params = parse_params(required_params)
                if missing_params:
                   return jsonify(dict(error=f'Missing required params: {missing_params}')), 400
                kwargs['params'] = params

            status = 200
            resp = f(*args, **kwargs)
            if isinstance(resp, tuple):
                resp = resp[0]
                status = resp[1]
            return jsonify(dict(data=resp)), status
        return f
    return decorator


@route('/articles', methods=['get'])
def list_articles():
    articles = [art.as_dict() for art in article_service.all()]
    return articles

@route('/articles', methods=['post'], required_params=['user_id', 'title'])
def create_article(params):
    image = request.files['image']
    if image:
        image.filename = secure_filename(image.filename)
    article = article_service.create(image=image, **params)
    return article.as_dict()

@route('/articles/<id>', methods=['delete'])
def delete_article(id):
    article_service.delete(id)
    return {}, 204 

@route('/users', methods=['get'])
def list_users():
    users = [u.as_dict() for u in user_service.all()]
    return users

@route('/users', methods=['post'], required_params=['name', 'email'])
def create_user(params):
    user = user_service.create(**params)
    return user.as_dict()

@route('/users/<id>', methods=['delete'])
def delete_user(id):
    user_service.delete(id)
    return {}, 204
