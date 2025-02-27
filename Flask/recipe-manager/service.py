from models import Users
from typing import Optional

    

def get_author_obj(author_id: int) -> Optional[Users]:
    user_obj = Users.query.filter_by(id=author_id).first()

    return user_obj
