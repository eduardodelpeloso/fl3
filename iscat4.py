import pandas as pd
import matplotlib.pyplot as plt
import easygui
import tkinter as tk
from tkinter import simpledialog
from tkinter import Text
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Global variables
bin_size = 1.0
selected_y_column = 1


# Create buttons for actions
def update():
    global selected_y_column, bin_size, ax


    try:
        data = pd.read_csv(csv_file_path)

        x_data = data[data.columns[0]]
        y_data = data[data.columns[selected_y_column]]

        bin_size = float(bin_size_textbox.get(1.0, tk.END))
        if bin_size > 0:
            bins = pd.interval_range(start=x_data.min(), end=x_data.max(), freq=bin_size)
            grouped_data = y_data.groupby(pd.cut(x_data, bins)).mean()
            x_data_binned = [interval.mid for interval in grouped_data.index]
            y_data_binned = grouped_data.values
        else:
            x_data_binned = x_data
            y_data_binned = y_data

        ax.clear()
        ax.scatter(x_data_binned, y_data_binned)
        ax.set_xlabel(data.columns[0])
        ax.set_ylabel(data.columns[selected_y_column])
        ax.set_title("Scatter Plot with Binning")
        ax.grid(True)

        if log_x.get():
            ax.set_xscale('log')
        if log_y.get():
            ax.set_yscale('log')

        canvas.draw()
    except ValueError:
        print("Invalid input. Please enter a valid number.")


def open_csv_file():
    file_path = easygui.fileopenbox(default="*.csv", filetypes=["*.csv"])
    return file_path


def open_radio_dialog(data):
    global selected_y_column, selected_column

    dialog = tk.Toplevel()
    dialog.title("Select Column Index")

    def on_ok():
        global selected_y_column
        index = selected_column.get()
        if 1 <= index < len(data.columns):
            selected_y_column = index
            dialog.destroy()
            update()
        else:
            print("Invalid column index. Please select a valid index.")

    for i in range(1, len(data.columns)):
        tk.Radiobutton(dialog, text=str(i) + " " + data.columns[i], variable=selected_column, value=i).pack(anchor=tk.W)

    ok_button = tk.Button(dialog, text="OK", command=on_ok)
    ok_button.pack()


def main():
    global bin_size, selected_y_column, selected_column, csv_file_path, canvas, ax, bin_size_textbox, log_x, log_y

    root = tk.Tk()

    log_x = tk.IntVar(value=0)
    log_y = tk.IntVar(value=0)
    selected_column = tk.IntVar(value=1)

    csv_file_path = open_csv_file()

    try:
        data = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")
        return
    except pd.errors.EmptyDataError:
        print("The CSV file is empty.")
        return
    except pd.errors.ParserError:
        print("Unable to parse the CSV file. Please ensure it is well-formatted.")
        return

    if len(data.columns) < 2:
        print("The CSV file must contain at least two columns (X and Y data).")
        return

    x_data = data[data.columns[0]]
    y_data = data[data.columns[selected_y_column]]

    if bin_size > 0:
        bins = pd.interval_range(start=x_data.min(), end=x_data.max(), freq=bin_size)
        grouped_data = y_data.groupby(pd.cut(x_data, bins)).mean()
        x_data_binned = [interval.mid for interval in grouped_data.index]
        y_data_binned = grouped_data.values
    else:
        x_data_binned = x_data
        y_data_binned = y_data

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(x_data_binned, y_data_binned)
    ax.set_xlabel(data.columns[0])
    ax.set_ylabel(data.columns[selected_y_column])
    ax.set_title("Scatter Plot with Binning")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack()

    bin_size_textbox = tk.Text(root, height=1, width=10)
    bin_size_textbox.insert(tk.END, str(bin_size))
    bin_size_textbox.pack()

    update_button = tk.Button(root, text="Update Plot", command=update)
    update_button.pack()

    tk.Checkbutton(root, text="Log X", variable=log_x, command=update).pack()
    tk.Checkbutton(root, text="Log Y", variable=log_y, command=update).pack()

    select_column_button = tk.Button(root, text="Select column index", command=lambda: open_radio_dialog(data))
    select_column_button.pack()

    root.mainloop()


if __name__ == "__main__":
    main()
