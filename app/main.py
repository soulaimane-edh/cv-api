import os, json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

MODEL_ID     = os.getenv("MODEL_ID", "gpt-4o-mini")
ALLOW_ORIGIN = os.getenv("ALLOW_ORIGIN", "*")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOW_ORIGIN],
    allow_methods=["POST","GET","OPTIONS"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def health():
    return {"status":"ok"}

@app.post("/score")
async def score_endpoint(
    cv_file: UploadFile = File(...),
    fiche_file: UploadFile | None = File(None),
    fiche_json: str | None = Form(None),
    spec_json: str | None = Form(None),
):
    """
    Minimal stub. It just echoes what you send.
    Replace the 'TODO' section with your true pipeline logic later.
    """
    try:
        # Lazy import your pipeline (so startup never breaks)
        from app import pipeline as P

        # 1) Read CV to temp path (keep filename if helpful)
        cv_path = f"/tmp/{cv_file.filename}"
        with open(cv_path, "wb") as f:
            f.write(await cv_file.read())

        # 2) SPEC (either JSON string or uploaded file)
        spec = None
        if spec_json:
            spec = json.loads(spec_json)
        elif fiche_json:
            spec = json.loads(fiche_json)
        elif fiche_file:
            fpath = f"/tmp/{fiche_file.filename}"
            with open(fpath, "wb") as f:
                f.write(await fiche_file.read())
            # Heuristic: if file begins with '{', treat as JSON, else text
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fr:
                t = fr.read()
            if t.strip().startswith("{"):
                spec = json.loads(t)
            else:
                # Optional: turn text fiche -> spec via GPT (later, if needed)
                spec = {
                    "must_have": [],
                    "nice_to_have": [],
                    "experience_min_ans": 0,
                    "langues": {},
                    "diplomes": [],
                    "certifications": [],
                    "localisation": "",
                    "disponibilite_max_semaines": 4,
                    "poids": {"must_have":50,"nice_to_have":30,"experience":10,"langues":5,"diplomes_certifs":3,"localisation_dispo":2}
                }
        else:
            # Default empty spec
            spec = {
                "must_have": [],
                "nice_to_have": [],
                "experience_min_ans": 0,
                "langues": {},
                "diplomes": [],
                "certifications": [],
                "localisation": "",
                "disponibilite_max_semaines": 4,
                "poids": {"must_have":50,"nice_to_have":30,"experience":10,"langues":5,"diplomes_certifs":3,"localisation_dispo":2}
            }

        # 3) Read CV text
        cv_text = P.read_cv_text(cv_path)

        # ==========================
        # TODO: your true pipeline:
        #   ex = P.gpt_extract_profile_safe(cv_text, model_id=MODEL_ID)
        #   ex = P.enforce_evidence(ex, cv_text)
        #   ex = P.fill_with_regex_if_missing(ex, cv_text)
        #   pts_mn, evidences = P.score_competences_embeddings(cv_text, spec)
        #   pts_autres, _com, _details = P.score_autres_criteres(ex, spec)
        #   score_final = round(pts_mn + pts_autres, 2)
        #   commentaire = P.build_commentaire_deterministe(score_final, evidences, ex, spec)
        #
        # For now return a minimal, deploy-safe response:
        # ==========================
        return {
            "ok": True,
            "note": "Server deployed. Replace /score stub with your real pipeline when ready.",
            "cv_filename": cv_file.filename,
            "cv_len": len(cv_text or ""),
            "spec_keys": list(spec.keys()) if isinstance(spec, dict) else None
        }

    except Exception as e:
        return JSONResponse({"error": str(e)}, 500)
