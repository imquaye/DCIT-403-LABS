"""Lab 2 tools (the agent's actuators): a safe calculator and a Wikipedia lookup."""
import ast
import operator as op
from urllib.parse import quote

import requests

OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
       ast.Div: op.truediv, ast.USub: op.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in OPS:
        return OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Unsupported expression")


def calculator(expression: str) -> str:
    """Evaluate arithmetic safely with the ast module (never eval)."""
    try:
        expr = expression.replace(",", "")
        return str(_eval(ast.parse(expr, mode="eval").body))
    except Exception as e:
        return f"Error: {e}"


def _wiki_json(url, **kwargs):
    """Return a Wikipedia JSON object and an error message, if any."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "DCIT403-lab"},
                                **kwargs)
    except requests.RequestException as e:
        return None, f"Error: could not reach Wikipedia ({e})."
    if response.status_code == 429:
        return None, "Error: Wikipedia rate limited the request (HTTP 429)."
    if response.status_code != 200:
        return None, f"Error: Wikipedia returned HTTP {response.status_code}."
    try:
        payload = response.json()
    except ValueError:
        return None, "Error: Wikipedia returned invalid JSON."
    if not isinstance(payload, dict):
        return None, "Error: Wikipedia returned an unexpected response."
    return payload, ""


def wiki_lookup(title: str) -> str:
    """Return the first 800 characters of a Wikipedia page summary."""
    url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
           + quote(title.strip().replace(" ", "_"), safe=""))
    payload, error = _wiki_json(url)
    if error == "Error: Wikipedia returned HTTP 404.":
        return f"No Wikipedia page found for '{title}'."
    if error:
        return error
    extract = payload.get("extract", "")
    if not isinstance(extract, str):
        return "Error: Wikipedia returned an unexpected summary."
    extract = extract.strip()
    if len(extract) < 300:
        # A short summary may omit key facts such as a founding year.
        intro, error = _intro(title)
        if not (intro or extract):
            return error or f"No Wikipedia summary found for '{title}'."
        extract = intro or extract
    return extract[:800]


def _intro(title: str):
    """Return the plain-text introduction and an error message, if any."""
    payload, error = _wiki_json(
        "https://en.wikipedia.org/w/api.php",
        params={"action": "query", "prop": "extracts", "exintro": 1,
                "explaintext": 1, "redirects": 1, "format": "json",
                "titles": title.strip()},
    )
    if error:
        return "", error
    try:
        page = next(iter(payload["query"]["pages"].values()))
        extract = page.get("extract", "")
        return " ".join(extract.split()), ""
    except (KeyError, TypeError, AttributeError, StopIteration):
        return "", "Error: Wikipedia returned an unexpected introduction."


TOOLS = {"calculator": calculator, "wiki_lookup": wiki_lookup}


if __name__ == "__main__":
    # Step 2 checkpoint: test both tools directly before connecting the model.
    print("4*185 + 3*95 =", calculator("4*185 + 3*95"))
    print("1,200 - 1025 =", calculator("1,200 - 1025"))
    print("unsafe input  =", calculator("__import__('os')"))
    print("wiki:", wiki_lookup("Bono East Region")[:200])
    print("wiki missing:", wiki_lookup("Makola Flying Yam Festival"))
