"""Masterblog API: a small Flask backend for blog posts.

Endpoints: list (with sorting ascending and descending), add, delete, update and search and errorhandling.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Return all posts as JSON, optionally sorted.

    Optional query parameters:
        sort: field to sort by, 'title' or 'content'.
        direction: 'asc' (default) or 'desc'.

    Without 'sort' the posts keep their original order (200).
    An invalid 'sort' or 'direction' value returns an error (400).
    """
    usr_sort = request.args.get('sort')
    usr_direction = request.args.get('direction')

    if usr_direction is None:
        usr_direction = 'asc'

    if usr_direction not in ['asc', 'desc']:
        return jsonify({'error': f'Invalid direction: {usr_direction}'}), 400

    if usr_sort is not None:
        if usr_sort not in ['title', 'content']:
            return jsonify({'error': f'Invalid sort field: {usr_sort}'}), 400

    if usr_sort is None:
        return jsonify(POSTS)
    else:
        sorted_posts = sorted(
            POSTS,
            key=lambda post: post[usr_sort],
            reverse=usr_direction == 'desc'
        )
        return jsonify(sorted_posts)


@app.route('/api/posts', methods=['POST'])
def add_post():
    """Create a new post from the JSON body.

    Both 'title' and 'content' are required.
    Returns the new post with its generated ID (201), or the list of
    missing fields (400).
    """
    # 2myself: server receives new entry and sends ok message to frontend
    data = request.get_json()

    missing_fields = []
    if 'title' not in data:
        missing_fields.append('title')
    if 'content' not in data:
        missing_fields.append('content')

    if missing_fields:
        return jsonify({'error': f'Missing fields: {missing_fields}'}), 400

    all_ids = [post['id'] for post in POSTS]
    if all_ids:
        new_id = max(all_ids) + 1
    else:
        new_id = 1
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete the post with the given ID.

    Returns a confirmation message (200), or an error if the ID does
    not exist (404).
    """
    all_ids = [post['id'] for post in POSTS]
    if post_id not in all_ids:
        return jsonify(
            {'ERROR': f'Your post ID {post_id} is not in the list'}
        ), 404
    else:
        for post in POSTS:
            if post['id'] == post_id:
                POSTS.remove(post)
                break
        return jsonify({'message': f'Post {post_id} has been deleted'}), 200


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update title and/or content of the post with the given ID.

    Fields missing in the JSON body keep their current value.
    Returns the updated post (200), or an error if the ID does not
    exist (404).
    """
    data = request.get_json()
    all_ids = [post['id'] for post in POSTS]
    if post_id not in all_ids:
        return jsonify(
            {'ERROR': f'Your post ID {post_id} is not in the list'}
        ), 404
    else:
        for post in POSTS:
            if post['id'] == post_id:
                if 'title' in data:
                    post['title'] = data['title']
                if 'content' in data:
                    post['content'] = data['content']
                break
        return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    """Return posts whose title or content contains the search term.

    Optional query parameters:
        title: search term for the post title.
        content: search term for the post content.

    Returns the matching posts as JSON (200), an empty list if nothing
    matches.
    """
    usr_srch_title = request.args.get('title')
    usr_srch_content = request.args.get('content')

    search_results = []
    for post in POSTS:
        if (
            usr_srch_title is not None and usr_srch_title in post['title']
            or usr_srch_content is not None
            and usr_srch_content in post['content']
        ):
            search_results.append(post)
    return jsonify(search_results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
