import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

class CalculatorPage(ttk.Frame):
    def __init__(self, parent, controller, initial_data=None):
        super().__init__(parent)
        self.controller = controller
        self.current_expression = ""

        page_frame = ttk.Frame(self, padding=20)
        page_frame.pack(fill=BOTH, expand=True)

        title_label = ttk.Label(page_frame, text="Kalkulator", font=("Helvetica", 20, "bold"), bootstyle=PRIMARY)
        title_label.pack(pady=15)

        # Display Entry
        self.display = ttk.Entry(page_frame, font=("Helvetica", 32), justify="right", bootstyle=LIGHT)
        self.display.pack(fill=X, padx=10, pady=10, ipady=15)

        # Button Frame
        button_frame = ttk.Frame(page_frame)
        button_frame.pack(pady=10)

        # Define buttons with their text, row, col, and bootstyle
        buttons_config = [
            ('C', 1, 0, DANGER), ('/', 1, 3, WARNING),
            ('7', 2, 0, SECONDARY), ('8', 2, 1, SECONDARY), ('9', 2, 2, SECONDARY), ('*', 2, 3, WARNING),
            ('4', 3, 0, SECONDARY), ('5', 3, 1, SECONDARY), ('6', 3, 2, SECONDARY), ('-', 3, 3, WARNING),
            ('1', 4, 0, SECONDARY), ('2', 4, 1, SECONDARY), ('3', 4, 2, SECONDARY), ('+', 4, 3, WARNING),
            ('0', 5, 0, SECONDARY), ('.', 5, 1, SECONDARY), ('=', 5, 2, SUCCESS)
        ]

        for (text, row, col, style) in buttons_config:
            command = lambda t=text: self.append_to_expression(t)
            if text == '=':
                command = self.calculate
            elif text == 'C':
                command = self.clear_display

            btn = ttk.Button(button_frame, text=text, bootstyle=style, command=command)
            if text == '=':
                btn.grid(row=row, column=col, columnspan=2, padx=5, pady=5, sticky="nsew", ipady=15)
            elif text == 'C':
                btn.grid(row=row, column=col, columnspan=3, padx=5, pady=5, sticky="nsew", ipady=15)
            else:
                btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew", ipady=15)

        # Configure grid weights for responsive buttons
        for i in range(4):
            button_frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            button_frame.grid_rowconfigure(i, weight=1)

        back_button = ttk.Button(page_frame, text="Kembali ke Home", command=lambda: controller.show_frame("HomePage"), bootstyle=SECONDARY)
        back_button.pack(pady=25)

    def append_to_expression(self, value):
        self.current_expression += str(value)
        self.display.delete(0, END)
        self.display.insert(0, self.current_expression)

    def clear_display(self):
        self.current_expression = ""
        self.display.delete(0, END)

    def calculate(self):
        try:
            result = str(eval(self.current_expression))
            self.display.delete(0, END)
            self.display.insert(0, result)
            self.current_expression = result
        except Exception as e:
            messagebox.showerror("Error Kalkulator", "Ekspresi tidak valid atau error: " + str(e), parent=self)
            self.current_expression = ""
            self.display.delete(0, END)
