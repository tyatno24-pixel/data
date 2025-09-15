import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

class SalaryTrackerPage(ttk.Frame):
    def __init__(self, parent, controller, initial_data=None):
        super().__init__(parent)
        self.controller = controller
        self.employee_data = {}
        self.all_time_salary_data = initial_data.get("salary_data", {}).get("all_time", {})
        self.day_columns = ["#3", "#4", "#5", "#6", "#7", "#8", "#9"]
        self.work_states = ["Libur", "Setengah Hari", "1 Hari Full"]
        self.state_multipliers = {"Libur": 0, "Setengah Hari": 0.5, "1 Hari Full": 1}

        page_frame = ttk.Frame(self, padding=10)
        page_frame.pack(fill=BOTH, expand=True)
        title_label = ttk.Label(page_frame, text="Pencatat Gaji Karyawan", font=("Helvetica", 18, "bold"), bootstyle=PRIMARY)
        title_label.pack(pady=10)

        input_frame = ttk.LabelFrame(page_frame, text="Tambah Karyawan", padding=10, bootstyle=INFO)
        input_frame.pack(fill=X, pady=10)
        ttk.Label(input_frame, text="Nama Karyawan:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Label(input_frame, text="Gaji per Hari:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.salary_entry = ttk.Entry(input_frame, width=20)
        self.salary_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        add_button = ttk.Button(input_frame, text="Tambah Karyawan", command=self.add_employee, bootstyle=SUCCESS)
        add_button.grid(row=0, column=2, rowspan=2, padx=20, sticky="ns")
        input_frame.columnconfigure(1, weight=1)

        action_frame = ttk.Frame(page_frame)
        action_frame.pack(fill=X, pady=5, padx=10)
        self.submit_button = ttk.Button(action_frame, text="Masukan Data Mingguan", command=self.submit_weekly_data, bootstyle=PRIMARY)
        self.submit_button.pack(side=LEFT, padx=(0, 5))
        self.report_button = ttk.Button(action_frame, text="Lihat Gaji Keseluruhan", command=self.show_overall_salary_report, bootstyle=INFO)
        self.report_button.pack(side=LEFT, padx=5)
        self.grand_total_label = ttk.Label(action_frame, text="Total Gaji Mingguan: Rp 0.00", font=("Helvetica", 14, "bold"), bootstyle=SECONDARY)
        self.grand_total_label.pack(side=RIGHT)

        table_frame = ttk.LabelFrame(page_frame, text="Absensi & Gaji Mingguan", padding=10, bootstyle=INFO)
        table_frame.pack(fill=BOTH, expand=True, pady=10)
        cols = ["Nama", "Gaji/Hari", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu", "Total Gaji"]
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", bootstyle=PRIMARY)
        for col_text in cols:
            self.tree.heading(col_text, text=col_text)
            self.tree.column(col_text, anchor="center", width=90)
        self.tree.column("Nama", anchor="w", width=120)
        self.tree.column("Total Gaji", anchor="e", width=120)
        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview, bootstyle=ROUND)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.popup_menu = ttk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Hapus Karyawan", command=self.delete_employee)
        self.tree.bind("<ButtonRelease-1>", self.on_table_click)
        self.tree.bind("<Button-3>", self.show_popup)
        back_button = ttk.Button(page_frame, text="Kembali ke Home", command=lambda: controller.show_frame("HomePage"), bootstyle=SECONDARY)
        back_button.pack(pady=10)

        self.load_employees(initial_data.get("salary_data", {}).get("employees", []))

    def load_employees(self, employees):
        for emp in employees:
            values = [emp['name'], f"{emp['daily_salary']:,.2f}"] + emp['days'] + [f"{emp['weekly_total']:,.2f}"]
            item_id = self.tree.insert("", END, values=values)
            self.employee_data[item_id] = emp['daily_salary']
        self.update_grand_total()

    def get_data(self):
        employees = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            emp_data = {
                "name": values[0],
                "daily_salary": self.employee_data.get(item_id, 0),
                "days": values[2:9],
                "weekly_total": float(values[9].replace(",", ""))
            }
            employees.append(emp_data)
        return {"employees": employees, "all_time": self.all_time_salary_data}

    def add_employee(self):
        name, salary_str = self.name_entry.get(), self.salary_entry.get()
        if not name or not salary_str:
            messagebox.showerror("Input Tidak Lengkap", "Nama dan Gaji per Hari harus diisi.", parent=self)
            return
        try:
            salary = float(salary_str)
            if salary < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Gaji per Hari harus berupa angka positif.", parent=self)
            return
        values = [name, f"{salary:,.2f}"] + ["Libur"] * 7 + [f"{0:,.2f}"]
        item_id = self.tree.insert("", END, values=values)
        self.employee_data[item_id] = salary
        self.update_grand_total()
        self.name_entry.delete(0, END)
        self.salary_entry.delete(0, END)
        self.name_entry.focus_set()

    def on_table_click(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        item_id = self.tree.focus()
        column_id_str = self.tree.identify_column(event.x)
        if not item_id or column_id_str not in self.day_columns: return
        current_state = self.tree.set(item_id, column_id_str)
        try:
            current_index = self.work_states.index(current_state)
            new_state = self.work_states[(current_index + 1) % len(self.work_states)]
        except ValueError:
            new_state = self.work_states[0]
        self.tree.set(item_id, column_id_str, new_state)
        self.recalculate_row_total(item_id)

    def recalculate_row_total(self, item_id):
        if item_id not in self.employee_data: return
        daily_salary = self.employee_data[item_id]
        current_values = self.tree.item(item_id, "values")
        total_multiplier = sum(self.state_multipliers.get(state, 0) for state in current_values[2:9])
        total_weekly_salary = daily_salary * total_multiplier
        self.tree.set(item_id, column="Total Gaji", value=f"{total_weekly_salary:,.2f}")
        self.update_grand_total()

    def update_grand_total(self):
        grand_total = sum(float(self.tree.item(item_id, "values")[9].replace(",", "")) for item_id in self.tree.get_children())
        self.grand_total_label.config(text=f"Total Gaji Mingguan: Rp {grand_total:,.2f}")

    def submit_weekly_data(self):
        if not self.tree.get_children():
            messagebox.showwarning("Data Kosong", "Tidak ada data gaji untuk dimasukan.", parent=self)
            return
        prompt = "Yakin masukan data & reset absensi?"
        if not messagebox.askyesno("Konfirmasi", prompt, parent=self):
            return
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            name, weekly_total_str = values[0], values[9]
            try:
                weekly_total = float(weekly_total_str.replace(",", ""))
                self.all_time_salary_data[name] = self.all_time_salary_data.get(name, 0) + weekly_total
            except (ValueError, IndexError): continue
        self.reset_week()
        messagebox.showinfo("Berhasil", "Data gaji mingguan telah berhasil dimasukan.", parent=self)

    def reset_week(self):
        for item_id in self.tree.get_children():
            for col_id in self.day_columns:
                self.tree.set(item_id, col_id, "Libur")
            self.recalculate_row_total(item_id)

    def show_overall_salary_report(self):
        report_window = ttk.Toplevel(master=self.controller, title="Laporan Gaji Keseluruhan")
        report_window.geometry("400x500")
        report_window.transient(self.controller)
        report_window.grab_set()
        report_frame = ttk.LabelFrame(report_window, text="Akumulasi Gaji Karyawan", padding=10, bootstyle=INFO)
        report_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        tree = ttk.Treeview(report_frame, columns=["Nama", "Total Gaji"], show="headings", bootstyle=PRIMARY)
        tree.heading("Nama", text="Nama Karyawan")
        tree.heading("Total Gaji", text="Total Gaji Dibayarkan")
        tree.column("Nama", anchor="w")
        tree.column("Total Gaji", anchor="e")
        tree.pack(fill=BOTH, expand=True)
        if not self.all_time_salary_data:
            tree.insert("", END, values=("Tidak ada data...", ""))
        else:
            for name, total in sorted(self.all_time_salary_data.items()):
                tree.insert("", END, values=(name, f"{total:,.2f}"))

    def show_popup(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.popup_menu.post(event.x_root, event.y_root)

    def delete_employee(self):
        selected_items = self.tree.selection()
        if not selected_items: return
        if messagebox.askyesno("Konfirmasi Hapus", "Yakin ingin menghapus data karyawan ini?", parent=self):
            for item_id in selected_items:
                name_to_delete = self.tree.item(item_id, "values")[0]
                self.tree.delete(item_id)
                if item_id in self.employee_data: del self.employee_data[item_id]
                if name_to_delete in self.all_time_salary_data: del self.all_time_salary_data[name_to_delete]
            self.update_grand_total()
