from models import Users, Comments, Ratings

def get_post_data(post):
    author = get_author(post.author)
    created_at = post.created_at
    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')

    post_data_dict = {
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'author': author,
        'created_at': created_at
    }

    return post_data_dict


def get_comment_data(comment):
    created_at = comment.created_at
    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')

    replied_comment_author_id = Comments.query.filter_by(id=comment.parent_id).first()

    comment_data = {
        'id': comment.id,
        'content': comment.content,
        'author': get_author(comment.author),
        'created_at': created_at,
        'reply_to': get_author(replied_comment_author_id.author) if replied_comment_author_id else None
    }

    return comment_data


def get_author(author_id):
    author = Users.query.filter_by(id=author_id).first()

    return author.username


def get_post_rating(post):
    rating_obj = Ratings.query.filter_by(post=post.id).all()

    if not rating_obj:
        rating = 0
    
    else:
        rating = sum(rating.rating for rating in rating_obj) / len(rating_obj)
    
    rating = int(round(rating, 0))
    
    stars_list = []
    for num in range(1, rating + 1):
        stars_list.append('<i class="fa-solid fa-star"></i>')
    
    for _ in range(5 - rating):
        stars_list.append('<i class="fa-regular fa-star"></i>')
    
    return stars_list
