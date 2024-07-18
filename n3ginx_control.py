#```python
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import time
import os
import psutil

class NginxApp:
    def __init__(self, master):
        self.master = master
        master.title("Nginx Control Panel")

        # Process control
        self.process = None

        # Log display settings
        self.log_lines_to_fetch = 10  # Default: fetch last 10 lines
        self.reverse_log_order = True  # Default: reverse log order

        # Create Tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')
        
        # Control Tab
        self.control_frame = tk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control")

        # Log Tabs
        #self.access_log_frame = tk.Frame(self.notebook)
        #self.notebook.add(self.access_log_frame, text="Access Log")
        self.error_log_frame = tk.Frame(self.notebook)
        self.notebook.add(self.error_log_frame, text="Error Log")

        # Nginx Configuration Tab
        self.nginx_conf_frame = tk.Frame(self.notebook)
        self.notebook.add(self.nginx_conf_frame, text="Nginx Config")

        # Frame for buttons, align horizontally
        self.button_frame = tk.Frame(self.control_frame)
        self.button_frame.pack(pady=10)

        # Button to start Nginx
        self.start_button = tk.Button(self.button_frame, text="Start Nginx", command=self.start_nginx)
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Button to stop Nginx
        self.stop_button = tk.Button(self.button_frame, text="Stop Nginx", command=self.stop_nginx)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Label for process count
        self.process_count_label = tk.Label(self.button_frame, text="Nginx Processes: 0")
        self.process_count_label.pack(side=tk.LEFT, padx=5)
        
        # Frame for log settings
        self.log_settings_frame = tk.Frame(self.control_frame)
        self.log_settings_frame.pack()

        # Entry for number of lines
        tk.Label(self.log_settings_frame, text="Lines to fetch:").pack(side=tk.LEFT)
        self.lines_entry = tk.Entry(self.log_settings_frame, width=5)
        self.lines_entry.insert(0, str(self.log_lines_to_fetch))
        self.lines_entry.pack(side=tk.LEFT)

        # Checkbox for reverse order
        self.reverse_var = tk.BooleanVar(value=self.reverse_log_order)
        self.reverse_checkbox = tk.Checkbutton(self.log_settings_frame, text="Reverse order", variable=self.reverse_var)
        self.reverse_checkbox.pack(side=tk.LEFT)

        # Text window for access log
        #self.access_log_window = scrolledtext.ScrolledText(self.access_log_frame, wrap=tk.WORD)
        self.access_log_window = scrolledtext.ScrolledText(self.control_frame, wrap=tk.WORD)
        self.access_log_window.pack(expand=True, fill="both")

        # Text window for error log
        self.error_log_window = scrolledtext.ScrolledText(self.error_log_frame, wrap=tk.WORD)
        self.error_log_window.pack(expand=True, fill="both")

        # Text window for nginx.conf
        self.nginx_conf_window = scrolledtext.ScrolledText(self.nginx_conf_frame, wrap=tk.WORD)
        self.nginx_conf_window.pack(expand=True, fill="both")

        # Update process count and logs
        self.update_process_count()
        self.update_logs()
        self.update_error_log()
        self.display_nginx_conf()

    def start_nginx(self):
        self.process = subprocess.Popen(["nginx.exe"])
        self.update_button_colors()

    def stop_nginx(self):
        try:
            result = subprocess.run(["nginx.exe", "-s", "quit"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            #messagebox.showinfo("Success", "Nginx stopped successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to stop Nginx: {e.stderr}")
        except FileNotFoundError as e:
            messagebox.showerror("Error", "Nginx executable not found. Ensure nginx.exe is in the PATH or provide the full path.")
        self.update_button_colors()

    def update_process_count(self):
        try:
            #output = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq nginx.exe"], text=True)
            #process_count = output.count("nginx.exe")
            process_count = len([p for p in psutil.process_iter() if p.name() == "nginx.exe"])
            self.process_count_label.config(text=f"Nginx Processes: {process_count}")
            self.update_button_colors(process_count)
        except subprocess.CalledProcessError:
            self.process_count_label.config(text="Nginx Processes: Error")
        finally:
            self.master.after(2000, self.update_process_count)  # Update every 2 seconds

    def update_button_colors(self, process_count=0):
        if process_count == 0:
            self.start_button.config(fg="green")
            self.stop_button.config(fg="black")
        else:
            self.start_button.config(fg="black")
            self.stop_button.config(fg="red")

    def update_logs(self):
        if os.path.exists(".\\logs\\access.log"):
            with open(".\\logs\\access.log", "r") as log_file:
                lines = log_file.readlines()
                if self.reverse_var.get():
                    lines = lines[-self.log_lines_to_fetch:][::-1]
                else:
                    lines = lines[-self.log_lines_to_fetch:]
                self.access_log_window.config(state=tk.NORMAL)
                self.access_log_window.delete(1.0, tk.END)
                for line in lines:
                    self.access_log_window.insert(tk.END, line) #self.colorize_line(line))
                self.access_log_window.config(state=tk.DISABLED)
        self.master.after(2000, self.update_logs)

    def update_error_log(self):
        if os.path.exists(".\\logs\\error.log"):
            with open(".\\logs\\error.log", "r") as log_file:
                lines = log_file.readlines()
                if self.reverse_var.get():
                    lines = lines[-self.log_lines_to_fetch:][::-1]
                else:
                    lines = lines[-self.log_lines_to_fetch:]
                self.error_log_window.config(state=tk.NORMAL)
                self.error_log_window.delete(1.0, tk.END)
                for line in lines:
                    self.error_log_window.insert(tk.END, line)
                self.error_log_window.config(state=tk.DISABLED)
        self.master.after(2000, self.update_error_log)

    def display_nginx_conf(self):
        if os.path.exists(".\\conf\\nginx.conf"):
            with open(".\\conf\\nginx.conf", "r") as conf_file:
                content = conf_file.read()
                self.nginx_conf_window.config(state=tk.NORMAL)
                self.nginx_conf_window.delete(1.0, tk.END)
                self.nginx_conf_window.insert(tk.END, content)
                self.nginx_conf_window.config(state=tk.DISABLED)

    def colorize_line(self, line):
        parts = line.split(" ")
        colored_line = ""
        colors = ["blue", "green", "red", "purple", "orange", "brown", "pink", "cyan", "magenta", "yellow"]
        for i, part in enumerate(parts):
            color = colors[i % len(colors)]
            colored_line += self.color_text(part, color) + " "
        return colored_line

    def color_text(self, text, color):
        return f"{{{color}}}{{{text}}}"

# Main
root = tk.Tk()
app = NginxApp(root)
root.mainloop()
