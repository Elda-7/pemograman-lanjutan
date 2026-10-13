import ast
import operator
import tkinter as tk


OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def evaluate(expression):
    """Evaluate arithmetic expressions without executing arbitrary Python code."""
    tree = ast.parse(expression, mode="eval")

    def calculate(node):
        if isinstance(node, ast.Expression):
            return calculate(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](
                calculate(node.left), calculate(node.right)
            )
        if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
            return OPERATORS[type(node.op)](calculate(node.operand))
        raise ValueError("Ekspresi tidak valid")

    return calculate(tree)


class Kalkulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Kalkulator")
        self.root.geometry("340x490")
        self.root.minsize(300, 430)
        self.root.configure(bg="#151922")
        self.root.resizable(True, True)

        self.expression = ""
        self.just_calculated = False
        self.display = tk.StringVar(value="0")

        self._build_ui()
        self.root.bind("<Key>", self._on_key)

    def _build_ui(self):
        container = tk.Frame(self.root, bg="#151922", padx=18, pady=18)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="KALKULATOR",
            bg="#151922",
            fg="#9ba5b4",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 12))

        display = tk.Entry(
            container,
            textvariable=self.display,
            state="readonly",
            readonlybackground="#202633",
            fg="#f4f6fa",
            insertbackground="#f4f6fa",
            font=("Segoe UI", 28),
            justify="right",
            relief="flat",
            bd=0,
        )
        display.pack(fill="x", ipady=18, pady=(0, 16))

        buttons = [
            ("C", "⌫", "÷", "×"),
            ("7", "8", "9", "−"),
            ("4", "5", "6", "+"),
            ("1", "2", "3", "="),
            ("±", "0", "."),
        ]
        grid = tk.Frame(container, bg="#151922")
        grid.pack(fill="both", expand=True)
        for row in range(5):
            grid.rowconfigure(row, weight=1)
        for column in range(4):
            grid.columnconfigure(column, weight=1)

        for row, labels in enumerate(buttons):
            for column, label in enumerate(labels):
                is_operator = label in ("÷", "×", "−", "+", "=")
                is_action = label in ("C", "⌫", "±")
                background = (
                    "#5268e8" if label == "=" else
                    "#30394a" if is_operator else
                    "#252c39" if is_action else
                    "#202633"
                )
                button = tk.Button(
                    grid,
                    text=label,
                    command=lambda value=label: self._press(value),
                    bg=background,
                    fg="#ffffff",
                    activebackground="#6579f0" if label == "=" else "#3b465a",
                    activeforeground="#ffffff",
                    font=("Segoe UI", 16, "bold" if is_operator else "normal"),
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    takefocus=False,
                )
                button.grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=4,
                    pady=4,
                    rowspan=2 if label == "=" else 1,
                )

    def _press(self, key):
        if key == "C":
            self.expression = ""
            self.just_calculated = False
            self._show("0")
        elif key == "⌫":
            self.expression = self.expression[:-1]
            self.just_calculated = False
            self._show(self.expression.replace("*", "×").replace("/", "÷") or "0")
        elif key == "=":
            self._calculate()
        elif key == "±":
            self._toggle_sign()
        elif key in ("+", "−", "×", "÷"):
            self._append_operator({ "−": "-", "×": "*", "÷": "/" }[key])
        elif key == ".":
            self._append_decimal()
        elif key.isdigit():
            if self.just_calculated:
                self.expression = ""
                self.just_calculated = False
            self.expression += key
            self._show(self.expression)

    def _append_operator(self, operator_symbol):
        if not self.expression:
            if operator_symbol == "-":
                self.expression = "-"
                self._show("−")
            return
        if self.expression[-1] in "+-*/":
            self.expression = self.expression[:-1]
        self.expression += operator_symbol
        self.just_calculated = False
        self._show(self.expression.replace("*", "×").replace("/", "÷").replace("-", "−"))

    def _append_decimal(self):
        if self.just_calculated:
            self.expression = ""
            self.just_calculated = False
        current_number = self.expression.replace("+", " ").replace("-", " ")
        current_number = current_number.replace("*", " ").replace("/", " ").split()
        if "." not in (current_number[-1] if current_number else ""):
            if not self.expression or self.expression[-1] in "+-*/":
                self.expression += "0"
            self.expression += "."
            self._show(self.expression)

    def _toggle_sign(self):
        if not self.expression:
            self.expression = "-"
        else:
            start = len(self.expression)
            while start > 0 and (
                self.expression[start - 1].isdigit() or self.expression[start - 1] == "."
            ):
                start -= 1
            if start == len(self.expression):
                return
            has_unary_minus = (
                start > 0
                and self.expression[start - 1] == "-"
                and (start == 1 or self.expression[start - 2] in "+-*/")
            )
            if has_unary_minus:
                self.expression = self.expression[:start - 1] + self.expression[start:]
            else:
                self.expression = self.expression[:start] + "-" + self.expression[start:]
        self.just_calculated = False
        self._show(
            self.expression.replace("*", "×").replace("/", "÷").replace("-", "−")
        )

    def _calculate(self):
        if not self.expression:
            return
        try:
            if len(self.expression) > 120:
                raise ValueError("Ekspresi terlalu panjang")
            result = evaluate(self.expression)
            if isinstance(result, float):
                if not (float("-inf") < result < float("inf")):
                    raise ValueError("Hasil tidak valid")
                result = round(result, 10)
                if result.is_integer():
                    result = int(result)
            self.expression = str(result)
            self.just_calculated = True
            self._show(self.expression)
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            self.expression = ""
            self.just_calculated = False
            self._show("Error")

    def _show(self, value):
        self.display.set(value.replace("*", "×").replace("/", "÷").replace("-", "−"))

    def _on_key(self, event):
        if event.char.isdigit():
            self._press(event.char)
        elif event.char == "." or event.char == ",":
            self._press(".")
        elif event.char in "+-*/":
            self._append_operator(event.char)
        elif event.keysym in ("Return", "KP_Enter"):
            self._calculate()
        elif event.keysym == "BackSpace":
            self._press("⌫")
        elif event.keysym == "Escape":
            self._press("C")


if __name__ == "__main__":
    window = tk.Tk()
    Kalkulator(window)
    window.mainloop()
