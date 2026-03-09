"""
A minimal HTTP server for listing AI/ML competitions and recording selections.

This script uses Python's built-in ``http.server`` to serve a dynamic page
displaying a list of ongoing or upcoming data science, machine learning,
and AI competitions with prize money. The home page shows "Projects for
the day" using the current date. Each competition has a link that
triggers a selection action; when clicked the server appends a log entry
to ``selected_projects.txt`` and returns a confirmation page.

To run the server locally:

    python server.py

Then navigate to ``http://localhost:8000`` in your browser.

This server does not require any third party dependencies.
"""

from __future__ import annotations

import http.server
import os
import urllib.parse
from datetime import date, datetime
from typing import Dict, List, Optional


# Data definition
competitions: List[Dict[str, str]] = [
    {
        "id": "1",
        "name": "Hull Tactical Market Prediction",
        "platform": "Kaggle",
        "start_date": "2025-09-16",
        "end_date": "2026-06-16",
        "prize": "$50k first, $25k second, $10k third, $5k for 4th-6th",
        "link": "https://www.kaggle.com/competitions/hull-tactical-market-prediction",
    },
    {
        "id": "2",
        "name": "March Machine Learning Mania 2026",
        "platform": "Kaggle",
        "start_date": "2026-03-15",
        "end_date": "2026-04-08",
        "prize": "$10k first, $8k second, $7k third, $5k for 4th-8th",
        "link": "https://www.kaggle.com/competitions/march-machine-learning-mania-2026",
    },
    {
        "id": "3",
        "name": "AI Mathematical Olympiad Progress Prize 3",
        "platform": "Kaggle",
        "start_date": "2026-01-15",
        "end_date": "2026-03-31",
        "prize": "$262k first, $131k second, $65k third, other prizes up to $1.6M",
        "link": "https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-3",
    },
    {
        "id": "4",
        "name": "ARC Prize 2025",
        "platform": "Kaggle",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "prize": "$125k progress prizes, $700k grand prize, $175k other prizes",
        "link": "https://www.kaggle.com/competitions/arc-prize-2025",
    },
    {
        "id": "5",
        "name": "MedGemma Impact Challenge",
        "platform": "Kaggle",
        "start_date": "2026-01-13",
        "end_date": "2026-02-24",
        "prize": "$30k first, $20k second, $15k third, $10k fourth, plus special prizes",
        "link": "https://www.kaggle.com/competitions/medgemma-impact-challenge",
    },
    {
        "id": "6",
        "name": "Stanford RNA 3D Folding (Part 2)",
        "platform": "Kaggle",
        "start_date": "2025-11-01",
        "end_date": "2026-03-31",
        "prize": "$50k first, $15k second, $10k third",
        "link": "https://www.kaggle.com/competitions/stanford-rna-3d-folding-part-2",
    },
    {
        "id": "7",
        "name": "Deep Past Challenge: Akkadian to English",
        "platform": "Kaggle",
        "start_date": "2026-01-08",
        "end_date": "2026-03-04",
        "prize": "$15k first, $10k second, $8k third, $7k fourth, $5k for 5th-6th",
        "link": "https://www.kaggle.com/competitions/deep-past-challenge-akkadian-to-english",
    },
    {
        "id": "8",
        "name": "PowerSync AI Hackathon",
        "platform": "Hackathon",
        "start_date": "2026-03-06",
        "end_date": "2026-03-20",
        "prize": "$3k first, $1k second, $500 third; plus $500 category bonuses",
        "link": "https://powersync.ai/blog/ai-hackathon",
    },
    {
        "id": "9",
        "name": "Rise of AI Agents Hackathon",
        "platform": "Lablab.ai",
        "start_date": "2026-04-06",
        "end_date": "2026-04-11",
        "prize": "$60k+ prize pool, with on-site finals in Dubai",
        "link": "https://lablab.ai/event/ai-agents-hackathon",
    },
    {
        "id": "10",
        "name": "USAII Global AI Hackathon",
        "platform": "USAII",
        "start_date": "2026-02-20",
        "end_date": "2026-03-20",
        "prize": "$6k high school prize, $9k college/graduate prize, scholarships",
        "link": "https://usaai.org/global-ai-hackathon",
    },
    {
        "id": "11",
        "name": "Iqigai AI Fellowship Challenge",
        "platform": "Analytics Vidhya",
        "start_date": "2026-01-20",
        "end_date": "2026-03-15",
        "prize": "20L INR prize pool (₹5L first, ₹3L second, ₹2L third, ₹10L for ranks 4-1000)",
        "link": "https://iqigai.com/fellowship-challenge",
    },
    {
        "id": "12",
        "name": "RevenueCat Shipyard Contest",
        "platform": "Devpost",
        "start_date": "2026-02-01",
        "end_date": "2026-03-31",
        "prize": "$20k cash prize for each of 7 winning apps, $5k runner‑up draw",
        "link": "https://devpost.com/revenuecat-shipyard-2026",
    },
    {
        "id": "13",
        "name": "Zerve AI Hackathon",
        "platform": "Devpost",
        "start_date": "2026-02-15",
        "end_date": "2026-03-15",
        "prize": "$5k first, $3k second, $2k third",
        "link": "https://devpost.com/hackathons/zerve-ai-2026",
    },
    {
        "id": "14",
        "name": "Live AI Ivy Plus 2026",
        "platform": "Live AI Ivy Plus",
        "start_date": "2026-01-25",
        "end_date": "2026-04-30",
        "prize": "$137.6k+ prize pool, including trips and investment opportunities",
        "link": "https://liveai.com/ivyplus2026",
    },
    {
        "id": "15",
        "name": "Microsoft Imagine Cup 2026",
        "platform": "Microsoft",
        "start_date": "2025-09-05",
        "end_date": "2026-01-09",
        "prize": "$100k world champion, $50k launch track, $1k Azure credits for participants",
        "link": "https://imaginecup.microsoft.com/en-us/Competition/2026",
    },
]


def parse_date(date_str: str) -> date:
    return datetime.strptime(date_str, "%Y-%m-%d").date()


class CompetitionRequestHandler(http.server.BaseHTTPRequestHandler):
    """Request handler for the competition listing web server."""

    def _send_response(self, content: str, status: int = 200, content_type: str = "text/html") -> None:
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))

    def log_message(self, format: str, *args: str) -> None:
        """Override to suppress logging to stderr during normal operation."""
        return

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "":
            self.handle_index()
        elif path == "/select":
            self.handle_select(query)
        else:
            self._send_response("<h1>404 Not Found</h1>", status=404)

    def handle_index(self) -> None:
        """Serve the home page with current competitions."""
        today = date.today()
        current_comps = [c for c in competitions if parse_date(c["end_date"]) >= today]
        current_comps.sort(key=lambda c: c["start_date"])

        # Build HTML content
        html_parts: List[str] = []
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang=\"en\">\n<head>")
        html_parts.append("<meta charset=\"UTF-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">")
        html_parts.append("<title>Projects for the day – {}</title>".format(today))
        # inline styles for simplicity
        html_parts.append("<style>\n"
                          "body{font-family:Arial,Helvetica,sans-serif;background:#f9f9f9;margin:0;padding:0;}\n"
                          "header{background:#2c3e50;color:#fff;padding:20px;text-align:center;}\n"
                          "main{padding:20px;}\n"
                          ".comp{background:#fff;border:1px solid #ddd;border-radius:8px;padding:15px;margin-bottom:15px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}\n"
                          ".comp h3{margin:0 0 8px;}\n"
                          ".comp p{margin:4px 0;}\n"
                          ".button{display:inline-block;margin-top:10px;padding:8px 12px;background:#2980b9;color:#fff;text-decoration:none;border-radius:4px;}\n"
                          ".button:hover{background:#1f6391;}\n"
                          "</style>")
        html_parts.append("</head>\n<body>")
        html_parts.append(f"<header><h1>Projects for the day – {today}</h1></header>")
        html_parts.append("<main>")
        if current_comps:
            for comp in current_comps:
                html_parts.append("<div class=\"comp\">")
                html_parts.append(f"<h3>{comp['name']}</h3>")
                html_parts.append(f"<p><strong>Platform:</strong> {comp['platform']}</p>")
                html_parts.append(f"<p><strong>Start:</strong> {comp['start_date']} &nbsp; | &nbsp; <strong>End:</strong> {comp['end_date']}</p>")
                html_parts.append(f"<p><strong>Prize:</strong> {comp['prize']}</p>")
                html_parts.append(f"<p><a href='{comp['link']}' target='_blank'>Official competition page</a></p>")
                html_parts.append(f"<a href='/select?id={comp['id']}' class='button'>Select this project</a>")
                html_parts.append("</div>")
        else:
            html_parts.append("<p>No competitions available today. Please check back later.</p>")
        # Add a section to display project progress.  We read the 'progress.md'
        # file (if it exists) and escape its contents so it can be safely
        # embedded as HTML.  Newlines are converted to <br> tags for basic
        # formatting.  If the file cannot be read or is absent, we show a
        # placeholder message.  This allows users to track what has been done
        # and what remains directly from the website.
        import html as _html  # use a local alias to avoid global namespace pollution
        progress_path = os.path.join(os.path.dirname(__file__), "progress.md")
        if os.path.exists(progress_path):
            try:
                with open(progress_path, "r", encoding="utf-8") as pf:
                    progress_md = pf.read()
                progress_html = _html.escape(progress_md).replace("\n", "<br>")
            except Exception:
                progress_html = "Could not load progress information."
        else:
            progress_html = "No progress has been recorded yet."
        html_parts.append("<section style='margin-top:30px;'>")
        html_parts.append("<h2>Project Progress</h2>")
        html_parts.append(f"<p>{progress_html}</p>")
        html_parts.append("</section>")

        html_parts.append("</main>")
        html_parts.append("</body></html>")
        html = "\n".join(html_parts)
        self._send_response(html)

    def handle_select(self, query: Dict[str, List[str]]) -> None:
        """Handle a competition selection; log and respond."""
        comp_id: Optional[str] = query.get("id", [None])[0]
        comp: Optional[Dict[str, str]] = None
        if comp_id:
            comp = next((c for c in competitions if c["id"] == comp_id), None)
        if comp:
            # Log the selection
            log_path = os.path.join(os.path.dirname(__file__), "selected_projects.txt")
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | Selected: {comp['name']}\n")
            message = (
                f"<p>You selected '<strong>{comp['name']}</strong>'. "
                "Your selection has been logged. An assistant will start working on it "
                "and send status updates.</p>"
            )
        else:
            message = "<p>Competition not found.</p>"
        # Build confirmation page
        html = (
            "<!DOCTYPE html>"
            "<html lang='en'>"
            "<head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            "<title>Selection</title>"
            "<style>body{font-family:Arial,Helvetica,sans-serif;background:#f9f9f9;margin:0;padding:40px;}"
            "main{max-width:600px;margin:0 auto;background:#fff;border:1px solid #ddd;border-radius:8px;padding:20px;box-shadow:0 2px 4px rgba(0,0,0,0.1);}"
            ".button{display:inline-block;margin-top:20px;padding:8px 12px;background:#2980b9;color:#fff;text-decoration:none;border-radius:4px;}"
            ".button:hover{background:#1f6391;}"
            "</style></head><body>"
            f"<main>{message}<a href='/' class='button'>Back to list</a></main>"
            "</body></html>"
        )
        self._send_response(html)


def run_server(port: int = 8000) -> None:
    """Start the HTTP server on the given port."""
    server_address = ("", port)
    httpd = http.server.HTTPServer(server_address, CompetitionRequestHandler)
    print(f"Serving competition site on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    """
    When run as a script, this module starts the HTTP server.  On platforms like
    Render, the web service is assigned a port via the `PORT` environment
    variable.  If the variable is present, the server listens on that port.
    Otherwise it defaults to port 8000 for local development.
    """
    import os
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    run_server(port)
