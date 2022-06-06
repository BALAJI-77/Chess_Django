# sneetch
Games for natural and artificial intelligences

## Install
These are rough installation instructions (I have not retried them).

* Install Python 3.9.5
* Create a Python virtual environment with `python -m venv name_of_venv`
* Install the latest version of Redis
* If not running on windows, comment out the line `twisted-iocpsupport==1.0.1` from requirements.txt
* Run `pip install -r requirements.txt` to install all the Python dependencies
* Start Redis
* Run `python manage.py runserver` to start the web app
* Visit `localhost:8000` and click the `clicks` link to play the clicks game

## Using AIs

If you visit the game with an `aiport` in the URL:

`localhost:8000/clicks?aiport=8877`

then the game can only be played by an AI and the game will try to connect to an AI using the indicated port number. If you visit the game without an `aiport` number:

`localhost:8000/clicks`

then the game can only be played by a human and the game will not try to connect to an AI.

Here is how you would connect one AI to the game:

* Start an AI on a port #: `python client.py 8877`
* Start the website: `python manage.py runserver`
* Visit the game with the port # in the URL: `localhost:8000/clicks?aiport=8877`
* You should start to see random dots appear on the game screen

If you want to introduce human players, then simply open the game in another browser tab without `aiport` in the URL.

If you want to introduce additional AI players, then start a new AI client on a unique port number and then visit the game in new browser tab with `aiport` in the URL pointing to the new port number for the new AI. There is a one-to-one relationship between AI clients and AI browser tabs, ie. each AI needs its own port, client and browser tab - any other scenario is undefined behavior.
