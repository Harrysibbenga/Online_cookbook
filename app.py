import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'online_cookbook'
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

@app.route('/')
@app.route('/get_recipes')
def get_recipes():
    return render_template('recipes.html', recipes=mongo.db.recipes.find(), 
    authors=mongo.db.authors.find(), allergins=mongo.db.allergins.find(), types=mongo.db.types.find(),
    countries=mongo.db.countries.find(), cuisines=mongo.db.cuisines.find(), diets=mongo.db.diets.find(),
    origins=mongo.db.origins.find(), categories=mongo.db.categories.find())

if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
        port=int(os.environ.get('PORT')),
        debug=True)