# ghutils
Some GitHub utilities that I needed to write.

Make sure you have python3 and run (in the project root folder):

```
pip3 install -r requirements.txt
```

Now you should be able to run the script(s).

ghprmetrics: Pull Request Metrics
=================================

Get metrics for just the merged PRs, for the last 30 days, from repo named "foobar" of enterprise GitHub "mygithub.com",
using the provided GitHub token for authentication.

```
python ghprmetrics.py --enterprise=mygithub.com --merged --token=01234567890 --repos=^foobar$ --maxDays=30 --outputCSV=pr-metrics-30days.csv 
```

This will generate a CSV file "pr-metrics-30days.csv" which you can use to plot histograms, scatterplots, etc.
