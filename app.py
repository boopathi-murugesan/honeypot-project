from flask import Flask, request, render_template, Response, stream_with_context
import logging, os, subprocess, threading, datetime, platform, time

app = Flask(__name__)

# === Ensure logs folder exists ===
if not os.path.exists("logs"):
    os.makedirs("logs")

# === Logging Setup ===
logging.basicConfig(
    filename="logs/honeypot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True  # Flush any existing handlers and reconfigure
)

# === Packet Capture Thread ===
def start_packet_capture():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pcap_file = f"logs/capture_{timestamp}.pcap"

    if platform.system() == "Windows":
        windump_path = os.path.join(os.getcwd(), "WinDump.exe")
        if not os.path.exists(windump_path):
            print("[!] WinDump not found. Packet capture skipped.")
            return
        subprocess.Popen(
            [windump_path, "-i", "1", "-w", pcap_file, "port 22 or port 80 or port 8080 or port 21"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("[*] WinDump packet capture started.")
    else:
        subprocess.Popen(
            ["tcpdump", "-i", "any", "-w", pcap_file, "port 22 or port 80 or port 8080 or port 21"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("[*] tcpdump packet capture started.")

# === Routes ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    ip = request.remote_addr
    ua = request.headers.get("User-Agent")
    logging.warning(f"Unauthorized /admin access - IP: {ip}, UA: {ua}")
    return render_template("admin.html"), 403

@app.route("/login", methods=["GET", "POST"])
def login():
    ip = request.remote_addr
    ua = request.headers.get("User-Agent")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        logging.info(f"Login attempt - IP: {ip}, Username: {username}, Password: {password}, UA: {ua}")
        return render_template("admin.html"), 403
    return render_template("login.html")

@app.route("/logs")
def view_logs():
    return render_template("logs.html")

@app.route("/stream")
def stream_logs():
    def generate():
        logfile = "logs/honeypot.log"
        with open(logfile, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    yield f"data: {line.strip()}\n\n"
                else:
                    time.sleep(0.5)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

# === Entrypoint ===
if __name__ == "__main__":
    threading.Thread(target=start_packet_capture, daemon=True).start()
    app.run(host="0.0.0.0", port=8080)
