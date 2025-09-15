from __future__ import annotations

import os
import pickle
from typing import List, Dict, Any

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

from recommender import load, recommend_by_title

app = Flask(__name__)
CORS(app)

MOVIES: pd.DataFrame
SIMILARITY: Any


def initialize_artifacts() -> None:
	global MOVIES, SIMILARITY
	MOVIES, SIMILARITY = load()


@app.get("/api/health")
def health() -> Any:
	return jsonify({"status": "ok"})


@app.get("/api/suggestions")
def suggestions() -> Any:
	query = request.args.get("q", "").strip()
	limit = int(request.args.get("limit", 20))
	if not query:
		rows = MOVIES["title"].head(limit).tolist()
	else:
		rows = MOVIES[MOVIES["title"].str.contains(query, case=False, na=False)]["title"].head(limit).tolist()
	return jsonify({"suggestions": rows})


@app.get("/api/recommend")
def recommend() -> Any:
	title = request.args.get("title", "").strip()
	top_k = int(request.args.get("top_k", 5))
	if not title:
		return jsonify({"error": "missing title"}), 400
	results = recommend_by_title(title=title, movies=MOVIES, similarity=SIMILARITY, top_k=top_k)
	return jsonify({"recommendations": results})


if __name__ == "__main__":
	initialize_artifacts()
	port = int(os.environ.get("PORT", 5000))
	app.run(host="0.0.0.0", port=port, debug=False)
