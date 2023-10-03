import os, sys, webbrowser, chardet, tkinter as tk
from subprocess import Popen, PIPE
from tkinter import filedialog

def nx_file_renaming(path_to_nx_file_to_rename, name):

    # Take the Name that would be used to rename the file
    name = name + ".prt"

    # Split selected files directory and name into separate variables
    directory, nx_file_to_rename = os.path.split(path_to_nx_file_to_rename)
    # Convert the paths into Windows style path
    directory = directory.replace("/", "\\")

    # Collect All other NX files in the same directory
    nx_files = []

    files = os.listdir(directory)
    for file in files:
        if file.endswith('.prt'):
            nx_files.append(file)
            
    nx_files.remove(nx_file_to_rename)
            
    # Check for the children of the NX files
    arg_first_section = os.getenv("UGII_BASE_DIR") + "\\NXBIN\\ug_edit_part_names.exe "

    for nx_file in nx_files:
        arg_second_section = f'"{os.path.join(directory, nx_file)}"'
        get_argument = arg_first_section + arg_second_section + " -list"
        result = Popen(get_argument, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, error = result.communicate()
        
        if output:
            the_encoding = chardet.detect(output)['encoding']
            output = output.decode(encoding=the_encoding)
            childs = output.splitlines()

            # If no. of children is more than one then it is a Asssembly or Drawing file.
            if len(childs) > 1:
                # Update the link/reference of each Assembly or Drawing file
                for child in childs:
                    if nx_file_to_rename in child:
                        rename_arg = arg_first_section + arg_second_section + " -o " + arg_second_section + " -change_name " + f'"{nx_file_to_rename}" ' + f'"{name}"'
                        Popen(rename_arg, stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        break


    # Rename the file
    from_name = os.path.join(directory, nx_file_to_rename)
    to_name = os.path.join(directory, name)
    os.rename(from_name, to_name)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("NX File Renaming")

        # Set the window size
        self.root.geometry("700x200")
        self.root.resizable(False, False)

        # Add icon to the title bar
        root.iconbitmap(resource_path("nx_rename_icon.ico"))

        # Add background Color
        self.root['background']='#00e2a2'

        # Create a label for the file to rename entry field
        self.file_label = tk.Label(root, text="File to rename:")
        self.file_label['background']='#00e2a2'
        self.file_label.grid(row=1, column=0, padx= 25, pady=10)

        # Create a readonly entry field for the file to rename
        self.file_entry = tk.Entry(root, state="readonly", width=70)
        self.file_entry.grid(row=1, column=1, columnspan=4, padx=5, pady=10)

        # Check if the program was started from the right-click context menu
        if len(sys.argv) == 2:
            # If the program was started from the right-click context menu, insert the file name into the entry field
            file_name = sys.argv[1]

            if file_name.endswith(".prt"):
                # Enable the entry field
                self.file_entry.config(state="normal")

                # Insert the file name into the entry field
                self.file_entry.insert(0, file_name)

                # Make the entry field Readonly
                self.file_entry.config(state="readonly")

        # Create a browse button
        self.browse_button = tk.Button(root, text="Browse", command=self.browse, height=1, width=8)
        self.browse_button.grid(row=1, column=5, padx=10, pady=20)

        # Create a label for the new name entry field
        self.new_name_label = tk.Label(root, text="New Name:")
        self.new_name_label['background']='#00e2a2'
        self.new_name_label.grid(row=2, column=0, padx=5, pady=10)

        # Create an entry field for the new name
        self.new_name_entry = tk.Entry(root, width=70)
        self.new_name_entry.grid(row=2, column=1, columnspan=4, padx=5, pady=10)

        # Create an OK button
        self.ok_button = tk.Button(root, text="OK", command=self.rename_file, height=1, width=9)
        self.ok_button.grid(row=4, column=2, padx=5, pady=10)

        # Create a Cancel button
        self.cancel_button = tk.Button(root, text="Cancel", command=root.destroy, height=1, width=9)
        self.cancel_button.grid(row=4, column=3, padx=5, pady=10)

        # Create an About button
        self.about_button = tk.Button(root, text="About", command=self.show_about, height=1, width=9)
        self.about_button.grid(row=4, column=4, padx=5, pady=10)

        # Bind the Enter key to the OK button
        self.new_name_entry.bind("<Return>", lambda event: self.rename_file())

        # Create a label for Motto
        self.motto = tk.Label(root, text="SIEMENS NX", justify="right", fg="white", font=("calibri", 24, "bold"))
        self.motto['background']='#00e2a2'
        self.motto.grid(row=4, column=4, rowspan=5, columnspan=5, padx=0, pady=45)

    def browse(self):
        # Open a file dialog
        file_path = filedialog.askopenfilename(filetypes=[("NX Part Files", "*.prt")])

        # If the user selected a file, insert the file path into the entry field
        if file_path:
            self.file_entry.config(state="normal")
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
            self.file_entry.config(state="readonly")

    def show_about(self):
        # Create a new window to display the about information
        about_window = tk.Toplevel(self.root)
        about_window.resizable(False, False)
        about_window.title("About NX File Renaming")
        about_window.iconbitmap(resource_path("nx_rename_icon.ico"))
        about_window['background']='#00e2a2'

        # Create a label to display the about information
        info = "NX File Renaming v1.0\n\n"\
        "About Program:\n\n"\
        "NX File Renaming is an endeavour to automate SIEMENS NX. "\
        "This Program helps you to rename NX file "\
        "from windows and keeps the linked files such as Assembly or "\
        "Drawing updated. For details about this program check the github page "\
        "of the program. \nThis Program was written in Python. GUI of this program "\
        "was solely designed by the help of 'Bard', an AI by Google. "\
        "If you find any bug in the program then go to my Github account and comment it "\
        "on the projects page.\n\n\n\n"\
        "About Author:\n\n"\
        "MD. Nahid Mubin Khan.\n"\
        "Mechanical Engineer | Product Designer\n\n"\
        "Github: https://github.com/nahidmubin"

        about_label = tk.Label(about_window, text=info, justify="left", wraplength=500)
        about_label['background']='#00e2a2'
        about_label.grid(row=0, rowspan=7, column=0, padx=5, pady=10)

        # Create an Close button to close the about window
        close_button = tk.Button(about_window, text="Close", command=about_window.destroy, height=1, width=9)
        close_button.grid(row=7, column=0, padx=5, pady=10)

        # Add image file
        self.bg = tk.PhotoImage(file = resource_path("about_pic.png"))
        bg_label = tk.Label( about_window, image = self.bg, cursor="hand2")
        bg_label.grid(row=6, column=1, padx=15, pady=0)
        bg_label.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/nahidmubin"))


    def rename_file(self):
        # Get the file path and the new name
        file_path = self.file_entry.get()
        new_name = self.new_name_entry.get()

        # Check if the new name is empty
        if new_name == "":
            # If the new name is empty, show an error message
            tk.messagebox.showerror("Error!", "Please enter a new name for the file.")

            # Return so that the program does not rename the file
            return

        try:
            # Rename the file
            nx_file_renaming(file_path, new_name)

            
        
        except FileNotFoundError:
            tk.messagebox.showerror("Error!", "The file wasn't found. Please Enter a valid file to rename.")

            # Return so that the program does not rename the file
            return

        # Show a notification message
        tk.messagebox.showinfo("Success!", f"The file was successfully renamed to {new_name}.")

        # Close the window
        self.root.destroy()

if __name__ == "__main__":
        
    root = tk.Tk()
    app = App(root)
    root.mainloop()