from flask import Flask, render_template, request, jsonify
import json


app = Flask(__name__)


@app.route('/')
def root():
    return render_template('Homepage.html')


@app.route('/filter-users', methods=['POST'])
def filter_users():
    ## Right now I just used "INFORMS2023" data we have as a demo, we'll change to a more logic data latter.
    with open('tweet.json', 'r', encoding='utf-8') as file:
        users = json.load(file)

    # Get maxCount and hashtag from post(Selected parameter from the html page)
    data = request.get_json()
    max_count = data.get('maxCount')
    tag = data.get('tag')
    filtered_user = []
    for user in users:
        if tag in user['tweet_hashtags']:
            filtered_user.append(user)

    # Sort by the sum of replies likes and retweet for each user. (Algorithms that can be further optimized)
    sorted_users = sorted(filtered_user, key=lambda user: user['replies'] + user['likes'] + user['retweets'],
                          reverse=True)

    # Get the top max_count users
    filtered_users = sorted_users[:max_count]

    # Returns filtered user avatar
    return jsonify([user['tweet_avatar'] for user in filtered_users], [user['url'] for user in filtered_users]), 200


if __name__ == '__main__':
    app.run()
