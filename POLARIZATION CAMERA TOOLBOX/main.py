import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, Toplevel
from PIL import Image, ImageTk
from threading import Thread
import pandas as pd
import platform
import subprocess


from plotly.subplots import make_subplots
import plotly.graph_objects as go
from tkhtmlview import HTMLLabel
import tempfile
import webbrowser

# Enable interactive matplotlib for zooming/panning
plt.switch_backend('TkAgg')

root = tk.Tk()
root.title("Polarization Camera")
root.geometry("1000x800")

output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

current_matrix = tk.StringVar()

# Map internal keys to user-friendly display names
display_name_map = {
    "I_00": "I_00",
    "I_45": "I_45",
    "I_90": "I_90",
    "I_45_90": "I_45_90",
    "S0": "S0",
    "S1": "S1",
    "S2": "S2",
    "S3": "S3",
    "DOP": "Degree of Polarization",
    "OA": "Orientation Angle",
    "EA": "Angle of Ellipticity",
    "PD": "Phase Difference",
    "Ex_amptd": "Ex Amplitude",
    "Ey_amptd": "Ey Amplitude"
}

# Reverse map for display name → internal key
internal_key_map = {v: k for k, v in display_name_map.items()}


current_folder = tk.StringVar()
image_label = tk.Label(root)
image_label.pack(pady=10)

loading_label = tk.Label(root, text="", font=("Arial", 14), fg="blue")
loading_label.pack()

def save_heatmap(matrix, name, folder):
    vmin, vmax = None, None
    if name == "EA":
        matrix = np.clip(matrix, -np.pi / 4, np.pi / 4)
        vmin, vmax = -np.pi / 4, np.pi / 4
    elif name == "OA":
        matrix = np.clip(matrix, 0, np.pi)
        vmin, vmax = 0, np.pi

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        zmin=vmin,
        zmax=vmax,
        colorscale='Viridis',
        colorbar=dict(title=name)
    ))
    # fig.update_layout(title=name, autosize=False, width=600, height=500)
    fig.update_layout(title=display_name_map.get(name, name), autosize=False, width=600, height=500)

    path = os.path.join(folder, f"{name}.png")
    fig.write_image(path)
    np.savetxt(os.path.join(folder, f"{name}.txt"), matrix, fmt='%.4f')

def show_image(name=None):
    folder = current_folder.get()
    if not folder:
        messagebox.showerror("Error", "No folder selected. Please process images first.")
        return

    # Get display name from dropdown
    display_name = current_matrix.get()

    # Convert display name (e.g. "Orientation Angle") to internal key (e.g. "OA")
    internal_name = internal_key_map.get(display_name, display_name)

    # Load the image file using internal name
    path = os.path.join(folder, f"{internal_name}.png")

    if os.path.exists(path):
        try:
            img = Image.open(path)
            img = img.resize((500, 400), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img)
            image_label.image = img
        except Exception as e:
            messagebox.showerror("Image Error", f"Could not display image: {e}")
    else:
        messagebox.showerror("File Not Found", f"{internal_name}.png not found in:\n{folder}")



# def show_image(name):
#     path = os.path.join(current_folder.get(), f"{name}.png")
#     if os.path.exists(path):
#         img = Image.open(path)
#         img = img.resize((500, 400), Image.Resampling.LANCZOS)
#         img = ImageTk.PhotoImage(img)
#         image_label.config(image=img)
#         image_label.image = img
#         current_matrix.set(name)
#     else:
#         messagebox.showerror("Error", f"{name}.png not found!")

def show_matrix():
    name = internal_key_map.get(current_matrix.get(), current_matrix.get())
    folder = current_folder.get()
    excel_path = os.path.join(folder, "matrices.xlsx")

    if not os.path.exists(excel_path):
        messagebox.showerror("Error", "Excel file not found. Please process images first.")
        return

    try:
        system = platform.system()

        if system == 'Windows':
            os.startfile(excel_path)
        elif system == 'Darwin':  # macOS
            subprocess.call(['open', excel_path])
        elif system == 'Linux':
            subprocess.call(['xdg-open', excel_path])
        else:
            messagebox.showerror("Unsupported OS", f"Cannot open Excel file on: {system}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Excel file: {e}")


# def show_matrix():
#     # name = current_matrix.get()
#     name = internal_key_map.get(current_matrix.get(), current_matrix.get())

#     folder = current_folder.get()
#     path = os.path.join(folder, f"{name}.txt")
#     if os.path.exists(path):
#         matrix_window = Toplevel(root)
#         matrix_window.title(f"{name} Matrix")
#         text_box = scrolledtext.ScrolledText(matrix_window, width=100, height=30, font=("Courier", 8))
#         text_box.pack()
#         with open(path, 'r') as f:
#             text_box.insert(tk.END, f.read())
#     else:
#         messagebox.showerror("Error", f"Matrix for {name} not available.")

def show_interactive_plot(name=None):
    if not name:
        name = internal_key_map.get(current_matrix.get(), current_matrix.get())

        # name = current_matrix.get()
    folder = current_folder.get()
    path = os.path.join(folder, f"{name}.txt")
    if not os.path.exists(path):
        messagebox.showerror("Error", f"{name}.txt not found!")
        return

    matrix = np.loadtxt(path)

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        colorscale='Viridis',
        colorbar=dict(title=name)
    ))
    fig.update_layout(title=f"{name} (Interactive)", autosize=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
        fig.write_html(tmpfile.name)
        webbrowser.open(f"file://{tmpfile.name}")

def show_interactive_ellipses():
    folder = current_folder.get()
    try:
        OA = np.loadtxt(os.path.join(folder, "OA.txt"))
        EA = np.loadtxt(os.path.join(folder, "EA.txt"))
        Ex = np.loadtxt(os.path.join(folder, "Ex_amptd.txt"))
        Ey = np.loadtxt(os.path.join(folder, "Ey_amptd.txt"))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load ellipse data: {e}")
        return

    nx, ny = OA.shape
    step = 20
    maj_axis = np.sqrt(Ex**2 + Ey**2)
    EA = np.clip(EA, -np.pi/2, np.pi/2)
    min_axis = maj_axis * np.tan(EA)

    fig = go.Figure()

    for i in range(0, nx, step):
        for j in range(0, ny, step):
            theta = OA[i, j]
            A = maj_axis[i, j]
            B = min_axis[i, j]
            phi = np.linspace(0, 2*np.pi, 50)
            x = A * np.cos(phi) * np.cos(theta) - B * np.sin(phi) * np.sin(theta)
            y = A * np.cos(phi) * np.sin(theta) + B * np.sin(phi) * np.cos(theta)
            fig.add_trace(go.Scatter(
                x=x + j,
                y=y + i,
                mode='lines',
                line=dict(color='black', width=1),
                showlegend=False
            ))

    fig.update_layout(
        title="Interactive Polarization Ellipses",
        xaxis=dict(scaleanchor="y", showgrid=False, visible=False),
        yaxis=dict(showgrid=False, visible=False),
        autosize=True,
        height=700
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmpfile:
        fig.write_html(tmpfile.name)
        webbrowser.open(f"file://{tmpfile.name}")

def plot_ellipses(folder, OA, EA, Ex_amptd, Ey_amptd):
    nx, ny = OA.shape
    step = 20
    # maj_axis = np.sqrt(Ex_amptd ** 2 + Ey_amptd ** 2)
    maj_axis = np.sqrt(Ex_amptd**2 + Ey_amptd**2) * np.cos(EA)

    EA = np.clip(EA, -np.pi / 2, np.pi / 2)
    min_axis = maj_axis * np.tan(EA)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(0, nx)
    ax.set_ylim(0, ny)
    ax.set_aspect('equal')

    for i in range(0, nx, step):
        for j in range(0, ny, step):
            theta = OA[i, j]
            A = maj_axis[i, j]
            B = min_axis[i, j]
            phi = np.linspace(0, 2 * np.pi, 50)
            x = A * np.cos(phi) * np.cos(theta) - B * np.sin(phi) * np.sin(theta)
            y = A * np.cos(phi) * np.sin(theta) + B * np.sin(phi) * np.cos(theta)
            ax.plot(x + i, y + j, 'k', linewidth=0.5)

    plt.title("Polarization Ellipses")
    ellipse_path = os.path.join(folder, "Ellipses.png")
    plt.savefig(ellipse_path)
    plt.close()
    np.savetxt(os.path.join(folder, "Ellipses.txt"), np.zeros((1, 1)), fmt='%d')  # Dummy file

def show_I_subplots():
    folder = current_folder.get()
    titles = ["I_00", "I_45", "I_90", "I_45_90"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for idx, title in enumerate(titles):
        ax = axes[idx // 2, idx % 2]
        path = os.path.join(folder, f"{title}.txt")
        if os.path.exists(path):
            matrix = np.loadtxt(path)
            im = ax.imshow(matrix, cmap="viridis")
            ax.set_title(title, fontsize=10)
            ax.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(folder, "I_Subplots.png"))
    plt.show()

# def process_images():
#     loading_label.config(text="Processing... Please wait...")

#     mode = messagebox.askquestion("Upload Mode", "Do you want to upload both main and 90° images?\n\nClick 'Yes' for both images.\nClick 'No' for single image only.")

#     path1 = filedialog.askopenfilename(title="Select Main Image")
#     if not path1:
#         messagebox.showerror("Error", "Main image is required")
#         loading_label.config(text="")
#         return

#     path2 = None
#     if mode == 'yes':
#         path2 = filedialog.askopenfilename(title="Select 90° Image")
#         if not path2:
#             messagebox.showerror("Error", "Second image is required in dual-image mode.")
#             loading_label.config(text="")
#             return

#     folder_name = os.path.splitext(os.path.basename(path1))[0]
#     folder = os.path.join(output_dir, folder_name)
#     os.makedirs(folder, exist_ok=True)
#     current_folder.set(folder)

#     image_gray = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
#     rows, cols = image_gray.shape
#     half_rows, half_cols = rows // 2, cols // 2

#     I_00 = image_gray[:half_rows, :half_cols]
#     I_45 = image_gray[half_rows:, :half_cols]
#     I_90 = image_gray[half_rows:, half_cols:]

#     matrices = {
#         "I_00": I_00,
#         "I_45": I_45,
#         "I_90": I_90,
#     }

#     S0 = I_00 + I_90
#     S1 = I_00 - I_90
#     S2 = 2 * I_45 - I_00 - I_90

#     matrices.update({
#         "S0": S0 / S0.max(),
#         "S1": S1 / S0.max(),
#         "S2": S2 / S0.max(),
#         "OA": np.arctan2(S2, S1) / 2,
#         "Ex_amptd": np.sqrt((S0 + S1) / 2),
#         "Ey_amptd": np.sqrt((S0 - S1) / 2),
#     })

#     if path2:
#         I_45_90 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)[half_rows:, :half_cols]
#         S3 = 2 * I_45_90 - I_00 - I_90
#         DOP = np.sqrt((S1**2 + S2**2 + S3**2) / (S0**2 + 1e-10))
#         EA = np.arcsin(np.clip(S3 / (S0 + 1e-10), -1, 1)) / 2
#         PD = np.arctan2(S3, S2) / 2

#         matrices.update({
#             "I_45_90": I_45_90,
#             "S3": S3 / S0.max(),
#             "DOP": DOP,
#             "EA": EA,
#             "PD": PD,
#         })

#     for name, matrix in matrices.items():
#         save_heatmap(matrix, name, folder)

#     if "EA" in matrices and "OA" in matrices:
#         plot_ellipses(folder, matrices["OA"], matrices["EA"], matrices["Ex_amptd"], matrices["Ey_amptd"])

#     loading_label.config(text="Done.")
#     messagebox.showinfo("Success", "Image processing complete.")

###################################################################################################################################

def process_images():
    loading_label.config(text="Processing... Please wait...")

    mode = messagebox.askquestion("Upload Mode", "Do you want to upload both main and 90° images?\n\nClick 'Yes' for both images.\nClick 'No' for single image only.")
    is_dual_mode = (mode == 'yes')

    path1 = filedialog.askopenfilename(title="Select Main Image")
    if not path1:
        messagebox.showerror("Error", "Main image is required")
        loading_label.config(text="")
        return

    path2 = None
    if is_dual_mode:
        path2 = filedialog.askopenfilename(title="Select 90° Image")
        if not path2:
            messagebox.showerror("Error", "Second image is required in dual-image mode.")
            loading_label.config(text="")
            return

    folder_name = os.path.splitext(os.path.basename(path1))[0]
    folder = os.path.join(output_dir, folder_name)
    os.makedirs(folder, exist_ok=True)
    current_folder.set(folder)

    image_gray = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)
    rows, cols = image_gray.shape
    half_rows, half_cols = rows // 2, cols // 2

    I_00 = image_gray[:half_rows, :half_cols]
    I_45 = image_gray[half_rows:, :half_cols]
    I_90 = image_gray[half_rows:, half_cols:]

    matrices = {
        "I_00": I_00,
        "I_45": I_45,
        "I_90": I_90,
    }

    S0 = I_00 + I_90
    S1 = I_00 - I_90
    S2 = 2 * I_45 - I_00 - I_90

    matrices.update({
        "S0": S0 / S0.max(),
        "S1": S1 / S0.max(),
        "S2": S2 / S0.max(),
        "OA": np.arctan2(S2, S1) / 2,
        "Ex_amptd": np.sqrt((S0 + S1) / 2),
        "Ey_amptd": np.sqrt((S0 - S1) / 2),
    })

    if is_dual_mode:
        I_45_90 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)[half_rows:, :half_cols]
        S3 = 2 * I_45_90 - I_00 - I_90
        DOP = np.sqrt((S1**2 + S2**2 + S3**2) / (S0**2 + 1e-10))
        EA = np.arcsin(np.clip(S3 / (S0 + 1e-10), -1, 1)) / 2
        PD = np.arctan2(S3, S2) / 2
        
        

        matrices.update({
            "I_45_90": I_45_90,
            "S3": S3 / S0.max(),
            "DOP": DOP,
            "EA": EA,
            "PD": PD,
        })

    for name, matrix in matrices.items():
        save_heatmap(matrix, name, folder)

    if "EA" in matrices and "OA" in matrices:
        plot_ellipses(folder, matrices["OA"], matrices["EA"], matrices["Ex_amptd"], matrices["Ey_amptd"])
#TEMP CHANGE#################################
    #save images in excel file
    excel_path = os.path.join(folder, "matrices.xlsx")
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for name, matrix in matrices.items():
            df = pd.DataFrame(matrix)
            df.to_excel(writer, sheet_name=name[:31])
###################################################

    # Update dropdown menu based on mode
    update_dropdown(is_dual_mode)

    loading_label.config(text="Done.")
    messagebox.showinfo("Success", "Image processing complete.")

def update_dropdown(is_dual_mode):
    menu = matrix_dropdown["menu"]
    menu.delete(0, "end")

    if is_dual_mode:
        keys = ["I_00", "I_45", "I_90", "I_45_90", "S0", "S1", "S2", "S3", "DOP", "OA", "EA", "PD", "Ex_amptd", "Ey_amptd"]
        ellipse_button.pack(pady=5)
    else:
        keys = ["I_00", "I_45", "I_90", "S0", "S1", "S2", "OA", "Ex_amptd", "Ey_amptd"]
        ellipse_button.pack_forget()

    for key in keys:
        label = display_name_map.get(key, key)
        menu.add_command(label=label, command=lambda value=label: current_matrix.set(value))

    current_matrix.set(display_name_map.get(keys[0], keys[0]))


# def update_dropdown(is_dual_mode):
#     menu = matrix_dropdown["menu"]
#     menu.delete(0, "end")

#     if is_dual_mode:
#         options = ["I_00", "I_45", "I_90", "I_45_90", "S0", "S1", "S2", "S3", "DOP", "OA", "EA", "PD", "Ex_amptd", "Ey_amptd"]
#         ellipse_button.pack(pady=5)

#     else:
#         options = ["I_00", "I_45", "I_90", "S0", "S1", "S2", "OA", "Ex_amptd", "Ey_amptd"]
#         ellipse_button.pack_forget()

#     for option in options:
#         menu.add_command(label=option, command=lambda value=option: current_matrix.set(value))

#     current_matrix.set(options[0])




# ---- GUI Buttons ----
# ---- GUI Buttons & Matrix Selection ----
tk.Button(root, text="Process Images", command=lambda: Thread(target=process_images).start()).pack(pady=5)
tk.Button(root, text="Show Matrix", command=show_matrix).pack(pady=5)
tk.Button(root, text="Show Interactive Plot", command=lambda: show_interactive_plot()).pack(pady=5)
tk.Button(root, text="Show I Subplots", command=show_I_subplots).pack(pady=5)
# tk.Button(root, text="Show Interactive Ellipses", command=show_interactive_ellipses).pack(pady=5)
ellipse_button = tk.Button(root, text="Show Interactive Ellipses", command=show_interactive_ellipses)
ellipse_button.pack(pady=5)
ellipse_button.pack_forget()  # Hide initially


# # Dropdown instead of free text entry
# matrix_options = ["I_00", "I_45", "I_90", "I_45_90", "S0", "S1", "S2", "S3", "DOP", "OA", "EA", "PD", "Ex_amptd", "Ey_amptd"]
# current_matrix.set(matrix_options[0])
# # tk.Label(root, text="Select Matrix:").pack()
# # tk.OptionMenu(root, current_matrix, *matrix_options).pack(pady=5)
# tk.Label(root, text="Select Matrix:").pack()
# matrix_dropdown = tk.OptionMenu(root, current_matrix, "I_00")  # dummy init
# matrix_dropdown.pack(pady=5)

matrix_dropdown = tk.OptionMenu(root, current_matrix, "")
matrix_dropdown.pack(pady=5)


tk.Button(root, text="Display Image", command=lambda: show_image(current_matrix.get())).pack(pady=5)

root.mainloop()



#CODED By Kartikey Rathi 