from chanjo.store.models import BASE
from flask_sqlalchemy import SQLAlchemy

api = SQLAlchemy(model_class=BASE)
