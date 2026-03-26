from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    descripcion: str = Field(min_length=2, max_length=80)


class CategoriaUpdate(BaseModel):
    descripcion: str | None = Field(default=None, min_length=2, max_length=80)


class CategoriaOut(BaseModel):
    id_categoria: int
    descripcion: str
    model_config = {"from_attributes": True}
