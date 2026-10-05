import secrets
from database import KeyModel, SessionLocal
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

app = FastAPI(title="Roblox Key Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


class KeyCreateRequest(BaseModel):
  custom_key: str | None = None
  owner: str


class HWIDResetRequest(BaseModel):
  key: str


class VerifyRequest(BaseModel):
  key: str
  hwid: str


@app.post("/admin/keys/create")
def create_key(req: KeyCreateRequest, db: Session = Depends(get_db)):
  new_key = (
      req.custom_key
      if req.custom_key
      else f"KEY-{secrets.token_hex(6).upper()}"
  )
  if db.query(KeyModel).filter(KeyModel.key == new_key).first():
    raise HTTPException(status_code=400, detail="La key ya existe.")

  key_obj = KeyModel(key=new_key, owner=req.owner)
  db.add(key_obj)
  db.commit()
  return {"status": "success", "key": new_key, "owner": req.owner}


@app.post("/admin/keys/reset")
def reset_hwid(req: HWIDResetRequest, db: Session = Depends(get_db)):
  key_obj = db.query(KeyModel).filter(KeyModel.key == req.key).first()
  if not key_obj:
    raise HTTPException(status_code=404, detail="Key no encontrada.")
  key_obj.hwid = None
  db.commit()
  return {"status": "success", "message": "HWID reseteado."}


@app.delete("/admin/keys/{key_str}")
def delete_key(key_str: str, db: Session = Depends(get_db)):
  key_obj = db.query(KeyModel).filter(KeyModel.key == key_str).first()
  if not key_obj:
    raise HTTPException(status_code=404, detail="Key no encontrada.")
  db.delete(key_obj)
  db.commit()
  return {"status": "success", "message": "Key eliminada."}


@app.get("/admin/keys")
def list_keys(db: Session = Depends(get_db)):
  return db.query(KeyModel).all()


@app.post("/api/verify")
def verify_key(req: VerifyRequest, db: Session = Depends(get_db)):
  key_obj = (
      db.query(KeyModel)
      .filter(KeyModel.key == req.key, KeyModel.is_active == True)
      .first()
  )
  if not key_obj:
    return {"valid": False, "reason": "Key invalida o desactivada."}

  if key_obj.hwid is None:
    key_obj.hwid = req.hwid
    db.commit()
    return {
        "valid": True,
        "owner": key_obj.owner,
        "message": "HWID registrado con exito.",
    }

  if key_obj.hwid != req.hwid:
    return {"valid": False, "reason": "HWID no coincide."}

  return {"valid": True, "owner": key_obj.owner}

@app.get("/ping")
def ping():
  return {"status": "ok"}