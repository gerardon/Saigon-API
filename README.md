# Saigon

Saigon is a project to port a board game called [Codenames from Vlaada Chvátil](https://boardgamegeek.com/boardgame/178900/codenames)
to the internet world.

Currently the game provides an HTTP API to play the game and you can build the
interface using the tool you want to.

You can install and run the api simply by cloning this repo and install
the requirements:
```
git clone git@github.com:gerardon/Saigon-API.git
pip install requirements.txt
gunicorn app:api
```
You can run the tests by typing this in our terminal: `pip install unittest2; python -m unittest`
