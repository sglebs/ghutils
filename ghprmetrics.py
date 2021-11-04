"""ghprmetrics (GitHub PR Metrics).

Usage:
  gh-metrics      --token=<token> \r\n \
                  [--outputCSV=<outputCSV>]  \r\n \
                  [--repos=<repoRegex>]   \r\n \
                  [--skipTitles=<titleRegex>]   \r\n \
                  [--creator=<creatorRegex>]   \r\n \
                  [--state=<state>]   \r\n \
                  [--enterprise=<enterprise>] \r\n \
                  [--maxCount=<maxCount>] \r\n \
                  [--maxDays=<maxDays>] \r\n \
                  [--merged]

Options:
  --token=<token>                 GitHub token to use
  --repos=<repoRegex>             Regex to match repos you want to check  [default: .*]
  --skipTitles=<titleRegex>       Regex to match PR titles you want to skip - release, for example  [default: ^$]
  --state=<state>                 State of teh PRs  [default: closed]
  --enterprise=<enterprise>       Enterprise account to use, as in https://{hostname}/api/v3 [default: api.github.com]
  -m, --merged                    If you want to traverse only merged PRs
  --maxCount=<maxCount>           Maximum number of PRs to traverse per repo. Limits the output [default: 4096]
  --maxDays=<maxDays>             Maximum PR age in days. Limits the output [default: 120]
  --creator=<creatorRegex>        Regex to match user login who created the PR. Skip non-matches [default: .*]
  --outputCSV=<outputCSV>         Output CSV file path with the PR metrics [default: pr-metrics.csv]

Author:
  Marcio Marchini (marcio@BetterDeveloper.net)

"""
from github import Github
import datetime
import csv
from docopt import docopt
import re


def prs_with_metrics_iterator(token, enterprise, repo_regex, title_regex, state, only_merged, max_count, max_days, creator_regex):
    gh = Github(base_url="https://%s/api/v3" % enterprise, login_or_token=token)
    for repo in gh.get_user().get_repos():
        total_count_of_prs_traversed = 0
        if not re.search(repo_regex, repo.name):
            continue
        for pull in repo.get_pulls(state=state):
            if only_merged and not pull.merged:
                continue  # skip
            if not re.search(creator_regex, pull.user.login):
                continue  # skip
            title = pull.title
            if re.search(title_regex, title):
                continue  # skip
            if total_count_of_prs_traversed >= max_count:  # enough work, we can abort
                break
            creation_date = pull.created_at
            pr_age_in_days = (datetime.datetime.now() - creation_date).days
            if pr_age_in_days > max_days:  # enough work, we can abort
                break
            review_request_count = 0
            for review_request_users in pull.get_review_requests():
                review_request_count += 1
            first_review = None
            last_review = None
            review_count = 0
            for review in pull.get_reviews():
                review_count += 1
                if first_review is None:
                    first_review = review
                last_review = review
            wait_time_for_first_review = datetime.timedelta() if first_review is None else first_review.submitted_at - creation_date
            wait_time_for_last_review = datetime.timedelta() if first_review is None else last_review.submitted_at - creation_date
            total_time_between_reviews = wait_time_for_last_review - wait_time_for_first_review
            yield [repo.name, pull.id, title, pull.state, creation_date, pull.user.login, pull.last_modified,
                    pull.merged, pull.merged_at, "-" if pull.merged_by is None else pull.merged_by.login,
                    pull.changed_files, pull.comments, pull.commits, pull.deletions,
                    review_request_count, review_count, int(wait_time_for_first_review.total_seconds() / 60),
                   int(wait_time_for_last_review.total_seconds() / 60),
                   int(total_time_between_reviews.total_seconds() / 60)]

            total_count_of_prs_traversed += 1


def main():
    start_time = datetime.datetime.now()
    arguments = docopt(__doc__, version="0.0.1")
    print("\r\n====== ghprmetrics ==========")
    print(arguments)
    csv_file = open(arguments["--outputCSV"], 'w')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Repository", "PR id", "PR title", "PR state", "PR Creation Date", "PR Creator",
                         "PR Last Modified", "PR is merged", "PR Date Merged", "PR Merged By", "Count Files Changed",
                         "Count Comments", "Count Commits", "Count Deletions", "Count Review Requests", "Count Reviews",
                         "Minutes to First Review", "Minutes to Last Review", "Minutes Between Reviews"])
    for pr_data in  \
            prs_with_metrics_iterator(arguments["--token"], arguments["--enterprise"],
                                      arguments["--repos"], arguments["--skipTitles"],
                                      arguments["--state"], arguments["--merged"],
                                      int(arguments["--maxCount"]), int(arguments["--maxDays"]),
                                      arguments["--creator"]):
        csv_writer.writerow(pr_data)
    csv_file.close()
    print("")
    end_time = datetime.datetime.now()
    print("\r\n--------------------------------------------------")
    print("Started : %s" % str(start_time))
    print("Finished: %s" % str(end_time))
    print("--------------------------------------------------")


if __name__ == '__main__':
    main()
