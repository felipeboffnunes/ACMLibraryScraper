import subprocess
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
from tkinter import filedialog as fd
from components.csv_merger import progress, concatenate_csv
from components.processing import process_page, create_urls, parse_search_term


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_widgets()
        self.grid()
        
    def create_widgets(self):
        # Setup variables
        self.path = ""

        fontStyle = tkFont.Font(family="Century Gothic", size=30)
        self.title = tk.Label(self, text="ACM Library Scraper", pady=3, font=fontStyle, foreground='#444444')
        self.title.grid(row=0, columnspan=2)
        self.title.configure(background='white')

        self.search_term = tk.Text(self, height=10, width=70, borderwidth=0)
        self.search_term.grid(row=1, columnspan=2)
        st_raw = "(code summarization OR comment generation) AND (software engineering)"
        st = tk.StringVar()
        st.set(st_raw)
        self.search_term.insert(tk.INSERT, st_raw)

        self.s = ttk.Style()
        self.s.theme_use("classic")
        self.s.configure("colour.Horizontal.TProgressbar", troughcolor="white", borderwidth=0)
        progress_var = tk.IntVar()
        maxValue=2000
        self.update()
        TROUGH_COLOR = 'white'
        BAR_COLOR = 'black'
        self.s.configure("bar.Horizontal.TProgressbar", troughcolor=TROUGH_COLOR, bordercolor=TROUGH_COLOR, background=BAR_COLOR, lightcolor=BAR_COLOR, darkcolor=BAR_COLOR, borderwidth=0)
        self.progressbar=ttk.Progressbar(self, orient="horizontal",mode="determinate",maximum=maxValue, variable=progress_var, length=self.search_term.winfo_width())
        self.progressbar.configure(style="bar.Horizontal.TProgressbar")
        self.progressbar.grid(row=2, column=0, columnspan=2, pady=(0,20))
    
        path_button_image = tk.PhotoImage(file=r".\img\button_select-directory-for-csv.png")
        self.path_button = tk.Button(self, text="Select directory for csv", command=self.get_path, image=path_button_image, relief=tk.FLAT, borderwidth=0)
        self.path_button.image = path_button_image
        self.path_button.grid(row=3, column=0)
        self.path_button.configure(background='white')
      
        process_button_image = tk.PhotoImage(file=r".\img\button_process.png")
        self.process_button = tk.Button(self, text="Process", command=self.call_subprocess, image=process_button_image, relief=tk.FLAT, borderwidth=0)
        self.process_button.image = process_button_image
        self.process_button.grid(row=3, column=1)
        self.process_button.configure(background='white')
        
        fontM = tkFont.Font(family="Century Gothic", size=9)
        self.musaeum = tk.Label(self, text="Made by Musaeum.", pady=3, font=fontM, foreground='#444444')
        self.musaeum.grid(row=4, columnspan=2)
        self.musaeum.configure(background='white')
        
        self.configure(background='white')

    def opendoneWindow(self): 
      
        # Toplevel object which will  
        # be treated as a new window 
        doneWindow = tk.Toplevel(self) 
    
        # sets the title of the 
        # Toplevel widget 
        doneWindow.title("Search done") 
    
        # sets the geometry of toplevel 
        doneWindow.geometry("200x50") 
    
        # A Label widget to show in toplevel 
        tk.Label(doneWindow,  
            text ="Your search is saved as a csv!").pack()

    def finish_process(self):
        name = self.url[44:-1]
        name = name.replace('%28', '')
        name = name.replace('%29', '')
        name = name.replace('+', '_')
        if len(name) > 30:
            name = name[0:30]
            concatenate_csv(self.path, name)
        else: 
            concatenate_csv(self.path, name)
        self.opendoneWindow()

    def get_path(self):
        self.path = fd.askdirectory()

    def progress_update(self, currentValue):
        self.progressbar["value"]=currentValue
        
    def update_progressbar(self):
        currentValue = progress(self.path)*10
        if currentValue == self.progressbar["maximum"]:
            self.finish_process()
        self.progress_update(currentValue)
        self.after(5000, self.update_progressbar)

    def call_subprocess(self):
        self.set_url()
        self.check_search()
        subprocess.Popen(["python", ".\\components\\call_processes.py", self.url, self.path, str(self.pages_full)])
        self.update_progressbar()

    def set_url(self):
        search_term = parse_search_term(self.search_term.get('1.0', 'end'))
        url = 'https://dl.acm.org/action/doSearch?AllField={}'.format(search_term)
        self.url = url

    def check_search(self):
        pages_full = 0
        #pages_full = process_page(self.url, find_pages=True, page_size=50)
        if pages_full > 20:
            self.pages_full=20
        else:
            self.pages_full = pages_full 
        self.pages_full = 2
        self.progressbar["maximum"]=self.pages_full*10

    


            