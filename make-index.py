import re
import os
import json

def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

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

print("<!DOCTYPE html>")
print("<html>")
print("<head>")
print("<title>Archived PR index</title>")
print("<meta charset='utf-8'/>")
print("<link rel='stylesheet' href='/css/prindex.css'/>")
print("</head>")
print("<body>")

print("<p>Index of closed PRs. Link on PR number takes you to the GitHub PR page.")
print("Link on PR title takes you to the index of specifications in this build.")
print("If change markup is detected, the specifications that are changed by this")
print("PR are listed below the PR title.")
print("</p>")

for pr in prs:
    if not pr in issues:
        continue

    print("<div class='pr'>")
    print("<div class='headline'>")
    print(f"<span class='title'><a href='https://github.com/qt4cg/qtspecs/pull/{pr}'>{pr}</a>")
    print(f"<a href='pr/{pr}/'>{escape(issues[pr]['title'])}</a>")
    print("</span>")
    print("<span class='labels'>")
    for label in issues[pr]["labels"]:
        print(f"<span>{label['name']}</span>")
    print("</span>")
    print("</div>")
    print("<ul>")

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
                    print(f"<li><a href='{file}/Overview.html'>{title}</a>")
                    print(f" (<a href='{file}/autodiff.html'>diffs</a>)")
                    print("</li>")

    print("</ul>")
    print("</div>")

print("</body>")
print("</html>")
