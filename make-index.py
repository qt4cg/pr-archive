import re
import os
import sys
import json

def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def output_html(filename, last_year, year, prs_by_date):
    with open(filename, "w") as html:
        print("<!DOCTYPE html>", file=html)
        print("<html>", file=html)
        print("<head>", file=html)
        print(f"<title>Archived PR index for {year}</title>", file=html)
        print("<meta charset='utf-8'/>", file=html)
        print("<link rel='stylesheet' href='/css/prindex.css'/>", file=html)
        print("</head>", file=html)
        print("<body>", file=html)

        print("<p class='years'>", file=html)
        for y in range(last_year, 2021, -1):
            if y == last_year:
                filename = "index.html"
            else:
                filename = f"{y}.html"

            if y == 2022:
                sep = ""
            else:
                sep = ", "

            if y == year:
                print(f"<span>{y}</span>{sep}", file=html)
            else:
                print(f"<a href='{filename}'>{y}</a>{sep}", file=html)
        print("</p>", file=html)

        print(f"<p>Index of PRs closed in {year}. Link on PR number takes you to the GitHub PR page.", file=html)
        print("Link on PR title takes you to the index of specifications in this build.", file=html)
        print("If change markup is detected, the specifications that are changed by this", file=html)
        print("PR are listed below the PR title.", file=html)
        print("</p>", file=html)

        dates = set()
        for date in prs_by_date:
            dates.add(date)

        dates = reversed(sorted(dates))

        print("<dl>", file=html)
        for date in dates:
            print(f"<dt>Closed {date}</dt>\n<dd>", file=html)
            prs = reversed(sorted(prs_by_date[date]))

            for pr in prs:
                print("<div class='pr'>", file=html)
                print("<div class='headline'>", file=html)
                print(f"<span class='title'>PR <a href='https://github.com/qt4cg/qtspecs/pull/{pr}'>#{pr}</a>: ", file=html)
                print(f"<a href='pr/{pr}/index.html'>{escape(issues[pr]['title'])}</a>", file=html)
                print("</span>", file=html)
                print("<span class='labels'>", file=html)
                for label in issues[pr]["labels"]:
                    print(f"<span>{label['name']}</span>", file=html)
                print("</span>", file=html)
                print("</div>", file=html)

                print("<ul>", file=html)
                for name in os.listdir(f"pr/{pr}"):
                    file = f"pr/{pr}/{name}"
                    autodiff = f"{file}/autodiff.html"
                    if os.path.isdir(file) and os.path.isfile(autodiff):
                        with open(f"{file}/autodiff.html") as diff:
                            delta_old = 0
                            delta_new = 0
                            title = None
                            for line in diff.readlines():
                                delta_old += line.count("deltaxml-old")
                                delta_new += line.count("deltaxml-new")
                                if not title and "<title>" in line:
                                    title = re.sub(r"^.*<title>", "", line)
                                    title = re.sub(r"</title>.*$", "", title).strip()

                            #print(f"<li>{autodiff}, {delta_old+delta_new}</li>")

                            if not title:
                                title = name
                            if (delta_old + delta_new > 5):
                                print(f"<li><a href='{file}/Overview.html'>{title}</a>", file=html)
                                print(f" (<a href='{file}/autodiff.html'>diffs</a>)", file=html)
                                print("</li>", file=html)
                print("</ul>", file=html)
                print("</div>", file=html)
            print("</dd>", file=html)
        print("</dl>", file=html)

        print("</body>", file=html)
        print("</html>", file=html)

with open("qtspecs-issues.json") as data:
    array = json.load(data)
    issues = {}
    for item in array:
        issues[item["number"]] = item

prs = []
for file in os.listdir("pr"):
    if os.path.isdir("pr/" + file):
        try:
            prs.append(int(file))
        except ValueError:
            pass

prs = reversed(sorted(prs))

prs_by_date = {}
years = set()

for pr in prs:
    if not pr in issues:
        continue
    closed = issues[pr]['closed_at'][0:10]
    if closed in prs_by_date:
        prs_by_date[closed].append(pr)
    else:
        years.add(closed[0:4])
        prs_by_date[closed] = [pr]

years = reversed(sorted(years))
last_year = None

for year in years:
    if not last_year:
        last_year = int(year)
        filename = "index.html"
    else:
        filename = f"{year}.html"

    year_by_date = {}
    for date in prs_by_date:
        if date[0:4] == year:
            year_by_date[date] = prs_by_date[date]

    print(f"Writing {filename}...")
    output_html(filename, last_year, year, year_by_date)
