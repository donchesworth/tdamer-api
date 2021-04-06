import requests
import json
from pathlib import Path
import os
import time
from dotenv import load_dotenv, find_dotenv

RFILE = Path.cwd().joinpath("refresh_token.json")

def get_envs() -> dict:
    """Pull environment variables

    Returns:
        dict: Set of environment variables
    """
    load_dotenv(find_dotenv())
    envs = {}
    envs['CLIENT_ID'] = os.environ.get("CLIENT_ID")
    envs['TD_ACCT'] = os.environ.get("TD_ACCT")
    envs['AUTH_ENDPOINT'] = "https://api.tdameritrade.com/v1/oauth2/token"
    envs['LOCALURI'] = "http://localhost"
    return envs


def rtoken_is_fresh() -> bool:
    """Check if current refresh token is more than 60 days old
    (actually expires after 90 days)

    Returns:
        bool: whether refresh token is expired
    """
    global RFILE
    fresh = False
    if RFILE.is_file():
        save_time = RFILE.lstat().st_mtime
        fresh = (time.time() - save_time) / 86400 < 60
    return fresh


def get_current_rtoken() -> dict:
    """Pull current refresh token from file since it's
    not expired

    Returns:
        dict: dictionary including refresh token
    """
    global RFILE
    with open(RFILE) as f:
        tokens = json.load(f)
    return tokens


def write_tokens(new_token):
    global RFILE
    with open(RFILE, "w") as f:
        json.dump(new_token.json(), f, indent=2)


def get_new_rtoken(current: dict, envs: dict) -> dict:
    """This is the UNPROVEN method to get a new 90 day
    refresh token after the previous is going to expire.

    Args:
        tokens (dict): A dictionary containing the current
        refresh token
        envs (dict): Set of environment variables

    Returns:
        dict: the response.json() dict from the response
    """
    rtoken = current["refresh_token"]
    body_params = {
        "grant_type": "refresh_token",
        "refresh_token": rtoken,
        "access_type": "offline",
        "client_id": CLIENTID,
        "redirect_uri": LOCALURI,
    }
    response = requests.post(AUTH_ENDPOINT, data=body_params)
    if response.status_code == 200:
        print("received new refresh code")
    write_tokens(response)
    return response.json()


def get_refresh_token(envs: dict) -> dict:
    """Using the current refresh token information,
    checks if the refresh token is still current,
    and if isn't gets a new one, and returns either
    the current or the new.

    Args:
        envs (dict): Set of environment variables

    Returns:
        dict: A current refresh token
    """
    current = get_current_rtoken()
    if rtoken_is_fresh():
        return get_new_rtoken(current, envs)
    else:
        return current


def thirty_min_access_token(current: dict, envs: dict) -> dict:
    """This is the method to get a 30 minute access token to access TD data.
    A refresh token (which is good for 90 days) is used.

    Args:
        current (dict): The current refresh token
        envs (dict): Set of environment variables

    Returns:
        dict: A dict with TD positions
    """
    rtoken = current["refresh_token"]
    body_params = {
        "grant_type": "refresh_token",
        "refresh_token": rtoken,
        "client_id": CLIENTID,
        "redirect_uri": LOCALURI,
    }
    response = requests.post(AUTH_ENDPOINT, data=body_params)
    if response.status_code == 200:
        print("received new access code")
    return response.json()
