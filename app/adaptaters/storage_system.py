from datetime import date
import json
from pathlib import Path
from app.models.model1 import Model1


class StorageSystem:
    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.model1_path = Path(base_directory + "/model1")

    def update_db(self):
        Path.mkdir(self.model1_path, parents=True, exist_ok=True)

    def store_model1(self, model1: Model1):
        with Path.open(self.model1_path / model1.name, "w") as file:
            model_dict = model1.model_dump()
            model_dict["date"] = model1.date.isoformat()
            json.dump(model1, file)

    def load_model1(self, model1_name: str) -> Model1 | None:
        try:
            with Path.open(self.model1_path / model1_name, "r") as file:
                model_dict = json.load(file)
                model_dict["date"] = date.fromisoformat(model_dict["date"])
                return Model1(**model_dict)
        except FileNotFoundError:
            return None

    def get_all_model1(self) -> list[Model1]:
        response = []
        for file in Path(self.model1_path).glob("/*"):
            model = self.load_model1(file.name)
            if model is not None:
                response.append(model)
        return response
