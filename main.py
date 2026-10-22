"""OrbitLink Mission Intelligence - Tkinter desktop application."""
import random
import tkinter as tk
from tkinter import ttk, messagebox

from database import Database
from models import PACKET_TYPES, routing_score
import website


class OrbitLinkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OrbitLink Mission Intelligence")
        self.geometry("1080x720")
        self.minsize(900, 620)
        self.configure(bg="#0b1220")
        self.db = Database()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._style()
        self._build_header()
        self._build_controls()
        self._build_table()
        self._build_footer()
        self.refresh()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background="#121d30", foreground="#edf4ff",
                        fieldbackground="#121d30", rowheight=29, borderwidth=0)
        style.configure("Treeview.Heading", background="#20324b", foreground="#d9e7fb",
                        font=("Segoe UI", 9, "bold"), padding=8)
        style.map("Treeview", background=[("selected", "#244b64")])
        style.configure("TCombobox", fieldbackground="#17263c", background="#17263c",
                        foreground="#edf4ff", padding=5)
        style.configure("TSpinbox", fieldbackground="#17263c", foreground="#edf4ff")

    def _label(self, parent, text, **kwargs):
        return tk.Label(parent, text=text, bg=kwargs.pop("bg", "#121d30"),
                        fg=kwargs.pop("fg", "#9fb1ca"), font=kwargs.pop("font", ("Segoe UI", 9)),
                        **kwargs)

    def _button(self, parent, text, command, bg="#20324b", fg="#edf4ff"):
        return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                         activebackground="#31506e", activeforeground="white",
                         relief="flat", padx=12, pady=8, cursor="hand2",
                         font=("Segoe UI", 9, "bold"))

    def _build_header(self):
        header = tk.Frame(self, bg="#0b1220")
        header.pack(fill="x", padx=24, pady=(20, 12))
        tk.Label(header, text="ORBITLINK  /  MISSION INTELLIGENCE",
                 bg="#0b1220", fg="#61d9e8", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(header, text="Autonomous Downlink Planner", bg="#0b1220", fg="#edf4ff",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", pady=(3, 1))
        tk.Label(header, text="Simulate a short satellite pass and inspect every routing decision.",
                 bg="#0b1220", fg="#9fb1ca", font=("Segoe UI", 10)).pack(anchor="w")

    def _build_controls(self):
        panel = tk.Frame(self, bg="#121d30", highlightbackground="#263750", highlightthickness=1)
        panel.pack(fill="x", padx=24, pady=8)
        tk.Label(panel, text="PACKET INTAKE", bg="#121d30", fg="#61d9e8",
                 font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=8, sticky="w", padx=14, pady=(12, 6))
        self.mode = tk.StringVar(value="TT&C / Health")
        self.size = tk.StringVar(value="240")
        self.urgency = tk.StringVar(value="3")
        ttk.Combobox(panel, textvariable=self.mode, values=list(PACKET_TYPES),
                     state="readonly", width=22).grid(row=1, column=0, padx=(14, 8), pady=(0, 12))
        tk.Entry(panel, textvariable=self.size, width=10, bg="#17263c", fg="#edf4ff",
                 insertbackground="white", relief="flat").grid(row=1, column=1, padx=8, ipady=8, pady=(0, 12))
        tk.Spinbox(panel, from_=1, to=5, textvariable=self.urgency, width=5,
                   bg="#17263c", fg="#edf4ff", buttonbackground="#20324b",
                   relief="flat").grid(row=1, column=2, padx=8, ipady=5, pady=(0, 12))
        self._button(panel, "＋ Add packet", self.add_packet, "#61d9e8", "#07111f").grid(row=1, column=3, padx=8, pady=(0, 12))
        self._button(panel, "Generate test queue", self.add_sample, "#20324b").grid(row=1, column=4, padx=8, pady=(0, 12))
        self._button(panel, "Run 60-second pass", self.run_pass, "#a99bff", "#101128").grid(row=1, column=5, padx=8, pady=(0, 12))
        self._button(panel, "Build report", self.build_report, "#174c4b").grid(row=1, column=6, padx=8, pady=(0, 12))
        self._button(panel, "Reset", self.reset, "#4b2b3a").grid(row=1, column=7, padx=(8, 14), pady=(0, 12))
        for col in range(8):
            panel.grid_columnconfigure(col, weight=1 if col in (0, 4) else 0)
        self.status = tk.Label(self, text="Ready. Add packets or generate a test queue.",
                               bg="#0b1220", fg="#9fb1ca", font=("Segoe UI", 9), anchor="w")
        self.status.pack(fill="x", padx=26, pady=(5, 2))

    def _build_table(self):
        title = tk.Frame(self, bg="#0b1220")
        title.pack(fill="x", padx=24, pady=(10, 7))
        tk.Label(title, text="Packet ledger", bg="#0b1220", fg="#edf4ff",
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(title, text="WAITING  ·  SENT  ·  DEFERRED", bg="#0b1220", fg="#9fb1ca",
                 font=("Segoe UI", 8, "bold")).pack(side="right")
        holder = tk.Frame(self, bg="#121d30")
        holder.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        cols = ("id", "mode", "size", "urgency", "status", "reason")
        self.table = ttk.Treeview(holder, columns=cols, show="headings")
        headings = {"id": "ID", "mode": "DATA MODE", "size": "SIZE (BYTES)",
                    "urgency": "URGENCY", "status": "STATUS", "reason": "ROUTING EXPLANATION"}
        widths = {"id": 55, "mode": 190, "size": 105, "urgency": 80, "status": 95, "reason": 450}
        for col in cols:
            self.table.heading(col, text=headings[col])
            self.table.column(col, width=widths[col], anchor="w" if col in ("mode", "reason") else "center")
        self.table.tag_configure("SENT", foreground="#7de2c4")
        self.table.tag_configure("DEFERRED", foreground="#ffc58a")
        self.table.tag_configure("WAITING", foreground="#b6c9e7")
        yscroll = ttk.Scrollbar(holder, orient="vertical", command=self.table.yview)
        xscroll = ttk.Scrollbar(holder, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        holder.rowconfigure(0, weight=1)
        holder.columnconfigure(0, weight=1)

    def _build_footer(self):
        foot = tk.Frame(self, bg="#0b1220")
        foot.pack(fill="x", padx=24, pady=(0, 15))
        tk.Label(foot, text="POLICY  TT&C  →  SSTV  →  M17 / Codec2",
                 bg="#0b1220", fg="#61d9e8", font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Label(foot, text="Tkinter controls · SQLite persistence · HTML report",
                 bg="#0b1220", fg="#7286a2", font=("Segoe UI", 8)).pack(side="right")

    def refresh(self):
        self.table.delete(*self.table.get_children())
        for row in self.db.get_packets():
            self.table.insert("", "end", values=row, tags=(row[4],))

    def add_packet(self):
        try:
            size = int(self.size.get())
            urgency = int(self.urgency.get())
            if size <= 0 or not 1 <= urgency <= 5:
                raise ValueError("Size must be positive and urgency must be 1–5.")
            self.db.add_packet(self.mode.get(), size, urgency)
            self.status.config(text=f"Added {self.mode.get()} packet ({size} bytes).")
        except ValueError as exc:
            messagebox.showerror("Invalid packet", str(exc) if str(exc) else "Enter whole numbers.")
            return
        self.refresh()

    def add_sample(self):
        examples = [
            ("TT&C / Health", 180, 5), ("TT&C / Health", 120, 4),
            ("SSTV Image", 1400, 3), ("SSTV Image", 950, 2),
            ("M17 / Codec2 Voice", 420, 3), ("M17 / Codec2 Voice", 300, 1),
        ]
        for mode, size, urgency in examples:
            self.db.add_packet(mode, size, urgency)
        self.refresh()
        self.status.config(text="Six demonstration packets added to the SQLite queue.")

    def run_pass(self):
        packets = [row for row in self.db.get_packets() if row[4] != "SENT"]
        if not packets:
            messagebox.showinfo("Queue empty", "Add packets before running a pass.")
            return
        signal = random.randint(20, 100)
        battery = random.randint(10, 100)
        remaining = 60.0
        sent = 0
        deferred = 0
        evaluated = []
        for row in packets:
            packet_cls = PACKET_TYPES[row[1]]
            packet = packet_cls(row[2], row[3])
            score = routing_score(packet, signal, battery)
            evaluated.append((row[0], packet, score))
        # Highest heuristic score first; TT&C remains the critical traffic class.
        evaluated.sort(key=lambda item: item[2], reverse=True)
        for packet_id, packet, score in evaluated:
            duration = packet.transmission_seconds(signal)
            if signal < packet.minimum_link():
                reason = f"Deferred: signal {signal}% below required {packet.minimum_link()}%."
                self.db.update_packet(packet_id, "DEFERRED", reason)
                deferred += 1
            elif battery < 8:
                reason = "Deferred: battery below safe transmission threshold (8%)."
                self.db.update_packet(packet_id, "DEFERRED", reason)
                deferred += 1
            elif score < 0:
                reason = "Deferred by resource-aware routing policy."
                self.db.update_packet(packet_id, "DEFERRED", reason)
                deferred += 1
            elif duration > remaining:
                reason = f"Deferred: needs {duration:.1f}s; only {remaining:.1f}s remain."
                self.db.update_packet(packet_id, "DEFERRED", reason)
                deferred += 1
            else:
                remaining -= duration
                self.db.update_packet(
                    packet_id, "SENT",
                    f"Sent: score {score:.0f}, link {signal}%, battery {battery}%, time {duration:.1f}s."
                )
                sent += 1
        self.db.add_session(signal, battery, sent, deferred, round(60 - remaining, 1))
        self.refresh()
        self.status.config(text=f"Pass complete · link {signal}% · battery {battery}% · {sent} sent · {deferred} deferred · {remaining:.1f}s left.")

    def build_report(self):
        path = website.build_report(self.db)
        self.status.config(text=f"Read-only HTML report generated: {path}")

    def reset(self):
        if messagebox.askyesno("Reset mission data", "Delete all packet and session records from SQLite?"):
            self.db.reset()
            self.refresh()
            self.status.config(text="Mission queue and session history reset.")

    def on_close(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    OrbitLinkApp().mainloop()
