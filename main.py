import argparse, sys, os
from collections import OrderedDict
import time, json
import requests

#CONSTANTS

URL_BASE = "https://www.instagram.com/"

URL_USER = URL_BASE+"{username}/?__a=1"

#==================================================

#PRETTY PRINT FUNCTIONS

def supports_color():
    supported_platform = (sys.platform != "Pocket PC") \
        and (sys.platform != "win32" \
        or "ANSICON" in os.environ \
        or "WT_SESSION" in os.environ \
        or os.environ.get("TERM_PROGRAM") == "vscode")
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty

BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
RESET = "\033[39m"

if not supports_color():
    BLUE = MAGENTA = CYAN = RESET = ""


def bannerprint():
    print(f"{MAGENTA}\
 ___           _                    _                  _        \n\
|_ _|_ __  ___| |_ __ _    _____  _| |_ _ __ __ _  ___| |_      \n\
| || '_ \/ __| __/ _` |  / _ \ \/ / __| '__/ _` |/ __| __|      \n\
| || | | \__ \ || (_| | |  __/>  <| |_| | | (_| | (__| |_  :p   \n\
|__|_| |_|___/\__\__,_|  \___/_/\_\___|_|  \__,_|\___|\__|      \n\
{RESET}")
    print("=============================================================")


def dictprint(d):
    if d is None:
        return

    for k, v in d.items():
        if k.startswith("sep"):
            print(f"\n{CYAN}[+]", v, f"{RESET}\n")
            continue
        print(f"{BLUE}{k}: {RESET}{v}")
        sys.stdout.flush()
    print("\n=============================================================")

#==================================================

#REQUEST

def safe_get(nretry, *args, **kwargs):
    try:
        response = requests.get(*args, **kwargs)

        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        if content_length is not None and int(content_length) != len(response.content):
            raise Exception("Partial response")

        return response

    except Exception as e:
        print("Error while getting:\n", e)
        if nretry-1 > 0:
            time.sleep(5)
            return safe_get(nretry-1, *args, **kwargs)
        else:
            return


def get_json(*args, **kwargs):
    response = safe_get(3, *args, **kwargs)
    return response.text if response is not None else None

#==================================================

#GET USER INFO

def user_info(username):
    response = get_json(URL_USER.format(username=username))

    if response is None:
        return

    results = json.loads(response)
    user_results = results["graphql"]["user"]

    info = OrderedDict()
    info["sep"] = "USER INFO"

    info["id"] = user_results["id"]
    info["username"] = user_results["username"]
    info["name"] = user_results["full_name"]

    info["profile_img_url"] = user_results["profile_pic_url_hd"]
    info["biography"] = user_results["biography"].replace("\n", " . ")
    info["external_url"] = user_results["external_url"]

    info["private"] = user_results["is_private"]
    info["verified"] = user_results["is_verified"]
    info["category"] = user_results["category_enum"]
    info["joined_recently"] = user_results["is_joined_recently"]
    info["business_account"] = user_results["is_business_account"]

    info["nfollowers"] = user_results["edge_followed_by"]["count"]
    info["nfollowing"] = user_results["edge_follow"]["count"]
    info["nimgs"] = user_results["edge_owner_to_timeline_media"]["count"]
    info["nvids"] = user_results["edge_felix_video_timeline"]["count"]
    info["nreels"] = user_results["highlight_reel_count"]

    if info["business_account"]:
        info["business_email"] = user_results["business_email"]
        info["business_phone_number"] = user_results["business_phone_number"]
        info["business_category_name"] = user_results["business_category_name"]

    return info

#==================================================

def args_control():

    ap = argparse.ArgumentParser(
        description="Extract and process data from instagram accounts",
        epilog="Author: @JavideSs"
    )

    ap.add_argument(
        "-u", "--user",
        help="Username to extract their information",
        metavar="username",
        type=str
    )

    if len(sys.argv) <= 1:
        ap.print_help()
        exit()

    return vars(ap.parse_args())


if __name__ == "__main__":
    args = args_control()

    bannerprint()

    if args["user"] is not None:
        user_info_data = user_info(args["user"])
        dictprint(user_info_data)