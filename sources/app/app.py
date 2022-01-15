from flask import Flask, Blueprint, jsonify, render_template, flash, redirect, request, url_for
from .settings import *
from .models import User
from flask_login import current_user, login_required


import urllib

is_bot_running = False

def display_log(path):
    return open(path).read().replace("\n", "<br>")


@main.route('/bot_log')
def bot_log():
    site = "<h1>Telegram Bot Log</h1>"

    site += "<div id=\"log\">" + display_log("../bot/botlog.txt") + "</div>"

    return site

@main.route('/access_log')
def access_log():
    site = "<h1>Telegram Access Log</h1>"

    site += "<div id=\"log\">" + display_log("../bot/access_log.txt") + "</div>"

    return site

@main.route('/init')
def init():
    text = ""
    if is_bot_running:
        text+= "<h1>Bot is running...</h1>"
    else:
        text+= "<h1>Bot is offline.</h1>"
    text+= "<div id=\"content\"> <p>Links to Administration:</p><ul> <li><a href=\"init\">init Bot</a></li><li><a href=\"bot_log\">Bot Log</a></li><li><a href=\"access_log\">Access Log</a></li></ul></div>"
    return text

@main.route('/protected')
@login_required
def protected():
    return 'Hello, World!'

@main.route('/users')
def users():
    return jsonify([ (u.username, u.email) for u in User.query.all() ])


