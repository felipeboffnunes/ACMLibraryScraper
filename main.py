from components.gui import Application, tk
import multiprocessing

def main():
    root = tk.Tk()
    root.title("ACM Library Scraper") 
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()