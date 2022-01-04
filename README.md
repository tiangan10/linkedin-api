# Linkedin Performance Analyzer
This tool is built upon [tomquirk/linkedin-api](https://github.com/tomquirk/linkedin-api). It is used to analyze the performance of any linkedin account's posts.

## Installation
### Git clone
```shell
git clone https://github.com/tiangan10/linkedin-api.git
```

### Install python libs
The necessary libs are listed in the requirements file. After clone, please run the following command within the linkedin-api folder:

```
cd linkedin-api # skip if you are already in linkedin-api
pip3 install -r ./requirements.txt
```

## Usage
### Secret
The script requires a real linkedin account to run the analysis. You can send in the linkedin account info (--email, --password) via command. Alternatively, you can save the account information in a `secret.txt` file within linkedin-api filder.

Here is an example of the secret.txt file:
```
the.secret.email@host.com  # list the email string in the first line
the_linkedin_password	   # list the linkedin password here
```

## Run the command
```shell
# Get the most recent 100 posts
python3 linked_post_perf.py

# Specify the total number of posts to fetch
python3 linked_post_perf.py --post_num=<number of posts to be fetched, e.g. 30>

# Specify a date range to fetch the posts from. Note that you do not need to specify
# both the start date and the end date. For instance, you can specify start_date only
# to get all the posts posted after the given start_date.
python3 linked_post_perf.py --start_date=<yyyy-mm-dd> --end_date=yyyy-mm-dd>

```
Note: after running the command, the analysis result will be saved in your Documents file. You can find the output file from your terminal log. An example command output is as below:
```
We will get TOP 100 posts info for dalianaliu.
In total we get 100 entries
the file is /Users/tiangan/Documents/linkedin_api/data/20220103-17:04.tsv
```
