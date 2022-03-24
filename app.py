import os

from flask import Flask, flash, redirect, render_template, request
from helpers import games_list, pick_game, resolve_vanity, validate_url, validate_id

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
def index():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign URL variable
        url = request.form.get("steamurl")

        # Ensure url was submitted
        if not request.form.get("steamurl"):
            flash("Missing URL!")
            return redirect("/")

        # Check for invalid URL
        elif validate_url(url) == -1:
            flash("Invalid URL!")
            return redirect("/")

        # Check for vanity URL and resolve to SteamID
        elif validate_url(url) == 1:
            if not resolve_vanity(url):
                flash("Invalid CommunityID!")
                return redirect("/")
            else:
                steamid = resolve_vanity(url)

        # Check for SteamID, clean up, and assign to variable
        elif validate_url(url) == 0:
            steamid = url.partition("/profiles/")[2].replace("/", "")

        # Validate profile public view
        if not validate_id(steamid):
            flash("Unable to access Steam profile! Make sure your profile and game details are set to public.")
            return redirect("/")

        # Assign list
        else:
            all_games = validate_id(steamid)

        # Create lists
        unplayed_list, replay_list = games_list(all_games)

        unplayed = pick_game(unplayed_list)
        replay = pick_game(replay_list)
        rand_game = pick_game(all_games)

        return render_template("results.html", unplayed=unplayed, replay=replay, rand_game=rand_game, url=url)

    else:
        return render_template("index.html")