# app.py
import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__, template_folder="templates")
CORS(app)

DATABASE_URL = os.environ.get("DATABASE_URL") or "sqlite:///posts.db"
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/posts", methods=["GET"])
def get_posts():
    posts = Post.query.order_by(Post.created_at.desc()).limit(200).all()
    return jsonify([{"id":p.id,"content":p.content,"created_at":p.created_at.isoformat()} for p in posts])

@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json() or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error":"content required"}), 400
    if len(content) > 2000:
        return jsonify({"error":"too long"}), 400
    p = Post(content=content)
    db.session.add(p)
    db.session.commit()
    return jsonify({"id":p.id,"content":p.content,"created_at":p.created_at.isoformat()}), 201

# 起動時にテーブルがなければ作る（小さなプロジェクト向けの簡便処理）
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # ローカル開発用（本番は gunicorn で動かします）
    app.run(host="0.0.0.0", port=port, debug=True)
