"""Generate a read-only HTML mission report from SQLite data."""
from html import escape
from pathlib import Path
import webbrowser

SITE_PATH = Path(__file__).resolve().parent / "website" / "mission_report.html"


def build_report(db, open_browser=True):
    rows = db.get_packets()
    sessions = db.get_sessions()
    sent = sum(row[4] == "SENT" for row in rows)
    deferred = sum(row[4] == "DEFERRED" for row in rows)
    waiting = sum(row[4] == "WAITING" for row in rows)
    latest = sessions[0] if sessions else None
    signal = latest[1] if latest else 0
    battery = latest[2] if latest else 0
    signal_colour = "#20c997" if signal >= 60 else "#f0b45a" if signal >= 35 else "#ff7185"

    packet_rows = []
    for row in rows:
        packet_rows.append(
            "<tr><td>{}</td><td>{}</td><td>{:,} B</td><td>{}</td>"
            "<td><span class='status {}'>{}</span></td><td>{}</td></tr>".format(
                row[0], escape(row[1]), row[2], row[3], row[4].lower(),
                escape(row[4]), escape(row[5] or "No decision yet")
            )
        )
    if not packet_rows:
        packet_rows.append("<tr><td colspan='6' class='empty'>No packets have been added. Use the desktop app to create a test queue.</td></tr>")

    history_rows = []
    for session in sessions:
        history_rows.append(
            "<tr><td>#{}</td><td>{}%</td><td>{}%</td><td>{}</td><td>{}</td><td>{:.1f}s</td><td>{}</td></tr>".format(
                session[0], session[1], session[2], session[3], session[4],
                session[5], escape(session[6])
            )
        )
    if not history_rows:
        history_rows.append("<tr><td colspan='7' class='empty'>No downlink sessions recorded yet.</td></tr>")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OrbitLink | Mission Intelligence Report</title>
<style>
:root{{--bg:#0b1220;--panel:#121d30;--panel2:#17263c;--text:#edf4ff;--muted:#9fb1ca;--line:#263750;--cyan:#61d9e8;--violet:#a99bff}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 12% 0%,#182e4b 0,#0b1220 42%);color:var(--text);font:15px/1.5 Inter,Segoe UI,Arial,sans-serif}}
header{{padding:30px max(20px,calc((100% - 1120px)/2));border-bottom:1px solid var(--line);background:#0b1220cc}}
.brand{{display:flex;gap:14px;align-items:center}} .mark{{width:48px;height:48px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(135deg,#61d9e8,#8e86ff);color:#07111f;font-size:25px;font-weight:900}}
h1{{margin:0;font-size:clamp(24px,4vw,34px);letter-spacing:-.8px}} .sub{{color:var(--muted);margin:5px 0 0}}
main{{max-width:1120px;margin:0 auto;padding:26px 20px 50px}}
.kicker{{color:var(--cyan);text-transform:uppercase;letter-spacing:2px;font-size:11px;font-weight:800}}
.section-head{{display:flex;justify-content:space-between;align-items:end;gap:12px;margin:26px 0 12px}} h2{{font-size:18px;margin:0}} .hint{{font-size:12px;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}} .metric,.panel{{background:linear-gradient(150deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 10px 30px #0002}}
.metric span{{display:block;color:var(--muted);font-size:12px}} .metric strong{{display:block;font-size:30px;margin:5px 0 0;letter-spacing:-1px}} .metric small{{color:var(--cyan)}}
.signal-layout{{display:grid;grid-template-columns:1.1fr .9fr;gap:13px}} .signal-num{{font-size:36px;font-weight:800}} .bar{{height:10px;border-radius:20px;background:#27364c;overflow:hidden;margin:12px 0}} .bar i{{display:block;height:100%;width:{signal}%;background:{signal_colour};border-radius:20px}}
.battery{{color:#a99bff}} .pill{{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:5px 10px;color:var(--muted);font-size:11px}}
.route-list{{display:grid;gap:10px;margin-top:15px}} .route{{display:flex;align-items:center;gap:12px}} .num{{display:grid;place-items:center;width:30px;height:30px;border-radius:9px;background:#21344d;color:var(--cyan);font-weight:800}} .route b{{display:block}} .route small{{color:var(--muted)}}
.table-wrap{{overflow-x:auto;border:1px solid var(--line);border-radius:14px}} table{{width:100%;border-collapse:collapse;min-width:720px;background:#101a2b}} th{{text-align:left;background:#1b2b42;color:#b8c9df;font-size:11px;text-transform:uppercase;letter-spacing:.8px}} th,td{{padding:12px 14px;border-bottom:1px solid var(--line)}} tr:last-child td{{border-bottom:0}} td{{font-size:13px}} .status{{padding:4px 8px;border-radius:7px;font-size:10px;font-weight:800;letter-spacing:.4px}} .sent{{background:#143d3c;color:#7de2c4}} .deferred{{background:#493326;color:#ffc58a}} .waiting{{background:#263650;color:#b6c9e7}} .empty{{text-align:center;color:var(--muted);padding:28px}}
.note{{margin-top:20px;color:var(--muted);font-size:12px}} footer{{border-top:1px solid var(--line);padding:20px;text-align:center;color:var(--muted);font-size:12px}}
@media(max-width:760px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.signal-layout{{grid-template-columns:1fr}}}}
@media(max-width:420px){{.grid{{grid-template-columns:1fr 1fr}}.metric{{padding:13px}}.metric strong{{font-size:24px}}}}
</style></head>
<body>
<header><div class="brand"><div class="mark">O</div><div><h1>OrbitLink Mission Intelligence</h1>
<p class="sub">Autonomous downlink planning · SomaiyaSat / SomaiyaPod simulation</p></div></div></header>
<main>
<div class="kicker">Mission overview / local report</div>
<div class="section-head"><h2>Traffic at a glance</h2><span class="pill">Read-only generated report</span></div>
<div class="grid">
<div class="metric"><span>Packets in queue</span><strong>{len(rows)}</strong><small>All data modes</small></div>
<div class="metric"><span>Successfully sent</span><strong>{sent}</strong><small>Completed transmissions</small></div>
<div class="metric"><span>Deferred</span><strong>{deferred}</strong><small>Needs another opportunity</small></div>
<div class="metric"><span>Waiting</span><strong>{waiting}</strong><small>Not yet evaluated</small></div>
</div>
<div class="section-head"><h2>Link and energy snapshot</h2><span class="hint">From latest simulated pass</span></div>
<div class="signal-layout">
<section class="panel"><div class="kicker">Radio link quality</div><div class="signal-num">{signal}%</div><div class="bar"><i></i></div><span class="hint">Stronger links generally allow more data to be sent.</span></section>
<section class="panel"><div class="kicker">Power reserve</div><div class="signal-num battery">{battery}%</div><div class="bar"><i style="width:{battery}%;background:#a99bff"></i></div><span class="hint">The simulator reduces non-critical traffic priority when battery is low.</span></section>
</div>
<div class="section-head"><h2>Routing policy</h2><span class="hint">Priority + link + power + time</span></div>
<section class="panel"><div class="route-list">
<div class="route"><div class="num">01</div><div><b>TT&amp;C / housekeeping</b><small>Critical satellite health and command data is prioritised.</small></div></div>
<div class="route"><div class="num">02</div><div><b>SSTV imagery</b><small>Image traffic needs a stronger simulated signal.</small></div></div>
<div class="route"><div class="num">03</div><div><b>M17 / Codec2 voice and data</b><small>Voice traffic uses remaining link time when eligible.</small></div></div>
</div><p class="note">This is an explainable AI-inspired heuristic simulation, not a trained flight-qualified model. Real spacecraft deployment would require validation, safe fallback logic, and hardware-in-the-loop testing.</p></section>
<div class="section-head"><h2>Packet ledger</h2><span class="hint">Stored in SQLite</span></div>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Data mode</th><th>Size</th><th>Urgency</th><th>Status</th><th>Decision explanation</th></tr></thead><tbody>{''.join(packet_rows)}</tbody></table></div>
<div class="section-head"><h2>Downlink session history</h2><span class="hint">Most recent first</span></div>
<div class="table-wrap"><table><thead><tr><th>Session</th><th>Signal</th><th>Battery</th><th>Sent</th><th>Deferred</th><th>Time used</th><th>Timestamp</th></tr></thead><tbody>{''.join(history_rows)}</tbody></table></div>
<p class="note">To change data or run another pass, use the OrbitLink desktop application. This HTML page is a generated report and contains no interactive controls.</p>
</main><footer>OrbitLink Mission Intelligence · OOP with Python · Tkinter + SQLite</footer></body></html>"""

    SITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SITE_PATH.write_text(html, encoding="utf-8")
    if open_browser:
        webbrowser.open(SITE_PATH.resolve().as_uri())
    return str(SITE_PATH)
