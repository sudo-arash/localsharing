import os
import uuid
from flask.templating import render_template
import yaml
from flask import Flask, request, jsonify, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

config = load_config()
app.config["UPLOAD_FOLDER"] = config["upload_folder"]
app.config["ALLOWED_EXTENSIONS"] = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "zip", "rar", "7z", "tar", "gz", "mp4", "mp3", "wav", "flac", "ogg", "avi", "mov", "mkv", "doc", "docx", "xls", "xlsx", "ppt", "pptx"}

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

@app.route("/upload", methods=["POST"])
def upload_file():
    if config["uploads_locked"]:
        token = request.headers.get("Authorization")
        if token != f"Bearer {config['token']}":
            return jsonify({"error": "Unauthorized, invalid token"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_id)
        file.save(file_path)

        download_link = f"/download/{file_id}"

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "download_link": download_link
        }), 200

    return jsonify({"error": "File type not allowed"}), 400

@app.route("/download/<file_id>")
def download_file(file_id):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file_id)
    if os.path.exists(file_path):
        return send_from_directory(app.config["UPLOAD_FOLDER"], file_id, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=False)
