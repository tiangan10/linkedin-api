from linkedin_api import Linkedin
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import os
import argparse
import glob
import os

_DALIANA = "dalianaliu"
_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
_MAX_POST_COUNT = 2000
_NORMAL_POST_COUNT = 100


def _get_abs_time(time_diff):
    num_and_unit = time_diff.split(" ")[0]
    for i, c in enumerate(num_and_unit):
        if not c.isdigit():
            break
    num = int(num_and_unit[:i])
    unit = num_and_unit[i:]
    today = datetime.today()
    # print('unit:', unit)

    if unit.startswith("d"):
        time = today + relativedelta(days=-num)
    elif unit.startswith("h"):
        time = today + relativedelta(hours=-num)
    elif unit.startswith("mo"):
        time = today + relativedelta(months=-num)
    elif unit.startswith("w"):
        time = today + relativedelta(weeks=-num)
    elif unit.startswith("m"):
        time = today + relativedelta(minutes=-num)
    elif unit.startswith("y"):
        time = today + relativedelta(years=-num)
    abs_time = datetime.strftime(time, "%Y-%m-%d %H:%M")
    return abs_time


def _get_val(the_dict, *args):
    cur = the_dict
    for path in args:
        # print("the path", path)
        if not isinstance(cur, dict):
            return None
        if path not in cur:
            return None
        cur = cur[path]
    return cur


def _get_reaction_type_count(post, row):
    count_stats = _get_val(
        post, "socialDetail", "totalSocialActivityCounts", "reactionTypeCounts"
    )
    if count_stats is None:
        print("return none")
        return
    for count_stat in count_stats:
        row[count_stat["reactionType"].lower()] = count_stat["count"]


def _get_post_url(post, row):
    actions = _get_val(post, "updateMetadata", "updateActions", "actions")
    if actions is None or len(actions) < 2:
        return
    action = actions[1]
    if action["actionType"] != "SHARE_VIA":
        return None
    row["url"] = action["url"]


def _get_post_text(post, row):
    text = _get_val(post, "commentary", "text", "text")
    if text is None:
        row["text"] = "Found no text. Likely it is a repo."
        return
    text = text.replace("\n", " ")
    row["text"] = text


def _get_post_num_comments(post, row):
    num_comments = _get_val(
        post, "socialDetail", "totalSocialActivityCounts", "numComments"
    )
    row["comment"] = num_comments


def _get_post_time(post, row):
    # print('the post:', post)
    time_info = _get_val(post, "actor", "subDescription", "accessibilityText")
    # print('the time_info', time_info)

    abs_time = _get_abs_time(time_info)


    row["time_info"] = time_info
    row["abs_time"] = abs_time


def _get_row_val(row, key, default_val=""):
    return str(row[key]) if key in row else default_val


def _filter_data(rows, start_date, end_date):
    new_rows = []
    for row in rows:
        row_time = _get_row_val(row, "abs_time")
        row_time = row_time[:10]
        if not row_time:
            continue
        if start_date and row_time < start_date:
            continue
        if end_date and row_time > end_date:
            continue
        new_rows.append(row)
    return new_rows


def _write_to_csv(file_path, rows):
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    print("The analysis result is saved in", file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        columns = [
            "url",
            "abs_time",
            "time_info",
            "text",
            "comment",
            "like",
            "interest",
            "praise",
            "maybe",
            "appreciation",
        ]
        f.write("\t".join(columns))
        f.write("\n")
        for row in rows:
            vals = [_get_row_val(row, col) for col in columns]
            # print('the vals:', vals)
            line = "\t".join(vals)
            f.write(line)
            f.write("\n")


def get_linkedin_performance(
    target, email, password, post_count, start_date, end_date
):
    if start_date or end_date:
        print(
            "You have specified the start_date or end_date, we will try fetching as much as we can, and then filter by date..."
        )
        post_count = max(_MAX_POST_COUNT, post_count)
    api = Linkedin(email, password)
    target_user = api.get_profile(target)
    print("We will get TOP %d posts info for %s." % (post_count, target))
    posts = api.get_profile_posts(
        urn_id=target_user["profile_id"], post_count=post_count
    )
    if len(posts) > post_count:
        print(
            "There are %d posts retrieved, it is because we have to fetch 100 multiple posts."
            % len(posts)
        )
        posts = posts[:post_count]
    rows = [dict() for i in range(len(posts))]
    for i, post in enumerate(posts):
        _get_post_url(post, rows[i])
        _get_post_time(post, rows[i])
        _get_post_text(post, rows[i])
        _get_post_num_comments(post, rows[i])
        _get_reaction_type_count(post, rows[i])
    file_name = datetime.strftime(datetime.today(), "%Y%m%d-%H%M") + ".tsv"
    rows = _filter_data(rows, start_date, end_date)
    print("In total we get %d entries" % len(rows))
    _write_to_csv(_FILE_PATH + "/" + file_name, rows)


def main():
    parser = argparse.ArgumentParser(
        description="This app helps you to find your linkedin post performance."
    )
    parser.add_argument("--email", type=str, help="Your linkedin account email")
    parser.add_argument(
        "--password", type=str, help="Your linkedin account password"
    )
    parser.add_argument(
        "--post_num", type=int, help="How many posts should be processed"
    )
    parser.add_argument(
        "--linkedin_account",
        type=str,
        help="Which LinkedIn account are you interested in",
    )
    parser.add_argument(
        "--start_date",
        type=str,
        help="What's the start date that you are interested in?, format %Y-%m-%d",
    )
    parser.add_argument(
        "--end_date",
        type=str,
        help="What's the start date that you are interested in?, format %Y-%m-%d",
    )
    args = parser.parse_args()
    if args.email is None or args.password is None:
        secret = open("./secret.txt", "r")
        lines = secret.readlines()
        print("We read the secret from secret file :)")
        args.email = lines[0].split("#")[0].strip()
        args.password = lines[1].split("#")[0].strip()
        print(args.email, args.password)

    get_linkedin_performance(
        target=args.linkedin_account if args.linkedin_account else _DALIANA,
        email=args.email,
        password=args.password,
        post_count=args.post_num if args.post_num else _NORMAL_POST_COUNT,
        start_date=args.start_date,
        end_date=args.end_date,
    )


if __name__ == "__main__":
    main()
