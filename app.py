from flask import Flask, jsonify
from flask import request as rq
from flask_cors import CORS, cross_origin

from openai import OpenAI
import os
import gensim
import logging
import dotenv

from crawling import get_public_dataset, get_news, get_github_repos

import urllib.request

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
API_KEY = os.environ.get("OPENAI_API_KEY") # openai api key


client = OpenAI(
    api_key=API_KEY
)

# word2vec
# model_path = "./models/ko.bin"
# model = gensim.models.Word2Vec.load(model_path)

# fasttext
model_path = "./models/ft_namu.bin"
model = gensim.models.fasttext.load_facebook_model(model_path)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cors = CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'


#단어에 대한 정보 제공
@app.get("/words")
@cross_origin()
def get_words():
    default_word_count = 10
    parameter_dict = rq.args.to_dict()

    topic_word = parameter_dict["topicWord"]
    except_words = parameter_dict["exceptWords"].split(',')
    seq = int(parameter_dict['seq'])

    related_words = [result[0] for result in model.wv.most_similar(topic_word, topn=seq * 10 + default_word_count + len(except_words))];
    words = { 
        "words":  [x for x in related_words if x not in except_words][seq * 10: seq * 10 + default_word_count]
    }
    return jsonify(words)


@app.get("/datasets")
def datasets():
    parameter_dict = rq.args.to_dict()
    topic_word = parameter_dict["topicWord"]
    result = {
        "datasets": get_public_dataset(topic_word)
    }
    return jsonify(result)


@app.get("/news")
def news():
    parameter_dict = rq.args.to_dict()
    topic_word = parameter_dict["topicWord"]
    result = {
        "news": get_news(topic_word)
    }
    return jsonify(result)


@app.get("/repositories")
def repositories():
    parameter_dict = rq.args.to_dict()
    topic_word = parameter_dict["topicWord"]

    result = {
        "repos": get_github_repos(topic_word)
    }
    return jsonify(result)


@app.post("/words")
def train_words(): # word2vec 파인튜닝
    pass


@app.get("/topics")
def get_topics():
    parameter_dict = rq.args.to_dict()
    topic_words = parameter_dict['words'].split(',')

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        # model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You must return four app ideas as json that type is { title, subtitle, description } in array. Array's key is 'ideas'. One description should be no more than 250 characters but need a detail. Language should be korean as honorific. "},
            {"role": "user", "content": '{}'.format(', '.join(topic_words))}
            # {"role": "user", "content": "아니 내가 앱 주제를 선정해주는 프로그램을 만드는데 프로세스가 어떻게 되어야 할까"}
        ]
    )
    return completion.choices[0].message.content
    

if __name__ == "__main__":
    app.run()