import customtkinter as ctk
from tkinter import messagebox
from db import init_db, get_db_connection
from utils import hash_password, verify_password
import user, admin, counselor
from PIL import Image
import os
import sqlite3
import datetime

# --- Setup Paths and Initialize DB ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, "assets")

init_db()
ctk.set_appearance_mode("light")
try:
    ctk.set_default_color_theme("steam_theme.json")
except FileNotFoundError:
    ctk.set_default_color_theme("blue")

# --- Main App Window ---
app = ctk.CTk()
app.title("MindSync Aura - Welcome")
app.geometry("1280x720")
app.minsize(1100, 700)
app.configure(fg_color="#FFFFFF")

# --- Splash Screen ---
splash_frame = ctk.CTkFrame(app, fg_color="#4338CA", corner_radius=0)
splash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
ctk.CTkLabel(splash_frame, text="🌸 MindSync Aura",
             font=ctk.CTkFont(size=50, weight="bold"),
             text_color="white").pack(pady=(app.winfo_screenheight() // 4, 20))
ctk.CTkLabel(splash_frame, text="Your journey to inner peace begins now.",
             font=ctk.CTkFont(size=20), text_color="#E0E7FF").pack()

# --- Main UI Function ---
def show_main_ui():
    splash_frame.destroy()
    app.after(100, lambda: app.state("zoomed"))

    main_container = ctk.CTkFrame(app, fg_color="#F3F4F6", corner_radius=0)
    main_container.pack(fill="both", expand=True)
    main_container.grid_columnconfigure(0, weight=2)
    main_container.grid_columnconfigure(1, weight=3)
    main_container.grid_rowconfigure(0, weight=1)

    left_panel = ctk.CTkFrame(main_container, fg_color="#4338CA", corner_radius=0)
    left_panel.grid(row=0, column=0, sticky="nsew")
    try:
        logo_pil = Image.open(os.path.join(ASSETS_PATH, "logo.png")).convert("RGBA")
        watermark_img = logo_pil.resize((400, 400), Image.LANCZOS)
        alpha = watermark_img.split()[3]; alpha = alpha.point(lambda p: p * 0.08)
        watermark_img.putalpha(alpha)
        watermark_ctk = ctk.CTkImage(watermark_img, size=(400, 400))
        ctk.CTkLabel(left_panel, image=watermark_ctk, text="").place(relx=0.5, rely=0.5, anchor="center")
    except Exception as e: print(f"Could not create watermark: {e}")
    left_content_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
    left_content_frame.place(relx=0.5, rely=0.4, anchor="center")
    ctk.CTkLabel(left_content_frame, text="MindSync Aura", font=ctk.CTkFont(size=40, weight="bold"), text_color="white").pack(pady=10)
    ctk.CTkLabel(left_content_frame, text="A safe space for your thoughts.\nClarity for your mind.",
                 font=ctk.CTkFont(size=18), text_color="#C7D2FE", wraplength=400, justify="center").pack(pady=10)
    
    right_panel = ctk.CTkFrame(main_container, fg_color="#FFFFFF", corner_radius=0)
    right_panel.grid(row=0, column=1, sticky="nsew")
    login_card = ctk.CTkFrame(right_panel, fg_color="#FFFFFF", width=400)
    login_card.place(relx=0.5, rely=0.5, anchor="center")
    ctk.CTkLabel(login_card, text="Welcome Back", font=ctk.CTkFont(size=32, weight="bold"), text_color="#111827").pack(pady=(20, 10))
    ctk.CTkLabel(login_card, text="Please enter your details to sign in.", font=ctk.CTkFont(size=16), text_color="#6B7280").pack(pady=(0, 30))
    ctk.CTkLabel(login_card, text="Username", anchor="w", text_color="#374151", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=40, pady=(15, 5))
    entry_username = ctk.CTkEntry(login_card, height=45, placeholder_text="your.username", fg_color="#F9FAFB", border_color="#E5E7EB", border_width=1, corner_radius=8)
    entry_username.pack(fill="x", padx=40)
    ctk.CTkLabel(login_card, text="Password", anchor="w", text_color="#374151", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=40, pady=(20, 5))
    entry_password = ctk.CTkEntry(login_card, show="*", height=45, placeholder_text="••••••••", fg_color="#F9FAFB", border_color="#E5E7EB", border_width=1, corner_radius=8)
    entry_password.pack(fill="x", padx=40)
    
    def register_user():
        def save_user():
            name, uname, pwd, role = entry_name.get(), entry_uname.get(), entry_pwd.get(), role_var.get()
            if not all([name, uname, pwd, role]): messagebox.showerror("Error", "All fields are required!", parent=reg_win); return
            conn = get_db_connection()
            try:
                conn.execute("INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)", (name, uname, hash_password(pwd), role))
                conn.commit(); messagebox.showinfo("Success", "User Registered Successfully!", parent=reg_win); reg_win.destroy()
            except sqlite3.IntegrityError: messagebox.showerror("Error", "This username is already taken.", parent=reg_win)
            finally: conn.close()
        reg_win = ctk.CTkToplevel(app); reg_win.title("Create an Account"); reg_win.geometry("450x500")
        reg_win.transient(app); reg_win.grab_set(); reg_win.configure(fg_color="#F9FAFB")
        ctk.CTkLabel(reg_win, text="Join MindSync Aura", font=ctk.CTkFont(size=22, weight="bold"), text_color="#1E293B").pack(pady=(30, 20))
        ctk.CTkLabel(reg_win, text="Full Name", anchor="w").pack(fill="x", padx=40); entry_name = ctk.CTkEntry(reg_win, width=300, height=35); entry_name.pack(pady=(0, 15))
        ctk.CTkLabel(reg_win, text="Username", anchor="w").pack(fill="x", padx=40); entry_uname = ctk.CTkEntry(reg_win, width=300, height=35); entry_uname.pack(pady=(0, 15))
        ctk.CTkLabel(reg_win, text="Password", anchor="w").pack(fill="x", padx=40); entry_pwd = ctk.CTkEntry(reg_win, show="*", width=300, height=35); entry_pwd.pack(pady=(0, 15))
        ctk.CTkLabel(reg_win, text="Select Role", anchor="w").pack(fill="x", padx=40); role_var = ctk.StringVar(value="user"); ctk.CTkOptionMenu(reg_win, variable=role_var, values=["user", "admin", "counselor"], width=300, height=35).pack()
        ctk.CTkButton(reg_win, text="Create Account", command=save_user, height=40, fg_color="#22C55E", hover_color="#16A34A").pack(pady=30)

    def login_user():
        uname = entry_username.get(); pwd = entry_password.get()
        if not all([uname, pwd]): messagebox.showerror("Error", "Username and password cannot be empty."); return
        conn = get_db_connection(); row = conn.execute("SELECT id, password, role FROM users WHERE username=?", (uname,)).fetchone(); conn.close()
        if row and verify_password(pwd, row[1]):
            user_id, _, role = row
            if role == "user": check_for_appointments(user_id)
            app.withdraw()
            if role == "user": user.user_dashboard(app, user_id)
            elif role == "admin": admin.admin_dashboard(app)
            elif role == "counselor": counselor.counselor_dashboard(app, user_id)
        else: messagebox.showerror("Login Failed", "Invalid username or password.")
            
    def check_for_appointments(user_id):
        today = datetime.date.today().isoformat()
        conn = get_db_connection(); query = "SELECT a.time, u.name FROM appointments a JOIN users u ON a.counselor_id = u.id WHERE a.user_id = ? AND a.date = ? AND a.status IN ('Scheduled', 'Rescheduled')"
        appointment = conn.execute(query, (user_id, today)).fetchone(); conn.close()
        if appointment:
            time, counselor_name = appointment
            message = f"🔔 Reminder: You have an appointment today at {time} with {counselor_name}."
            messagebox.showinfo("Appointment Reminder", message)

    ctk.CTkButton(login_card, text="Sign In", command=login_user, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#4F46E5", hover_color="#4338CA").pack(fill="x", padx=40, pady=(30, 15))
    signup_frame = ctk.CTkFrame(login_card, fg_color="transparent"); signup_frame.pack(pady=(0, 20))
    ctk.CTkLabel(signup_frame, text="Don't have an account?", font=ctk.CTkFont(size=14), text_color="#6B7280").pack(side="left")
    ctk.CTkButton(signup_frame, text="Sign Up Now", command=register_user, height=20, font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent", text_color="#4F46E5", hover_color="#FFFFFF").pack(side="left", padx=5)
    ctk.CTkButton(login_card, text="Quit Application", command=lambda: os._exit(0), height=35, font=ctk.CTkFont(size=14), fg_color="transparent", text_color="#EF4444", hover_color="#FEE2E2").pack(side="bottom", pady=(20, 20))

# --- Schedule Splash Screen & Main Loop ---
app.after(2000, show_main_ui)
app.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
app.mainloop()