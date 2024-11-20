import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

from app.adaptaters.dependencies import get_storage_system
import app.logic.services as services
from app.adaptaters.storage_system import StorageSystem
from app.models.model1 import Model1, Model1Base

router = APIRouter(tags=["Core"])
logger = logging.getLogger("base")


@router.get("/", response_class=HTMLResponse)
async def read_index():
    with Path.open(Path("./assets/website/index.html")) as f:
        html = f.read()
    return HTMLResponse(content=html, status_code=200)


@router.get("/assets/{directory}/{file}", response_class=HTMLResponse)
async def read_assest(directory: str, file: str):
    return FileResponse(f"./assets/{directory}/{file}")


@router.get(
    "/model1/stored",
    status_code=200,
    response_model=list[Model1],
)
async def get_already_produced_competitors_results(
    storage_system=Depends(get_storage_system),
):
    return await services.get_all_model1(storage_system)


@router.post("/model1", status_code=201)
async def create_model1(
    model_base: Model1Base, storage_system=Depends(get_storage_system)
):
    try:
        services.create_model1(model_base, storage_system)
        return {"message": "Model created"}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=e,
        )


@router.patch("/model1/{model_name}", status_code=201)
async def request_competitor_search(
    model_name: str,
    value: int,
    storage_system: StorageSystem = Depends(get_storage_system),
):
    try:
        services.add_value_to_model(model_name, value, storage_system)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=e,
        )
