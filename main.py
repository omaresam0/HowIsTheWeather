import config
import requests
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# db configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///HowIsweather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)  # can't stay null


@app.route('/', methods=['GET', 'POST'])
def index():
    show_label = False
    message = ""

    if request.method == "POST":
        # get city from user and add it to db
        city1 = request.form.get('cityInput')
        if city1:  # if it exists
            url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=" + config.OPENWEATHERMAP_API_KEY
            response = requests.get(url.format(city1)).json()

            # Checking cod key in the response dic (http response code returned by the api)
            #COD = 200 - successful, 404 - not found in db, etc.
            if response['cod'] == '404':
                message = f"Please enter a valid city."
            else: #adding city
                cityObj = City(name=city1)
                db.session.add(cityObj)
                db.session.commit()
                show_label = True
                cities_count = City.query.count()
                show_label = True if cities_count > 2 else False

    cities = City.query.all()
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=21b8d60c2bbb73f3bb7d6a7a7736944b"
    weatherData = []

    for city in cities:
        # adding the city in the {} placeholder in url
        response = requests.get(url.format(city.name)).json()

        # Check if 'main' key is present in response
        if 'main' in response:
            temperature = response['main']['temp']
        else:
            temperature = None

        # Check if 'weather' key is present in response
        if 'weather' in response and len(response['weather']) > 0:
            description = response['weather'][0]['description']
            icon = response['weather'][0]['icon']
        else:
            description = None
            icon = None

        weatherFiltered = {
            'city': city.name,
            'temperature': temperature,
            'description': description,
            'icon': icon,
        }
        weatherData.append(weatherFiltered)

    # passing data to template
    return render_template('index.html', weatherData=weatherData, show_label=show_label, message=message)


@app.route('/delete/<name>')
def remove(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, host="0.0.0.0", port=8000)
