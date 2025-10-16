import customtkinter as ctk
from tkinter import Toplevel, messagebox
from db import get_db_connection
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from wordcloud import WordCloud
from reports import export_report
import sqlite3

def admin_dashboard(app):
    app.withdraw()
    win = ctk.CTkToplevel(app)
    win.title("MindSync Aura – Admin Control Panel")
    win.state("zoomed")
    win.after(100, lambda: win.state("zoomed"))
    win.configure(fg_color="#F3F4F6")
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), app.deiconify()))

    header = ctk.CTkFrame(win, fg_color="#1F2937", height=80, corner_radius=0)
    header.pack(fill="x", side="top")
    ctk.CTkLabel(header, text="🛡️ Admin Control Panel", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(side="left", padx=40, pady=15)
    ctk.CTkLabel(header, text="System Management & Analytics", font=ctk.CTkFont(size=16), text_color="#D1D5DB").pack(side="right", padx=40)

    sidebar = ctk.CTkFrame(win, width=240, fg_color="#FFFFFF", corner_radius=0)
    sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)
    ctk.CTkLabel(sidebar, text="⚙️ Management", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B").pack(pady=(20, 10))

    def set_active(btn):
        for b in buttons: b.configure(fg_color="#E2E8F0", text_color="#334155")
        btn.configure(fg_color="#2563EB", text_color="white")

    def show_frame(frame, button):
        for f in [stats_frame, appoint_frame, users_frame]: f.pack_forget()
        frame.pack(fill="both", expand=True, padx=25, pady=25); set_active(button)

    buttons = []
    btn_stats = ctk.CTkButton(sidebar, text="📈 Group Stats", fg_color="#2563EB", text_color="white", hover_color="#1D4ED8", command=lambda: show_frame(stats_frame, btn_stats))
    btn_stats.pack(fill="x", padx=25, pady=(15, 5)); buttons.append(btn_stats)
    btn_appoint = ctk.CTkButton(sidebar, text="🗓️ Appointments", fg_color="#E2E8F0", text_color="#334155", hover_color="#CBD5E1", command=lambda: show_frame(appoint_frame, btn_appoint))
    btn_appoint.pack(fill="x", padx=25, pady=5); buttons.append(btn_appoint)
    btn_users = ctk.CTkButton(sidebar, text="👥 All Users", fg_color="#E2E8F0", text_color="#334155", hover_color="#CBD5E1", command=lambda: show_frame(users_frame, btn_users))
    btn_users.pack(fill="x", padx=25, pady=5); buttons.append(btn_users)
    ctk.CTkButton(sidebar, text="📄 Export Report", fg_color="#16A34A", hover_color="#15803D", command=lambda: export_report("group_report.pdf", ["Group Stress Report Generated."])).pack(side="bottom", fill="x", padx=25, pady=10)
    
    def handle_logout():
        win.destroy(); app.deiconify(); app.after(100, lambda: app.state("zoomed"))
    ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="#F87171", hover_color="#DC2626", text_color="white", command=handle_logout).pack(side="bottom", fill="x", padx=25, pady=(5, 20))

    main_content = ctk.CTkFrame(win, fg_color="#F9FAFB")
    main_content.pack(side="right", fill="both", expand=True)
    stats_frame = ctk.CTkFrame(main_content, fg_color="transparent")
    appoint_frame = ctk.CTkFrame(main_content, fg_color="transparent")
    users_frame = ctk.CTkFrame(main_content, fg_color="transparent")

    ctk.CTkLabel(stats_frame, text="Group Wellness Analytics", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E293B").pack(pady=20)
    stats_card = ctk.CTkFrame(stats_frame, fg_color="#FFFFFF", corner_radius=15)
    stats_card.pack(padx=30, pady=10, fill="both", expand=True)
    def show_group_stats():
        conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT stress_score FROM entries"); data = [row[0] for row in cur.fetchall()]; conn.close()
        if not data: messagebox.showinfo("Info", "No entries found."); return
        avg = round(sum(data) / len(data), 2); messagebox.showinfo("Group Stats", f"Average Group Stress Level: {avg}")
    def show_wordcloud():
        conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT journal FROM entries"); texts = [row[0] for row in cur.fetchall() if row[0]]; conn.close()
        if not texts: messagebox.showinfo("Info", "No journals yet."); return
        wc_win = Toplevel(win); wc_win.title("Journal Word Cloud"); fig, ax = plt.subplots(figsize=(8, 4))
        wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(texts)); ax.imshow(wc, interpolation="bilinear"); ax.axis("off")
        canvas = FigureCanvasTkAgg(fig, master=wc_win); canvas.draw(); canvas.get_tk_widget().pack()
        wc_win.protocol("WM_DELETE_WINDOW", lambda: (plt.close(fig), wc_win.destroy()))
    ctk.CTkButton(stats_card, text="Calculate Average Stress", command=show_group_stats).pack(pady=(40, 10))
    ctk.CTkButton(stats_card, text="Generate Journal Word Cloud", command=show_wordcloud).pack(pady=10)

    ctk.CTkLabel(appoint_frame, text="Schedule a New Appointment", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E293B").pack(pady=20)
    appoint_card = ctk.CTkFrame(appoint_frame, fg_color="#FFFFFF", corner_radius=15)
    appoint_card.pack(padx=30, pady=10, fill="x")
    def create_appointment():
        try:
            user_id = user_var.get().split(" - ")[0]; counselor_id = counselor_var.get().split(" - ")[0]
            if "No " in user_id or "No " in counselor_id: messagebox.showerror("Error", "A valid user and counselor must be selected."); return
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO appointments (user_id, counselor_id, date, time, status) VALUES (?, ?, ?, ?, ?)", (user_id, counselor_id, date_entry.get(), time_entry.get(), "Scheduled"))
            conn.commit(); conn.close(); messagebox.showinfo("Success", "Appointment created successfully!")
        except Exception as e: messagebox.showerror("Error", f"An error occurred: {e}")
    conn = get_db_connection(); user_list = conn.execute("SELECT id, name FROM users WHERE role='user'").fetchall(); counselor_list = conn.execute("SELECT id, name FROM users WHERE role='counselor'").fetchall(); conn.close()
    user_names = [f"{u[0]} - {u[1]}" for u in user_list] if user_list else ["No users found"]; counselor_names = [f"{c[0]} - {c[1]}" for c in counselor_list] if counselor_list else ["No counselors found"]
    user_var = ctk.StringVar(value=user_names[0]); counselor_var = ctk.StringVar(value=counselor_names[0])
    ctk.CTkLabel(appoint_card, text="Select User:").pack(pady=(20, 5)); ctk.CTkOptionMenu(appoint_card, values=user_names, variable=user_var, width=300).pack()
    ctk.CTkLabel(appoint_card, text="Select Counselor:").pack(pady=(10, 5)); ctk.CTkOptionMenu(appoint_card, values=counselor_names, variable=counselor_var, width=300).pack()
    date_entry = ctk.CTkEntry(appoint_card, placeholder_text="YYYY-MM-DD", width=300); date_entry.pack(pady=(10, 5))
    time_entry = ctk.CTkEntry(appoint_card, placeholder_text="HH:MM", width=300); time_entry.pack(pady=5)
    ctk.CTkButton(appoint_card, text="Create Appointment", command=create_appointment).pack(pady=20)

    ctk.CTkLabel(users_frame, text="Registered System Users", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E293B").pack(pady=20)
    users_card = ctk.CTkScrollableFrame(users_frame, label_text="All Users", fg_color="#FFFFFF", corner_radius=15)
    users_card.pack(padx=30, pady=10, fill="both", expand=True)
    def populate_users():
        for widget in users_card.winfo_children(): widget.destroy()
        conn = get_db_connection(); all_users = conn.execute("SELECT id, name, username, role FROM users").fetchall(); conn.close()
        for u in all_users:
            role_color = {"user": "#3B82F6", "admin": "#EF4444", "counselor": "#10B981"}
            user_frame = ctk.CTkFrame(users_card, fg_color="#F1F5F9", corner_radius=8); user_frame.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(user_frame, text=f"ID: {u[0]} | Name: {u[1]} | Username: {u[2]}", anchor="w").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(user_frame, text=f"{u[3].upper()}", text_color=role_color.get(u[3], "black"), font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)
    populate_users()
    
    show_frame(stats_frame, btn_stats)
