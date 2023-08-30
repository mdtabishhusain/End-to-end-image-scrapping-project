from flask import Flask, render_template, request, jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
import os
logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route("/review", methods = ['POST', 'GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            # Query to search for images
            query = request.form['content'].replace(" ", "")

            # directory to store downloaded images
            save_dir = "images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AB5stBg-UqbcoWxswoz2kG_H4PbO-c2K2Q:1693102839810&q=feroze+gandhi+institute+of+engineering+and+technology&tbm=isch&source=lnms&sa=X&ved=2ahUKEwjq3dbK4_uAAxVFS2wGHaL7AyEQ0pQJegQICxAB&biw=864&bih=618&dpr=1")
            soup = BeautifulSoup(response.content,features="html.parser")
            images_tags = soup.find_all("img")
            del images_tags[0]
            img_data = []
            for index,image_tag in enumerate(images_tags):
                image_url = image_tag['src']
                image_data = requests.get(image_url).content
                mydict = {"Index":index, "image":image_data}
                img_data.append(mydict)
                with open (os.path.join(save_dir, f"{query}_{images_tags.index(image_tag)}.jpg"),"wb") as f:
                    f.write(image_data)
                    
            client = pymongo.MongoClient("mongodb+srv://pyproject:allisfunMDB25@cluster0.ukhlydk.mongodb.net/?retryWrites=true&w=majority")
            db = client["Image_Scrapping"]
            coll_image = db["Image_Scrapping"]
            coll_image.insert_many(img_data)

            return "Thank you for searching, Please contact admin (from where you get the link) for output images"
        except Exception as e:
            logging.info(e)
            return 'Something Is Wrong, Please contact admin(from where you get the link).'

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='172.18.0.12', port=8000, debug=True)
