# -*- coding: utf-8 -*-

from flask import Flask, jsonify, url_for, redirect, request
from flask_pymongo import PyMongo
from flask_restful import Api, Resource

app = Flask(__name__)
app.config["MONGO_DBNAME"] = "tweets_db"
mongo = PyMongo(app, config_prefix='MONGO')
APP_URL = "http://127.0.0.1:5000"


class Tweets(Resource):
    def get(self, id=None, range=None, emotion=None):
        data = []

        if id:
            tweet_info = mongo.db.tweets.find_one({"id": id}, {"_id": 0})
            if tweet_info:
                return jsonify({"status": "ok", "data": tweet_info})
            else:
                return {"response": "no tweet found for {}".format(id)}

        elif range:
            #YYYYMMDDHHMMSS
            range = range.split('to')
            cursor = mongo.db.tweets.find({"timestamp":{"$gt": int(range[0])}, "timestamp":{"$lt": int(range[1])}}, {"_id": 0}).limit(10)
            for tweet in cursor:
                tweet['url'] = APP_URL + url_for('tweets') + "/" + tweet.get('id')
                data.append(tweet)

            return jsonify({"range": range, "response": data})

        elif emotion:
            cursor = mongo.db.tweets.find({"emotion": emotion}, {"_id": 0}).limit(10)
            for tweet in cursor:
                tweet['url'] = APP_URL + url_for('tweets') + "/" + tweet.get('id')
                data.append(tweet)

            return jsonify({"emotion": emotion, "response": data})

        else:
            cursor = mongo.db.tweets.find({}, {"_id": 0, "update_time": 0}).limit(10)

            for tweet in cursor:
                print tweet
                tweet['url'] = APP_URL + url_for('tweets') + "/" + tweet.get('id')
                data.append(tweet)

            return jsonify({"response": data})

    def post(self):
        data = request.get_json()
        if not data:
            data = {"response": "ERROR"}
            return jsonify(data)
        else:
            id = data.get('id')
            if id:
                if mongo.db.tweets.find_one({"id": id}):
                    return {"response": "tweet already exists."}
                else:
                    mongo.db.tweets.insert(data)
            else:
                return {"response": "id number missing"}

        return redirect(url_for("tweets"))

    def put(self, id):
        data = request.get_json()
        mongo.db.tweets.update({'id': id}, {'$set': data})
        return redirect(url_for("tweets"))

    def delete(self, id):
        mongo.db.tweets.remove({'id': id})
        return redirect(url_for("tweets"))


class Index(Resource):
    def get(self):
        return redirect(url_for("tweets"))


api = Api(app)
api.add_resource(Index, "/", endpoint="index")
api.add_resource(Tweets, "/api", endpoint="tweets")
api.add_resource(Tweets, "/api/<string:id>", endpoint="id")
api.add_resource(Tweets, "/api/emotion/<string:emotion>", endpoint="emotion")
api.add_resource(Tweets, "/api/range/<string:range>", endpoint="range")

if __name__ == "__main__":
    app.run(debug=True)