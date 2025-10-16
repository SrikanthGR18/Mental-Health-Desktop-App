import customtkinter as ctk
from db import get_db_connection
from tkinter import messagebox, Toplevel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

def counselor_dashboard(app, counselor_id):
    app.withdraw()
    win = ctk.CTkToplevel(app)
    win.title("MindSync Aura – Counselor Dashboard")
    win.state("zoomed")
    win.after(100, lambda: win.state("zoomed"))
    win.configure(fg_color="#F3F4F6")
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), app.deiconify()))

    # ===== Header =====
    header = ctk.CTkFrame(win, fg_color="#0D9488", height=80, corner_radius=0)
    header.pack(fill="x", side="top")
    ctk.CTkLabel(header, text="🌿 Counselor Dashboard", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(side="left", padx=40, pady=15)
    
    # ===== Sidebar Navigation =====
    sidebar = ctk.CTkFrame(win, width=240, fg_color="#FFFFFF", corner_radius=0)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    def handle_logout():
        win.destroy(); app.deiconify(); app.after(100, lambda: app.state("zoomed"))
    ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="#F87171", hover_color="#DC2626", text_color="white", command=handle_logout).pack(side="bottom", fill="x", padx=25, pady=20)
    
    conn = get_db_connection()
    counselor_name = conn.execute("SELECT name FROM users WHERE id=?", (counselor_id,)).fetchone()[0]
    conn.close()
    
    ctk.CTkLabel(sidebar, text=f"Welcome,\n{counselor_name}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B").pack(pady=(20, 10))

    def set_active(btn):
        for b in buttons: b.configure(fg_color="#E2E8F0", text_color="#334155")
        btn.configure(fg_color="#2563EB", text_color="white")

    def show_frame(frame, button):
        for f in [dashboard_frame, appointments_frame]: f.pack_forget()
        frame.pack(fill="both", expand=True, padx=25, pady=25)
        set_active(button)

    buttons = []
    btn_dashboard = ctk.CTkButton(sidebar, text="📊 Dashboard", fg_color="#2563EB", text_color="white", hover_color="#1D4ED8")
    btn_dashboard.pack(fill="x", padx=25, pady=(15, 5)); buttons.append(btn_dashboard)

    btn_appointments = ctk.CTkButton(sidebar, text="🗓️ Appointments", fg_color="#E2E8F0", text_color="#334155", hover_color="#CBD5E1")
    btn_appointments.pack(fill="x", padx=25, pady=5); buttons.append(btn_appointments)

    # ===== Main Content Area =====
    main_content = ctk.CTkFrame(win, fg_color="#F9FAFB")
    main_content.pack(side="right", fill="both", expand=True)

    dashboard_frame = ctk.CTkFrame(main_content, fg_color="transparent")
    appointments_frame = ctk.CTkFrame(main_content, fg_color="transparent")
    
    btn_dashboard.configure(command=lambda: show_frame(dashboard_frame, btn_dashboard))
    btn_appointments.configure(command=lambda: show_frame(appointments_frame, btn_appointments))
    
    # --- 1. Dashboard Frame Content ---
    ctk.CTkLabel(dashboard_frame, text="At a Glance", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E293B").pack(pady=20)
    stats_container = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
    stats_container.pack(fill="x", padx=20); stats_container.grid_columnconfigure((0,1,2), weight=1)
    today_card = ctk.CTkFrame(stats_container, fg_color="#FFFFFF", corner_radius=15)
    today_card.grid(row=0, column=0, padx=10, sticky="nsew")
    ctk.CTkLabel(today_card, text="Appointments Today", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20,10))
    today_count_label = ctk.CTkLabel(today_card, text="--", font=ctk.CTkFont(size=36, weight="bold"), text_color="#3B82F6"); today_count_label.pack(pady=(0,20))
    completed_card = ctk.CTkFrame(stats_container, fg_color="#FFFFFF", corner_radius=15)
    completed_card.grid(row=0, column=1, padx=10, sticky="nsew")
    ctk.CTkLabel(completed_card, text="Total Completed", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20,10))
    completed_count_label = ctk.CTkLabel(completed_card, text="--", font=ctk.CTkFont(size=36, weight="bold"), text_color="#22C55E"); completed_count_label.pack(pady=(0,20))

    def load_dashboard_stats():
        today_str = datetime.date.today().isoformat()
        conn = get_db_connection()
        today_count = conn.execute("SELECT COUNT(*) FROM appointments WHERE counselor_id=? AND date=? AND status IN ('Scheduled', 'Rescheduled')", (counselor_id, today_str)).fetchone()[0]
        completed_count = conn.execute("SELECT COUNT(*) FROM appointments WHERE counselor_id=? AND status='Completed'", (counselor_id,)).fetchone()[0]
        conn.close(); today_count_label.configure(text=str(today_count)); completed_count_label.configure(text=str(completed_count))

    # --- 2. Appointments Frame Content (Master-Detail) ---
    appointments_frame.grid_columnconfigure(1, weight=3); appointments_frame.grid_rowconfigure(0, weight=1)
    list_panel = ctk.CTkFrame(appointments_frame, fg_color="#FFFFFF", corner_radius=15)
    list_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    ctk.CTkLabel(list_panel, text="Client Sessions", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
    filter_var = ctk.StringVar(value="Upcoming")
    filter_frame = ctk.CTkFrame(list_panel, fg_color="transparent"); filter_frame.pack(fill="x", padx=10, pady=(0, 10))
    ctk.CTkRadioButton(filter_frame, text="Upcoming", variable=filter_var, value="Upcoming", command=lambda: load_appointments()).pack(side="left", expand=True)
    ctk.CTkRadioButton(filter_frame, text="All History", variable=filter_var, value="All", command=lambda: load_appointments()).pack(side="left", expand=True)
    appointment_list_frame = ctk.CTkScrollableFrame(list_panel, fg_color="transparent"); appointment_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
    detail_panel = ctk.CTkFrame(appointments_frame, fg_color="transparent"); detail_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    detail_content_frame = ctk.CTkFrame(detail_panel, fg_color="#FFFFFF", corner_radius=15)
    
    def display_appointment_details(appointment_id):
        for widget in detail_content_frame.winfo_children(): widget.destroy()
        detail_content_frame.pack(fill="both", expand=True)
        conn = get_db_connection(); query = "SELECT a.id, u.name, a.date, a.time, a.status, a.notes, a.user_id FROM appointments a JOIN users u ON a.user_id = u.id WHERE a.id = ?"
        appt = conn.execute(query, (appointment_id,)).fetchone(); conn.close()
        if not appt: return
        appt_id, user_name, date, time, status, notes, user_id = appt
        ctk.CTkLabel(detail_content_frame, text=f"Details for Session #{appt_id}", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 10))
        info_frame = ctk.CTkFrame(detail_content_frame, fg_color="transparent"); info_frame.pack(fill="x", padx=30, pady=10)
        info_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(info_frame, text="Patient:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", pady=4)
        ctk.CTkLabel(info_frame, text=user_name, anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(info_frame, text="Date:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", pady=4)
        ctk.CTkLabel(info_frame, text=f"{date} at {time}", anchor="w").grid(row=1, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(info_frame, text="Status:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", pady=4)
        status_color = {"Scheduled": "#3B82F6", "Completed": "#22C55E", "Rescheduled": "#F59E0B", "Canceled": "#EF4444"}
        ctk.CTkLabel(info_frame, text=status, text_color=status_color.get(status, "black"), anchor="w").grid(row=2, column=1, sticky="ew", padx=10)
        ctk.CTkLabel(detail_content_frame, text="Session Notes", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")
        notes_box = ctk.CTkTextbox(detail_content_frame, height=150, corner_radius=8); notes_box.pack(fill="both", expand=True, padx=20)
        if notes: notes_box.insert("1.0", notes)
        def save_notes():
            new_notes = notes_box.get("1.0", "end-1c"); conn = get_db_connection()
            conn.execute("UPDATE appointments SET notes = ? WHERE id = ?", (new_notes, appt_id)); conn.commit(); conn.close()
            messagebox.showinfo("Success", "Notes have been saved.")
        ctk.CTkButton(detail_content_frame, text="Save Notes", command=save_notes).pack(pady=10)
        ctk.CTkLabel(detail_content_frame, text="Actions", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5), padx=20, anchor="w")
        action_frame = ctk.CTkFrame(detail_content_frame, fg_color="transparent"); action_frame.pack(fill="x", padx=20, pady=10)
        action_frame.grid_columnconfigure((0,1,2,3), weight=1)
        def mark_complete():
            if messagebox.askyesno("Confirm", "Mark session as 'Completed'?"):
                conn = get_db_connection(); conn.execute("UPDATE appointments SET status='Completed' WHERE id=?", (appt_id,)); conn.commit(); conn.close()
                load_appointments(); load_dashboard_stats()
        def cancel_appointment():
            if messagebox.askyesno("Confirm", "Cancel this session?"):
                conn = get_db_connection(); conn.execute("UPDATE appointments SET status='Canceled' WHERE id=?", (appt_id,)); conn.commit(); conn.close()
                load_appointments()
        def open_reschedule_window():
            res_win = ctk.CTkToplevel(win); res_win.title(f"Reschedule for {user_name}"); res_win.geometry("400x300")
            res_win.transient(win); res_win.grab_set()
            ctk.CTkLabel(res_win, text="New Date (YYYY-MM-DD):").pack(pady=(20, 5))
            date_entry = ctk.CTkEntry(res_win, width=200); date_entry.pack()
            ctk.CTkLabel(res_win, text="New Time (HH:MM):").pack(pady=(10, 5))
            time_entry = ctk.CTkEntry(res_win, width=200); time_entry.pack()
            def save_reschedule():
                new_date, new_time = date_entry.get(), time_entry.get()
                if not all([new_date, new_time]): messagebox.showerror("Error", "All fields are required.", parent=res_win); return
                conn = get_db_connection(); conn.execute("UPDATE appointments SET date=?, time=?, status='Rescheduled' WHERE id=?", (new_date, new_time, appt_id)); conn.commit(); conn.close()
                res_win.destroy(); load_appointments()
            ctk.CTkButton(res_win, text="Save Changes", command=save_reschedule).pack(pady=20)
        def view_patient_history():
            history_win = Toplevel(win); history_win.title(f"Stress History for {user_name}"); history_win.geometry("800x600")
            conn = get_db_connection(); data = conn.execute("SELECT date, stress_score FROM entries WHERE user_id=? ORDER BY date", (user_id,)).fetchall(); conn.close()
            if not data: ctk.CTkLabel(history_win, text="No stress entries found for this user.").pack(pady=50); return
            dates, scores = zip(*data); fig, ax = plt.subplots(); ax.plot(dates, scores, marker='o', linestyle='-', color="#4F46E5")
            ax.set_title(f"Stress Trend for {user_name}"); ax.set_xlabel("Date"); ax.set_ylabel("Stress Score")
            fig.autofmt_xdate(); plt.grid(True, alpha=0.3); plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=history_win); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
            history_win.protocol("WM_DELETE_WINDOW", lambda: (plt.close(fig), history_win.destroy()))
        ctk.CTkButton(action_frame, text="Complete", command=mark_complete, fg_color="#22C55E", hover_color="#16A34A").grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(action_frame, text="Reschedule", command=open_reschedule_window, fg_color="#F59E0B", hover_color="#D97706").grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(action_frame, text="Cancel Session", command=cancel_appointment, fg_color="#EF4444", hover_color="#DC2626").grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkButton(action_frame, text="View Patient History", command=view_patient_history, fg_color="#8B5CF6", hover_color="#7C3AED").grid(row=0, column=3, padx=5, sticky="ew")
        
    def load_appointments():
        for widget in appointment_list_frame.winfo_children(): widget.destroy()
        for widget in detail_panel.winfo_children(): widget.pack_forget()
        ctk.CTkLabel(detail_panel, text="Select an appointment from the list\nto view details.", font=ctk.CTkFont(size=16, slant="italic"), text_color="gray").pack(pady=100, padx=20)
        conn = get_db_connection(); filter_choice = filter_var.get()
        if filter_choice == "Upcoming":
            query = "SELECT a.id, u.name, a.date, a.status FROM appointments a JOIN users u ON a.user_id = u.id WHERE a.counselor_id=? AND a.status IN ('Scheduled', 'Rescheduled') ORDER BY a.date, a.time"
        else:
            query = "SELECT a.id, u.name, a.date, a.status FROM appointments a JOIN users u ON a.user_id = u.id WHERE a.counselor_id=? ORDER BY a.date DESC, a.time DESC"
        data = conn.execute(query, (counselor_id,)).fetchall(); conn.close()
        if not data:
            message = "No upcoming appointments." if filter_choice == "Upcoming" else "No appointment history."
            ctk.CTkLabel(appointment_list_frame, text=message, text_color="gray").pack(pady=20); return
        for appt_id, user_name, date, status in data:
            status_color = {"Scheduled": "#3B82F6", "Completed": "#22C55E", "Rescheduled": "#F59E0B", "Canceled": "#EF4444"}
            appt_frame = ctk.CTkFrame(appointment_list_frame, fg_color="#F1F5F9", corner_radius=8, cursor="hand2"); appt_frame.pack(fill="x", padx=10, pady=4)
            def create_lambda(aid): return lambda e: display_appointment_details(aid)
            appt_frame.bind("<Button-1>", create_lambda(appt_id))
            appt_text = f"{user_name}\n{date}"; label = ctk.CTkLabel(appt_frame, text=appt_text, anchor="w"); label.pack(side="left", padx=10, pady=10)
            label.bind("<Button-1>", create_lambda(appt_id))
            status_label = ctk.CTkLabel(appt_frame, text=f"{status}", text_color=status_color.get(status, "black"), font=ctk.CTkFont(weight="bold"))
            status_label.pack(side="right", padx=10); status_label.bind("<Button-1>", create_lambda(appt_id))

    # --- Initial View Setup ---
    load_dashboard_stats()
    show_frame(dashboard_frame, btn_dashboard)