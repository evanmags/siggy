import base64
import re
from pathlib import Path
from typing import List, Tuple, TypedDict
import htmlmin

from jinja2 import Environment, FileSystemLoader, select_autoescape
import requests

TREES_URL = "https://api.github.com/repos/evanmags/siggy/git/trees/main"
ROOT_TEMPLATES_PATH = "siggy/templates"
TEMPLATE_NAME_REGEX = re.compile(r"(\d{6}).html$")
LOCAL_TEMPLATES_PATH = Path(__file__).parent / "templates"


class TreeObj(TypedDict):
    path: str
    mode: str
    type: str
    sha: str
    size: int
    url: str


class File(TypedDict):
    sha: str
    node_id: str
    size: int
    url: str
    content: str
    encoding: str


Tree = List[TreeObj]


def pull_most_recent_template():
    response = requests.get(TREES_URL, params=dict(recursive=1))
    response.raise_for_status()

    tree: Tree = response.json().get("tree", [])
    timestamp, tree_obj = find_most_recent_version_in_tree(tree)

    content = get_file_content(tree_obj)
    template_name = f"{timestamp}.html"

    with (LOCAL_TEMPLATES_PATH / template_name).open("w+") as file:
        file.write(content)

    return template_name


def find_most_recent_version_in_tree(tree: Tree) -> Tuple[int, TreeObj]:
    most_recent: Tuple[int, TreeObj] = (0, {})
    for obj in tree:
        if (
            (path := obj["path"])  # object has a path
            and path.startswith(ROOT_TEMPLATES_PATH)  # object path in the templates dir
            and obj["type"] == "blob"  # object is correct type
            and (match := TEMPLATE_NAME_REGEX.search(path))  # path is timestamp
            and (ts := int(match.groups(0)[0])) > most_recent[0]  # ts is most recent
        ):
            most_recent = (ts, obj)

    return most_recent


def get_file_content(tree_obj: TreeObj) -> str:
    response = requests.get(tree_obj["url"])
    response.raise_for_status()

    return base64.decodebytes(response.json()["content"].encode()).decode("utf-8")


def load_template(name: str, role: str, email: str, phone: str):
    template_name = pull_most_recent_template()

    loader = FileSystemLoader(LOCAL_TEMPLATES_PATH)

    env = Environment(loader=loader, autoescape=select_autoescape())
    template = env.get_template(template_name)

    return htmlmin.minify(
        template.render(name=name, role=role, email=email, phone=phone)
    )
