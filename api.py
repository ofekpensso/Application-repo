from flask import Flask, jsonify

app = Flask(__name__)

# --- החלק החדש שהוספנו ---
@app.route('/')
def home():
    return "I finish the deploy stage", 200
# -------------------------

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
