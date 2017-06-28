from models import User
from app import ma
# serializer for my models

class UserSchema(ma.ModelSchema):
    class meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)
