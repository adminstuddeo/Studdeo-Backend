from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

from app.external_services import odoo

teacher_router: APIRouter = APIRouter(prefix="/profesores", tags=["Profesor Odoo"])


@teacher_router.get("/", response_model=List[Dict[str, Any]])
def listar_profesores(q: Optional[str] = None):
    try:
        profs: List[Dict[str, Any]] = odoo.list_professors()
        if q:
            qlow: str = q.lower()
            profs = [
                p
                for p in profs
                if (p.get("name") and qlow in (p["name"] or "").lower())
                or (p.get("email") and qlow in (p["email"] or "").lower())
                or (p.get("login") and qlow in (p["login"] or "").lower())
            ]
        return profs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando profesores: {e}")
