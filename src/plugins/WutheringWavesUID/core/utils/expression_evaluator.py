# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/expression_evaluator.py
from typing import List
from lark import Lark, Transformer

# 适配修改：从 from utils.expression_ctx import ...
from .expression_ctx import ExpressionCtx, get_func_args, get_func_name

GRAMMAR = r"""
    ?value:
          | SIGNED_NUMBER -> num
          | ESCAPED_STRING -> str
          | "true" -> true_
          | "false" -> false_
          | "null" -> null_
          | "undefined" -> undefined_
          | func
          | NAME -> var

    ?func: NAME "(" [value ("," value)*] ")"

    ?atom: value

    ?product: atom (("*" | "/" | "%") atom)*
    ?sum: product (("+" | "-") product)*
    ?comparison: sum (("==" | "!=" | "<" | "<=" | ">" | ">=") sum)*
    ?logical_and: comparison ("&&" comparison)*
    ?logical_or: logical_and ("||" logical_and)*
    ?expr: logical_or ( "?" logical_or ":" logical_or )?

    %import common.CNAME -> NAME
    %import common.SIGNED_NUMBER
    %import common.ESCAPED_STRING
    %import common.WS
    %ignore WS
"""


class ExpressionTransformer(Transformer):
  def __init__(self, ctx: ExpressionCtx) -> None:
    super().__init__()
    self.ctx = ctx

  def num(self, args):
    return float(args[0])

  def str(self, args):
    return args[0][1:-1]

  def true_(self, args):
    return True

  def false_(self, args):
    return False

  def null_(self, args):
    return None

  def undefined_(self, args):
    return None

  def var(self, args):
    var_name = str(args[0])
    return self.ctx.get(var_name)

  def func(self, args):
    func_name = str(args[0])
    func_args = args[1:]
    func = self.ctx.get(func_name)
    if callable(func):
      return func(*func_args)
    return None

  def product(self, args):
    res = args[0]
    for i in range(1, len(args), 2):
      op = args[i]
      val = args[i + 1]
      if op == "*":
        res *= val
      elif op == "/":
        res /= val
      elif op == "%":
        res %= val
    return res

  def sum(self, args):
    res = args[0]
    for i in range(1, len(args), 2):
      op = args[i]
      val = args[i + 1]
      if op == "+":
        res += val
      elif op == "-":
        res -= val
    return res

  def comparison(self, args):
    res = args[0]
    for i in range(1, len(args), 2):
      op = args[i]
      val = args[i + 1]
      if op == "==":
        res = res == val
      elif op == "!=":
        res = res != val
      elif op == "<":
        res = res < val
      elif op == "<=":
        res = res <= val
      elif op == ">":
        res = res > val
      elif op == ">=":
        res = res >= val
    return res

  def logical_and(self, args):
    res = args[0]
    for i in range(1, len(args), 2):
      op = args[i]
      val = args[i + 1]
      if op == "&&":
        res = res and val
    return res

  def logical_or(self, args):
    res = args[0]
    for i in range(1, len(args), 2):
      op = args[i]
      val = args[i + 1]
      if op == "||":
        res = res or val
    return res

  def expr(self, args):
    if len(args) == 3:
      condition, true_val, false_val = args
      return true_val if condition else false_val
    return args[0]


class ExpressionEvaluator:
  def __init__(self) -> None:
    self.parser = Lark(GRAMMAR, start="expr")

  def eval(self, expr: str, ctx: ExpressionCtx):
    tree = self.parser.parse(expr)
    return ExpressionTransformer(ctx).transform(tree)


def get_all_funcs(expr: str) -> List[str]:
  funcs = set()
  for func in FUNC_PATTERN.findall(expr):
    funcs.add(func[0])
  return list(funcs)


def get_all_vars(expr: str) -> List[str]:
  vars = set()
  for var in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", expr):
    if var not in ("true", "false", "null", "undefined"):
      vars.add(var)

  # Exclude function names
  funcs = get_all_funcs(expr)
  vars = vars - set(funcs)

  return list(vars)


if __name__ == "__main__":
  evaluator = ExpressionEvaluator()
  ctx = ExpressionCtx(
      {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5,
        "f": 6,
        "g": 7,
        "h": 8,
        "i": 9,
        "j": 10,
        "k": 11,
        "l": 12,
        "m": 13,
        "n": 14,
        "o": 15,
        "p": 16,
        "q": 17,
        "r": 18,
        "s": 19,
        "t": 20,
        "u": 21,
        "v": 22,
        "w": 23,
        "x": 24,
        "y": 25,
        "z": 26,
        "max": max,
        "min": min,
      }
  )
  expr = "a + b * c - d / e % f + g - h + i * j - k / l % m + n - o + p * q - r / s % t + u - v + w * x - y / z"
  expr = "a + b * c"
  expr = "a + b > c ? d : e"
  expr = "a > b && c > d || e > f"
  expr = "max(a, b, c)"
  expr = "a + b * max(c, d)"
  print(evaluator.eval(expr, ctx))