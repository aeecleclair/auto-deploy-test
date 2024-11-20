from datetime import UTC, datetime
from app.adaptaters.storage_system import StorageSystem
from app.models.model1 import Model1, Model1Base


def create_model1(model_base: Model1Base, storage_system: StorageSystem):
    exist = storage_system.load_model1(model_base.name)
    if exist is not None:
        raise ValueError("This model already exists")
    else:
        storage_system.store_model1(
            Model1(**model_base.model_dump(), date=datetime.now(tz=UTC).date())
        )


def add_value_to_model(
    model_name: str, value_to_add: int, storage_system: StorageSystem
):
    model = storage_system.load_model1(model_name)
    if model is None:
        raise ValueError("The model name given does not correspond to any model stored")
    model.value += value_to_add
    storage_system.store_model1(model)


def get_all_model1(storage_system: StorageSystem) -> list[Model1]:
    return storage_system.get_all_model1()
