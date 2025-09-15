import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter.font

class ThemePage(ttk.Frame):
    def __init__(self, parent, controller, initial_data=None):
        super().__init__(parent)
        self.controller = controller
        
        back_button_frame = ttk.Frame(self)
        back_button_frame.pack(side="top", fill="x", padx=10, pady=10, anchor="nw")

        back_button_top = ttk.Button(back_button_frame, text="Kembali", command=lambda: controller.show_frame("HomePage"), bootstyle=SECONDARY)
        back_button_top.pack(side="left")

        page_frame = ttk.Frame(self, padding=20)
        page_frame.pack(expand=True)

        title = ttk.Label(page_frame, text="Pilih Tema Aplikasi", font=("Helvetica", 18, "bold"), bootstyle=PRIMARY)
        title.pack(pady=20)

        theme_frame = ttk.Frame(page_frame)
        theme_frame.pack(pady=10)

        themes = ["superhero", "darkly", "cyborg", "vapor", "litera", "minty", "sandstone", "cosmo"]
        for i, theme_name in enumerate(themes):
            bootstyle = DARK if theme_name in ["superhero", "darkly", "cyborg", "vapor"] else LIGHT
            btn = ttk.Button(theme_frame, text=theme_name.capitalize(), bootstyle=(bootstyle, OUTLINE), command=lambda t=theme_name: controller.change_theme(t))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew", ipady=5)

        # --- Bagian Pemilihan Font ---
        font_title = ttk.Label(page_frame, text="Pilih Font Aplikasi", font=("Helvetica", 18, "bold"), bootstyle=PRIMARY)
        font_title.pack(pady=20)

        font_frame = ttk.Frame(page_frame)
        font_frame.pack(pady=10)

        fonts = [
            "Didot", "Bodoni", "Baskerville", "Garamond", "Times New Roman", 
            "New York", "Grafik ITC Lubalin", "Gabriela Stencil", "Arial", "Helvetica"
        ]

        for i, font_name in enumerate(fonts):
            btn = ttk.Button(font_frame, text=font_name, bootstyle=(INFO, OUTLINE), command=lambda f=font_name: controller.change_font(f))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew", ipady=5)

        def show_available_fonts():
            available_fonts = sorted(list(tkinter.font.families()))
            messagebox.showinfo("Available Fonts", "\n".join(available_fonts))

        show_fonts_button = ttk.Button(page_frame, text="Show Available Fonts", command=show_available_fonts, bootstyle=(INFO, OUTLINE))
        show_fonts_button.pack(pady=10)

        back_button = ttk.Button(page_frame, text="Kembali ke Home", command=lambda: controller.show_frame("HomePage"), bootstyle=SECONDARY)
        back_button.pack(pady=30)
