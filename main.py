import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
import json 
import os 
from data_manager import load_app_data, save_app_data 

# Impor halaman-halaman terpisah
from shopping_list_page import ShoppingListPage
from salary_tracker_page import SalaryTrackerPage
from theme_page import ThemePage
from calculator_page import CalculatorPage 


class FinancialApp(ttk.Window):
    def __init__(self):
        
        self.app_data = load_app_data()
        super().__init__(themename=self.app_data.get("theme", "superhero"))
        
        self.title("Manajemen Keuangan")
        self.geometry("950x700")

        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage, ShoppingListPage, SalaryTrackerPage, ThemePage, CalculatorPage): 
            page_name = F.__name__
            
            frame = F(parent=container, controller=self, initial_data=self.app_data)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Terapkan font yang tersimpan saat startup
        self.apply_font(self.app_data.get("font", "Arial")) 

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def change_theme(self, theme_name):
        self.style.theme_use(theme_name)
        self.app_data["theme"] = theme_name
        
        save_app_data(self.app_data)

    def change_font(self, font_name):
        self.app_data["font"] = font_name
        self.apply_font(font_name)
        
        save_app_data(self.app_data)

    def apply_font(self, font_name):
        
        self.style.configure(".", font=(font_name, 10)) 
        self.style.configure("TLabel", font=(font_name, 10)) 
        self.style.configure("TButton", font=(font_name, 10)) 
        self.style.configure("TEntry", font=(font_name, 10)) 
        self.style.configure("Treeview.Heading", font=(font_name, 10, "bold")) 
        self.style.configure("Treeview", font=(font_name, 10)) 

        
        if "HomePage" in self.frames:
            home_page_label = self.frames["HomePage"].children["center_frame"].children["label"]
            home_page_label.config(font=(font_name, 28, "bold"))
        
        
        for page_name in ["ShoppingListPage", "SalaryTrackerPage", "ThemePage", "CalculatorPage"]:
            if page_name in self.frames:
                
                pass 


    

    def on_closing(self):
        
        
        self.app_data["shopping_list"] = self.frames["ShoppingListPage"].get_data()
        
        
        salary_data_from_page = self.frames["SalaryTrackerPage"].get_data()
        self.app_data["salary_data"]["employees"] = salary_data_from_page["employees"]
        self.app_data["salary_data"]["all_time"] = salary_data_from_page["all_time"]


        save_app_data(self.app_data) 
        self.destroy()

class HomePage(ttk.Frame):
    def __init__(self, parent, controller, initial_data=None):
        super().__init__(parent)
        self.controller = controller
        center_frame = ttk.Frame(self, name="center_frame") 
        center_frame.pack(expand=True)
        
        label = ttk.Label(center_frame, text="Pencatat Keuangan Wulandari Dekorasi", font=("Arial", 28, "bold"), bootstyle=PRIMARY, name="label")
        label.pack(pady=25)
        btn1 = ttk.Button(center_frame, text="Daftar Belanja", command=lambda: controller.show_frame("ShoppingListPage"), bootstyle=(SUCCESS, OUTLINE), width=25)
        btn1.pack(pady=15, ipady=10)
        btn2 = ttk.Button(center_frame, text="Pencatat Gaji", command=lambda: controller.show_frame("SalaryTrackerPage"), bootstyle=(SUCCESS, OUTLINE), width=25)
        btn2.pack(pady=15, ipady=10)
        btn_calc = ttk.Button(center_frame, text="Kalkulator", command=lambda: controller.show_frame("CalculatorPage"), bootstyle=(INFO, OUTLINE), width=25) 
        btn_calc.pack(pady=15, ipady=10)
        btn3 = ttk.Button(center_frame, text="Tema", command=lambda: controller.show_frame("ThemePage"), bootstyle=(INFO, OUTLINE), width=25)
        btn3.pack(pady=15, ipady=10)
        btn4 = ttk.Button(center_frame, text="Exit", command=controller.on_closing, bootstyle=(DANGER, OUTLINE), width=25)
        btn4.pack(pady=25, ipady=10)

if __name__ == "__main__":
    app = FinancialApp()
    app.mainloop()