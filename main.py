import ast
import math
import operator
from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView

BIN_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
           ast.Mult: operator.mul, ast.Div: operator.truediv,
           ast.Pow: operator.pow, ast.Mod: operator.mod}
UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
FUNCTIONS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "log": math.log10, "ln": math.log, "abs": abs,
    "floor": math.floor, "ceil": math.ceil, "exp": math.exp
}
CONSTANTS = {"pi": math.pi, "e": math.e}

def calculate_expression(expression, degrees=True):
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
    tree = ast.parse(expression, mode="eval")

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            return BIN_OPS[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](visit(node.operand))
        if isinstance(node, ast.Name) and node.id in CONSTANTS:
            return CONSTANTS[node.id]
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in FUNCTIONS or len(node.args) != 1 or node.keywords:
                raise ValueError("Unsupported function")
            value = visit(node.args[0])
            if degrees and name in ("sin", "cos", "tan"):
                value = math.radians(value)
            result = FUNCTIONS[name](value)
            if degrees and name in ("asin", "acos", "atan"):
                result = math.degrees(result)
            return result
        raise ValueError("Invalid expression")

    result = visit(tree)
    if isinstance(result, complex):
        return str(result)
    if not math.isfinite(float(result)):
        raise ValueError("Non-finite result")
    if isinstance(result, float) and result.is_integer():
        return str(int(result))
    return str(round(result, 12))

class Calculator(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(8), spacing=dp(6), **kwargs)
        self.expression = ""
        self.history = []
        self.degrees = True
        self.dark = True

        self.display = Label(text="0", font_size="34sp", halign="right",
                             valign="middle", size_hint_y=None, height=dp(105))
        self.display.bind(size=lambda *_: setattr(self.display, "text_size", self.display.size))
        self.add_widget(self.display)

        toolbar = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(5))
        self.angle_button = self.add_btn("DEG", self.toggle_angle, toolbar=True)
        toolbar.add_widget(self.angle_button)
        toolbar.add_widget(self.add_btn("HISTORY", self.show_history, toolbar=True))
        toolbar.add_widget(self.add_btn("THEME", self.toggle_theme, toolbar=True))
        self.add_widget(toolbar)

        scroll = ScrollView()
        self.grid = GridLayout(cols=4, spacing=dp(5), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        self.add_widget(scroll)

        rows = [
            ["AC", "DEL", "(", ")"],
            ["sin(", "cos(", "tan(", "÷"],
            ["asin(", "acos(", "atan(", "×"],
            ["7", "8", "9", "−"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "^"],
            ["0", ".", "π", "e"],
            ["√", "log(", "ln(", "exp("],
            ["abs(", "floor(", "ceil(", "%"],
            ["=", "x²", "±", "÷"]
        ]
        for row in rows:
            for key in row:
                self.grid.add_widget(self.add_btn(key, lambda k=key: self.press(k)))
        self.apply_theme()

    def add_btn(self, text, callback, toolbar=False):
        button = Button(text=text, font_size="16sp" if toolbar else "19sp",
                        size_hint_y=None, height=dp(44) if toolbar else dp(58),
                        background_normal="", background_down="")
        button.bind(on_release=lambda *_: callback())
        return button

    def press(self, key):
        if key == "AC":
            self.expression = ""
        elif key == "DEL":
            self.expression = self.expression[:-1]
        elif key == "=":
            self.solve()
            return
        elif key == "π":
            self.expression += "pi"
        elif key == "√":
            self.expression += "sqrt("
        elif key == "x²":
            self.expression += "**2"
        elif key == "±":
            if self.expression:
                self.expression = f"-({self.expression})"
        elif key == "%":
            self.expression += "/100"
        elif key == "×":
            self.expression += "*"
        elif key == "÷":
            self.expression += "/"
        elif key == "−":
            self.expression += "-"
        else:
            self.expression += key
        self.refresh()

    def refresh(self):
        self.display.text = self.expression or "0"

    def solve(self):
        try:
            result = calculate_expression(self.expression, self.degrees)
            self.history.insert(0, f"{self.expression} = {result}")
            self.expression = result
            self.refresh()
        except ZeroDivisionError:
            self.display.text = "Cannot divide by zero"
        except Exception:
            self.display.text = "Invalid expression"

    def toggle_angle(self):
        self.degrees = not self.degrees
        self.angle_button.text = "DEG" if self.degrees else "RAD"

    def show_history(self):
        body = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        text = Label(text="\n".join(self.history[:40]) or "No calculations yet",
                     halign="left", valign="top")
        text.bind(size=lambda *_: setattr(text, "text_size", text.size))
        body.add_widget(text)
        popup = Popup(title="History", content=body, size_hint=(0.9, 0.75))
        body.add_widget(self.add_btn("CLOSE", popup.dismiss, toolbar=True))
        popup.open()

    def toggle_theme(self):
        self.dark = not self.dark
        self.apply_theme()

    def apply_theme(self):
        if self.dark:
            Window.clearcolor = (0.035, 0.045, 0.07, 1)
            self.display.color = (1, 1, 1, 1)
            normal, special, accent = (0.12, 0.15, 0.21, 1), (0.16, 0.34, 0.55, 1), (0.08, 0.55, 0.43, 1)
            foreground = (1, 1, 1, 1)
        else:
            Window.clearcolor = (0.94, 0.95, 0.97, 1)
            self.display.color = (0.08, 0.10, 0.14, 1)
            normal, special, accent = (0.82, 0.85, 0.89, 1), (0.55, 0.70, 0.88, 1), (0.20, 0.65, 0.48, 1)
            foreground = (0.05, 0.07, 0.10, 1)
        for button in self.grid.children:
            button.background_color = accent if button.text == "=" else (
                special if button.text in ("AC", "DEL", "+", "−", "×", "÷", "^") else normal)
            button.color = foreground
        for button in self.children[1].children:
            button.background_color = special
            button.color = foreground

class UltimateCalculatorApp(App):
    title = "Ultimate Calculator"
    def build(self):
        return Calculator()

if __name__ == "__main__":
    UltimateCalculatorApp().run()
