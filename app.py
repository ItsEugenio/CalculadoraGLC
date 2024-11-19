from flask import Flask, render_template, request, jsonify
import lark

# Gramática de la calculadora (GLC)
GRAMMAR = """
    ?start: expr
    ?expr: term
         | expr "+" term   -> suma
         | expr "-" term   -> resta
    ?term: factor
         | term "*" factor -> mult
         | term "/" factor -> divi
    ?factor: NUMBER        -> number
          | "(" expr ")"
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

# Parser
parser = lark.Lark(GRAMMAR, parser="lalr", transformer=None)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None
    tree_data = None
    if request.method == "POST":
        expression = request.form.get("expression")
        try:
            tree = parser.parse(expression)
            result = eval_expression(tree)
            tree_data = tree_to_dict(tree)
        except ZeroDivisionError as zde:
            result = str(zde)
        except Exception as e:
            result = f"Error: {e}"

    return render_template("index.html", result=result, tree_data=tree_data)


def eval_expression(tree):
    """Evalúa el árbol sintáctico."""
    if tree.data == "number":
        return float(tree.children[0])
    elif tree.data == "suma":
        return eval_expression(tree.children[0]) + eval_expression(tree.children[1])
    elif tree.data == "resta":
        return eval_expression(tree.children[0]) - eval_expression(tree.children[1])
    elif tree.data == "mult":
        return eval_expression(tree.children[0]) * eval_expression(tree.children[1])
    elif tree.data == "divi":
        divisor = eval_expression(tree.children[1])
        if divisor == 0:
            raise ZeroDivisionError("No se puede dividir entre 0")
        return eval_expression(tree.children[0]) / divisor


def tree_to_dict(tree):
    """Convierte un árbol de Lark a una estructura de diccionario."""
    node = {
        "name": tree.data,
        "children": [tree_to_dict(child) if isinstance(child, lark.Tree) else {"name": child} for child in tree.children]
    }
    return node


if __name__ == "__main__":
    app.run(debug=True)
