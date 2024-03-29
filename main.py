import argparse, sys, os
from collections import OrderedDict, Counter
import time, datetime, random, pickle, json, re
import requests

#CONSTANTS

URL_BASE = "https://www.instagram.com/"
URL_API = "https://i.instagram.com/api/v1/users/web_profile_info/?"

URL_LOGIN = URL_BASE+"accounts/login/ajax/"
URL_LOGOUT = URL_BASE+"accounts/logout/"

URL_USER = URL_API+"username={username}"
URL_POST = URL_API+"media_shortcode={post_shortcode}"

URL_QUERY = URL_BASE+"graphql/query/?query_hash={hash}&variables={params}"

TOGET_FOLLOWINGS = {
    "str": "followings",
    "hash": "c56ee0ae1f89cdbd1c89e2bc6b8f3d18",
    "edge_path": "edge_follow"
}
TOGET_FOLLOWERS = {
    "str": "followers",
    "hash": "5aefa9893005572d237da5068082d8d5",
    "edge_path": "edge_followed_by"
}
TOGET_POSTS = {
    "str": "posts",
    "hash": "42323d64886122307be10013ad2dcc44",
    "edge_path": "edge_owner_to_timeline_media"
}

USERAGENTS = (
    "Mozilla/5.0 (Linux; Android 9; GM1903 Build/PKQ1.190110.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/75.0.3770.143 Mobile Safari/537.36 Instagram 103.1.0.15.119 Android (28/9; 420dpi; 1080x2260; OnePlus; GM1903; OnePlus7; qcom; sv_SE; 164094539)",
)

def urlshortner(url):
    return requests.get("http://tinyurl.com/api-create.php?url=" + url).text

FNAME_SESSION = "usersession"

#==================================================

#AUTHENTICATION

class User:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "user-agent": random.choice(USERAGENTS)
        })

    def isLogin(self):
        return False

    @staticmethod
    def loadSession(fpath):
        with open(fpath, "rb") as f:
            return pickle.load(f)

    def saveSession(self, fpath):
        with open(fpath, "wb") as f:
            pickle.dump(self, f)


class AuthenticateUser(User):
    def __init__(self):
        super().__init__()
        self.session.headers = {
            "Referer": URL_BASE,
        }
        response = self.session.get(
            URL_BASE
        )
        self.session.headers.update({
            "X-CSRFToken": response.cookies["csrftoken"]
        })

        self.login_session = None

    def isLogin(self):
        return self.login_session is not None \
            and json.loads(self.login_session.text).get("authenticated") \
            and self.login_session.status_code == 200

    def login(self, username, password):
        self.login_session = self.session.post(
            url=URL_LOGIN,
            data={"username":username, "password":password},
            allow_redirects=True
        )

        if self.isLogin():
            self.session.headers.update({
                "user-agent": random.choice(USERAGENTS)
            })
        else:
            print("Error while login:\n", json.loads(self.login_session.text))

    def logout(self):
        if self.isLogin():
            self.session.post(
                url=URL_LOGOUT,
                data={"csrfmiddlewaretoken": self.login_session.cookies["csrftoken"]}
            )

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


def printsep():
    print("\n" + "="*61)


def bannerprint():
    print(f"{MAGENTA}\
 ___           _                    _                  _        \n\
|_ _|_ __  ___| |_ __ _    _____  _| |_ _ __ __ _  ___| |_      \n\
| || '_ \/ __| __/ _` |  / _ \ \/ / __| '__/ _` |/ __| __|      \n\
| || | | \__ \ || (_| | |  __/>  <| |_| | | (_| | (__| |_  :p   \n\
|__|_| |_|___/\__\__,_|  \___/_/\_\___|_|  \__,_|\___|\__|      \
{RESET}")
    printsep()


def dictprint(d):
    if d is None:
        return

    for k, v in d.items():
        if k.startswith("sep"):
            print(f"\n{CYAN}[+] {v}{RESET}\n")
            continue
        if isinstance(v, (list, tuple, set)):
            v = ", ".join(v)
        print(f"{BLUE}{k}: {RESET}{v}")
        sys.stdout.flush()
    printsep()


def listprint(l, title):
    if l is None:
        return

    print(f"\n{CYAN}{title}{RESET}\n")
    if not len(l):
        print("-")
    else:
        for v in l:
            print(v, end=", ")
    print()

#==================================================

#DEBUG FUNCTIONS

def debugjson(text, fname):
    with open(fname, "w") as fjson:
        json.dump(text, fjson, indent=4)

#==================================================

#REQUEST

def safe_get(nretry, *args, **kwargs):
    try:
        response = user.session.get(
            timeout=90,
            *args, **kwargs
        ) if not user.isLogin() \
        else user.session.get(
            timeout=90,
            cookies=user.login_session.cookies,
            *args, **kwargs
        )

        response.raise_for_status()

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
    return response.text if response is not None and response.ok else None


def download_webimg(url):
    response = requests.get(
        url,
        allow_redirects=True,
        stream=True
    )

    if not response.ok:
        print("Error while downloading post")
        return

    re_f_name = re.search("[a-zA-Z0-9_]+.jpg", url)
    f_name = re_f_name.group(0) if re_f_name is not None else "image.jpg"

    with open(f_name, "wb") as f:
        for block in response.iter_content(1024):
            if not block:
                break
            f.write(block)

#==================================================

#QUERY WITH CURSOR

def query_with_cursor(userid, toget, end_cursor):
    params = '{{"id":"{id}","first":50,"after":"{end}"}}'.format(id=userid, end=end_cursor)
    response = get_json(URL_QUERY.format(hash=toget["hash"], params=params))

    if response is None:
        return None, None

    edge = json.loads(response)["data"]["user"][toget["edge_path"]]

    if not edge:
        return None, None

    nodes = [node["node"] for node in edge["edges"]]
    end_cursor = edge["page_info"]["end_cursor"]
    return nodes, end_cursor


def query_with_cursor_gen(username, toget, end_cursor=""):
    userid = user_info(username)["id"]

    if userid is None:
        return

    while True:
        nodes, end_cursor = query_with_cursor(userid, toget, end_cursor)

        if not nodes:
            return

        for node in nodes:
            yield node

        if not end_cursor:
            return

#==================================================

#GET USER INFO

def get_user_info(username, to_download=False):
    response = get_json(URL_USER.format(username=username))

    if response is None:
        return

    results = json.loads(response)
    user_results = results["data"]["user"]

    info = OrderedDict()
    info["sep"] = "USER INFO"

    info["id"] = user_results["id"]
    info["username"] = user_results["username"]
    info["name"] = user_results["full_name"]

    info["profile_img_url"] = urlshortner(user_results["profile_pic_url_hd"])
    if to_download:
        download_webimg(user_results["profile_pic_url_hd"])

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

    func_list_sorted_by_counter = lambda l: next(zip(*sorted(Counter(l).items(), reverse=True, key=lambda v: v[1])))

    user_tags = re.findall(r"[＃#]([_a-zA-Z0-9\.\+-]+)", response)
    if len(user_tags):
        info["most_used_tags"] = func_list_sorted_by_counter(user_tags)[:5]

    user_mentions = re.findall(r"[＠@]([_a-zA-Z0-9\.\+-]+)", response)
    user_mentions = [mention for mention in user_mentions if mention != username]
    if len(user_mentions):
        info["most_used_mentions"] = func_list_sorted_by_counter(user_mentions)[:5]

    user_emails = re.findall(r"[_a-zA-Z0-9-\.]+[＠@][a-zA-Z0-9]+\.[a-zA-Z0-9]+", response)
    if len(user_emails):
        info["emails_found"] = user_emails

    return info


user_info = get_user_info

#==================================================

#GET POST INFO

def get_post_info(node, ipost, to_download, deep=True):
    #Option deep=True if the search has been made by query by cursor

    if deep:
        response = get_json(URL_POST.format(post_shortcode=node["shortcode"]))

        if response is None:
            return

        post_results = json.loads(response)["graphql"]["shortcode_media"]

    else:
        post_results = node

    info = OrderedDict()
    info["sep"] = "POST INFO "+str(ipost)

    info["timestamp"] = post_results["taken_at_timestamp"]
    info["date"] = datetime.datetime.fromtimestamp(post_results["taken_at_timestamp"])
    info["nlikes"] = post_results["edge_media_preview_like"]["count"]
    info["comments_disabled"] = post_results["comments_disabled"]

    info["ncomments"] = post_results["edge_media_to_comment"
        if "edge_media_to_comment" in post_results
        else "edge_media_to_parent_comment"
        ]["count"]

    location = post_results["location"]
    info["location"] = location["name"]+" (id: "+location["id"]+")" \
        if location is not None \
        else location

    caption = post_results["edge_media_to_caption"]["edges"]
    if len(caption):
        info["caption"] = caption[0]["node"]["text"].replace("\n", " . ")

    total_imgs = len(post_results["edge_sidecar_to_children"]["edges"]) \
        if "edge_sidecar_to_children" in post_results \
        else 1

    for iimage in range(total_imgs):
        iimage_str = "("+str(iimage)+") "

        post_image_results = post_results["edge_sidecar_to_children"]["edges"][iimage]["node"] \
            if total_imgs != 1 \
            else post_results

        info["sep "+str(iimage)] = "IMAGE "+str(iimage)

        info[iimage_str+"id"] = post_image_results["id"]

        info[iimage_str+"image_url"] = urlshortner(post_image_results["display_url"])
        if to_download:
            download_webimg(post_image_results["display_url"])

        info[iimage_str+"accessibility"] = post_image_results["accessibility_caption"]

        info[iimage_str+"type"] = "video" if post_image_results["is_video"] else "image"
        info[iimage_str+"typename"] = post_image_results["__typename"]
        info[iimage_str+"dimensions"] = "{width}x{height}".format(
            width=post_image_results["dimensions"]["width"],
            height=post_image_results["dimensions"]["height"]
        )

    return info


def post_info(username, ipost, to_download):
    #You have to make a query by cursor if the image is not from the last 12 uploads

    if ipost > 11:
        for i, node in enumerate(query_with_cursor_gen(username, TOGET_POSTS)):
            if i == ipost:
                return get_post_info(node, ipost, to_download)

    else:
        response = get_json(URL_USER.format(username=username))

        if response is None:
            return

        results = json.loads(response)
        node = results["data"]["user"]["edge_owner_to_timeline_media"]["edges"][ipost]["node"]

        return get_post_info(node, ipost, to_download, deep=False)


def posts_info(username, to_download):
    if not user.isLogin():
        i = 0
        while True:
            try:
                yield post_info(username, i, to_download)
                i+=1
            except IndexError:
                return

    for i, node in enumerate(query_with_cursor_gen(username, TOGET_POSTS)):
        yield get_post_info(node, i, to_download)

#==================================================

#GET FOLLOWERS/FOLLOWINGS USERNAMES

def followerings_usernames(username, f, toget):
    with f:
        f.write(username + "|"+toget["str"]+"|" + str(int(time.time())) + "\n")
        for node in query_with_cursor_gen(username, toget):
            f.write(node["username"] + "\n")
            f.flush()

#==================================================

#COMPARE USERNAMES

def cmp_usernames(f1, f2):
    with f1:
        with f2:
            try:
                _, mode1, t1 = f1.readline().split("|")
                _, mode2, t2 = f2.readline().split("|")

                usernames1 = set(f1.read().splitlines())
                usernames2 = set(f2.read().splitlines())
            except:
                print("Error while comparing usernames")
                return

            usernames1_notin_2 = usernames1.difference(usernames2)
            usernames2_notin_1 = usernames2.difference(usernames1)

            if mode1 == mode2:
                if t2 < t1:
                    usernames1_notin_2, usernames2_notin_1 \
                        = usernames2_notin_1, usernames1_notin_2

                listprint(usernames1_notin_2, mode1.upper() + " WHO ARE NO LONGER")
                listprint(usernames2_notin_1, mode1.upper() + " WHO WERE NOT BEFORE")
                printsep()

            else:
                if mode1 == "followers":
                    usernames1_notin_2, usernames2_notin_1 \
                        = usernames2_notin_1, usernames1_notin_2

                listprint(usernames1_notin_2, "FOLLOWINGS NOT FOLLOWERS")
                listprint(usernames2_notin_1, "FOLLOWERS NOT FOLLOWINGS")
                printsep()

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

    ap.add_argument(
        "-l", "--login",
        help="Login username and password required for some options",
        metavar=("username", "password"),
        type=str,
        nargs=2
    )

    ap.add_argument(
        "-i", "--info",
        help="""User profile info,
            option not necessary if no other option is used to extract user info""",
        action="store_true"
    )

    ap.add_argument(
        "-p", "--post",
        help="""Info of all post if not arguments,
            else info of the post at index (counting from the last post as 0)""",
        metavar="n",
        type=int,
        nargs="?",
        const=-1
    )

    ap.add_argument(
        "-dp", "--download_posts",
        help="Download posts found by the other options",
        action="store_true"
    )

    ap.add_argument(
        "-f1", "--get_followings",
        help="Usernames of the user's followings",
        metavar="outfile",
        type=argparse.FileType("w")
    )

    ap.add_argument(
        "-f2", "--get_followers",
        help="Usernames of the user's followers",
        metavar="outfile",
        type=argparse.FileType("w")
    )

    ap.add_argument(
        "-c", "--cmp",
        help="Compare two user lists created by the -f1 or -f2 options",
        metavar=("infile1", "infile2"),
        type=argparse.FileType("r"),
        nargs=2
    )

    if len(sys.argv) <= 1:
        ap.print_help()
        exit()

    return vars(ap.parse_args())


if __name__ == "__main__":
    args = args_control()

    bannerprint()

    if os.path.exists(FNAME_SESSION):
        user = User.loadSession(FNAME_SESSION)
    elif args["login"] is not None:
        user = AuthenticateUser()
        user.login(*args["login"])
    else:
        user = User()

    if args["user"] is not None:
        user_info_data = user_info(args["user"], args["download_posts"])

        only_user_info = True
        for k in ("post", "get_followings", "get_followers"):
            if args[k] != None:
                only_user_info = False
                break
        if args["info"] or only_user_info:
            dictprint(user_info_data)

        if args["post"] is not None:
            if user_info_data["private"]:
                print("Can't get post(s) info ->", "You must follow him")

            else:
                if args["post"] == -1:
                    if not user.isLogin():
                        print("Can't get more than 12 posts ->", "You must be logged in")
                    for post_info_data in posts_info(args["user"], args["download_posts"]):
                        dictprint(post_info_data)
                else:
                    if args["post"] > 11 and not user.isLogin():
                        print("Can't get post info ->", "If post index > 11 you must be logged in")
                    try:
                        post_info_data = post_info(args["user"], args["post"], args["download_posts"])
                        dictprint(post_info_data)
                    except IndexError:
                        print("Can't get post info ->", "Invalid index")

        if args["get_followings"] is not None:
            if not user.isLogin():
                print("Can't get followings ->", "You must be logged in")
            else:
                followerings_usernames(args["user"], args["get_followings"], TOGET_FOLLOWINGS)

        if args["get_followers"] is not None:
            if not user.isLogin():
                print("Can't get followers ->", "You must be logged in")
            else:
                followerings_usernames(args["user"], args["get_followers"], TOGET_FOLLOWERS)

    if args["cmp"] is not None:
        cmp_usernames(*args["cmp"])

    if user.isLogin():
        user.logout()
        user.saveSession(FNAME_SESSION)