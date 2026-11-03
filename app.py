"""Flask app. Files are read in memory and never saved on the server."""
import base64
import io
import os
from flask import Flask, jsonify, render_template, request
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analyzer import analyze

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def read_resume(file):
    name = (file.filename or "").lower()
    data = file.read()
    if not data:
        raise ValueError("The uploaded resume is empty.")
    if name.endswith(".txt"):
        return data.decode("utf-8-sig", errors="replace")
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        if len(reader.pages) > 30:
            raise ValueError("Please upload a resume with 30 pages or fewer.")
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                paragraphs.extend(cell.text for cell in row.cells)
        return "\n".join(paragraphs)
    raise ValueError("Supported resume formats: PDF, DOCX and TXT.")


def make_chart(result):
    categories = result["categories"]
    fig, ax = plt.subplots(figsize=(8, max(2.7, .65 * max(1, len(categories)) + 1.3)))
    fig.patch.set_facecolor("#111b30")
    ax.set_facecolor("#111b30")
    if categories:
        names = [c["category"] for c in categories][::-1]
        matched = [c["matched"] for c in categories][::-1]
        missing = [c["missing"] for c in categories][::-1]
        y = list(range(len(names)))
        ax.barh(y, matched, color="#47d5bd", height=.53, label="Matched")
        ax.barh(y, missing, left=matched, color="#ffaf70", height=.53, label="Missing")
        ax.set_yticks(y, names)
        ax.legend(loc="upper right", facecolor="#111b30", labelcolor="#e5edf8", frameon=False, ncol=2)
        ax.set_xlabel("Skills identified in job description", color="#acb7ca", fontsize=9)
    else:
        ax.text(.5,.5,"No supported skills detected in the job description",ha="center",va="center",color="#e5edf8",transform=ax.transAxes)
        ax.set_yticks([])
    ax.tick_params(colors="#c0cada", length=0)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.grid(axis="x", color="#ffffff", alpha=.08)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=2)
    out = io.BytesIO()
    fig.savefig(out, format="png", facecolor=fig.get_facecolor(), dpi=135)
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(out.getvalue()).decode("ascii")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/analyze")
def api_analyze():
    try:
        f = request.files.get("resume")
        job = request.form.get("job_description", "").strip()
        role = request.form.get("role", "Target Role")
        if not f or not f.filename:
            return jsonify({"error": "Please upload a resume."}), 400
        if len(job) < 30:
            return jsonify({"error": "Please enter a job description of at least 30 characters."}), 400
        text = read_resume(f)
        if len(text.strip()) < 20:
            return jsonify({"error": "Could not extract enough text. For scanned PDFs, use a text-based PDF, DOCX or TXT resume."}), 400
        result = analyze(text, job, role)
        result["chart"] = make_chart(result)
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        app.logger.exception("Analysis failed")
        return jsonify({"error": "Could not read that resume. Check that the file is valid and try again."}), 400


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "File too large. The maximum upload size is 5 MB."}), 413


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="127.0.0.1", port=5000)
