from flask import Flask, jsonify, request
from openai import OpenAI
import os
import gensim
import logging
import dotenv


dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)
API_KEY = os.environ.get("OPENAI_API_KEY") # openai api key

model_path = "models/ko.bin"


client = OpenAI(
    api_key=API_KEY
)

model = gensim.models.Word2Vec.load(model_path)
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.get("/words")
def get_words():
    parameter_dict = request.args.to_dict()
    topic_word = parameter_dict["word"]
    words = { 
        "words" : [result[0] for result in model.wv.most_similar(topic_word)] 
    }
    return jsonify(words)

@app.get("/topics")
def get_topics():
    parameter_dict = request.args.to_dict()
    topic_words = parameter_dict['words'].split(',')

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "user", "content": '{}에 대한 앱 개발 주제 제목만'.format(', '.join(topic_words))}
        ]
    )

    return completion.choices[0].message.content
    



if __name__ == "__main__":
    app.run()