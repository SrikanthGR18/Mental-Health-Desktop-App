import customtkinter as ctk
from tkinter import messagebox
from db import get_db_connection
from stress_calc import analyze_sentiment, calculate_stress
from tips import get_tip
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

def user_dashboard(app, user_id):
    app.withdraw()
    win = ctk.CTkToplevel(app)
    win.title("MindSync Aura – Wellness Dashboard")
    win.state("zoomed")
    win.after(100, lambda: win.state("zoomed"))
    win.configure(fg_color="#F3F4F6")
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), app.deiconify()))

    header_colors = ["#4F46E5", "#0EA5E9", "#06B6D4", "#14B8A6"]
    gradient_frame = ctk.CTkFrame(win, fg_color=random.choice(header_colors), height=80, corner_radius=0)
    gradient_frame.pack(fill="x", side="top")
    ctk.CTkLabel(gradient_frame, text="🌸 MindSync Aura", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(side="left", padx=40, pady=15)
    ctk.CTkLabel(gradient_frame, text="Your personal calm space.", font=ctk.CTkFont(size=16), text_color="white").pack(side="right", padx=40)

    sidebar = ctk.CTkFrame(win, width=230, fg_color="#FFFFFF", corner_radius=0)
    sidebar.pack(side="left", fill="y"); sidebar.pack_propagate(False)
    ctk.CTkLabel(sidebar, text="🧭 Navigation", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B").pack(pady=(20, 5))

    def set_active(btn):
        for b in buttons: b.configure(fg_color="#E2E8F0", text_color="#334155")
        btn.configure(fg_color="#2563EB", text_color="white")

    def show_frame(frame, button):
        for f in [home_frame, journal_frame, graph_frame]: f.pack_forget()
        frame.pack(fill="both", expand=True, padx=25, pady=25); set_active(button)

    buttons = []
    btn_home = ctk.CTkButton(sidebar, text="🏠 Home", fg_color="#2563EB", text_color="white", hover_color="#1D4ED8", command=lambda: show_frame(home_frame, btn_home))
    btn_home.pack(fill="x", padx=25, pady=(15, 5)); buttons.append(btn_home)
    btn_journal = ctk.CTkButton(sidebar, text="📝 Journal", fg_color="#E2E8F0", text_color="#334155", hover_color="#CBD5E1", command=lambda: show_frame(journal_frame, btn_journal))
    btn_journal.pack(fill="x", padx=25, pady=5); buttons.append(btn_journal)
    btn_graph = ctk.CTkButton(sidebar, text="📊 Trends", fg_color="#E2E8F0", text_color="#334155", hover_color="#CBD5E1", command=lambda: show_frame(graph_frame, btn_graph))
    btn_graph.pack(fill="x", padx=25, pady=5); buttons.append(btn_graph)
    
    def handle_logout():
        win.destroy(); app.deiconify(); app.after(100, lambda: app.state("zoomed"))
    ctk.CTkButton(sidebar, text="🚪 Logout", fg_color="#F87171", hover_color="#DC2626", text_color="white", command=handle_logout).pack(side="bottom", fill="x", padx=25, pady=20)

    main_frame = ctk.CTkFrame(win, fg_color="#F9FAFB")
    main_frame.pack(side="right", fill="both", expand=True)
    home_frame = ctk.CTkFrame(main_frame, fg_color="#F9FAFB")
    journal_frame = ctk.CTkFrame(main_frame, fg_color="#F9FAFB")
    graph_frame = ctk.CTkFrame(main_frame, fg_color="#F9FAFB")

    ctk.CTkLabel(home_frame, text="Welcome to MindSync 🌿", font=ctk.CTkFont(size=26, weight="bold"), text_color="#1E293B").pack(pady=15)
    ctk.CTkLabel(home_frame, text="Reflect. Record. Rejuvenate.\nEvery entry brings you closer to better balance.", font=ctk.CTkFont(size=16), text_color="#475569").pack(pady=5)
    stats_card = ctk.CTkFrame(home_frame, fg_color="#FFFFFF", corner_radius=15)
    stats_card.pack(padx=40, pady=40, fill="x")
    ctk.CTkLabel(stats_card, text="Overall Stress Level", font=ctk.CTkFont(size=20, weight="bold"), text_color="#1E293B").pack(pady=10)
    stat_label = ctk.CTkLabel(stats_card, text="Calculating...", font=ctk.CTkFont(size=22))
    stat_label.pack(pady=5)
    def refresh_stats():
        conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT stress_score FROM entries WHERE user_id=?", (user_id,)); data = cur.fetchall(); conn.close()
        if not data: stat_label.configure(text="No entries yet 🌸"); return
        avg = round(sum(d[0] for d in data) / len(data), 2)
        mood = "💖 Low" if avg < 0.4 else "😐 Medium" if avg < 0.7 else "🔥 High"; stat_label.configure(text=f"{avg} ({mood})")
    ctk.CTkButton(stats_card, text="🔄 Refresh", fg_color="#06B6D4", hover_color="#0891B2", command=refresh_stats).pack(pady=10)

    ctk.CTkLabel(journal_frame, text="Write Your Daily Reflection ✨", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E293B").pack(pady=20)
    input_card = ctk.CTkFrame(journal_frame, fg_color="#FFFFFF", corner_radius=15); input_card.pack(padx=30, pady=10, fill="x")
    labels = ["Sleep Quality (0–10):", "Workload (0–10):", "Energy Level (0–10):", "Mood (0–10):"]; entries = []
    for text in labels:
        frame = ctk.CTkFrame(input_card, fg_color="transparent"); frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=text, width=180, anchor="w", font=ctk.CTkFont(size=14)).pack(side="left", padx=15)
        e = ctk.CTkEntry(frame, width=100); e.pack(side="left", padx=10); entries.append(e)
    ctk.CTkLabel(journal_frame, text="How was your day?", font=ctk.CTkFont(size=16)).pack(pady=(20, 5))
    text_journal = ctk.CTkTextbox(journal_frame, height=150, corner_radius=12); text_journal.pack(padx=30, pady=10, fill="x")
    def submit_entry():
        try:
            vals = [int(e.get()) for e in entries]
            if not all(0 <= v <= 10 for v in vals): messagebox.showerror("Error", "Please enter values between 0–10."); return
            journal = text_journal.get("1.0", "end").strip()
            if not journal: messagebox.showerror("Error", "Please write your journal entry."); return
            sentiment = analyze_sentiment(journal); stress = calculate_stress(*vals, sentiment); date = datetime.date.today().isoformat()
            conn = get_db_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO entries (user_id, date, sleep, workload, energy, mood, journal, sentiment, stress_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (user_id, date, *vals, journal, sentiment, stress))
            conn.commit(); conn.close()
            tip_level = "high" if stress > 0.7 else "medium" if stress > 0.4 else "low"
            messagebox.showinfo("Saved ✅", f"Stress Score: {stress}\n\nTip: {get_tip(tip_level)}")
            for e in entries: e.delete(0, "end")
            text_journal.delete("1.0", "end"); refresh_stats()
        except ValueError: messagebox.showerror("Error", "All inputs must be numbers between 0–10.")
        except Exception as e: messagebox.showerror("Error", f"Something went wrong:\n{e}")
    ctk.CTkButton(journal_frame, text="💾 Save Entry", fg_color="#22C55E", hover_color="#16A34A", command=submit_entry, width=150).pack(pady=15)

    ctk.CTkLabel(graph_frame, text="Your Stress Journey 📊", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1E293B").pack(pady=20)
    graph_display_frame = ctk.CTkFrame(graph_frame, fg_color="#FFFFFF", corner_radius=15)
    graph_display_frame.pack(padx=30, pady=10, fill="both", expand=True)
    def show_graph():
        conn = get_db_connection(); cur = conn.cursor(); cur.execute("SELECT date, stress_score FROM entries WHERE user_id=? ORDER BY date", (user_id,)); data = cur.fetchall(); conn.close()
        if not data: messagebox.showinfo("No Data", "Add a few entries to see your progress."); return
        for widget in graph_display_frame.winfo_children(): widget.destroy()
        dates, scores = zip(*data); fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(dates, scores, color="#4F46E5", linewidth=2.5, marker="o", markerfacecolor="#A78BFA")
        ax.fill_between(dates, scores, color="#A5B4FC", alpha=0.3)
        ax.set_xlabel("Date", fontsize=10); ax.set_ylabel("Stress Level", fontsize=10); ax.set_title("Stress Levels Over Time", fontsize=14, weight="bold")
        ax.grid(alpha=0.3); plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=graph_display_frame); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    ctk.CTkButton(graph_frame, text="📈 Show My Progress", fg_color="#8B5CF6", hover_color="#7C3AED", command=show_graph).pack(pady=10)
    
    refresh_stats()
    show_frame(home_frame, btn_home)