from dataclasses import dataclass
from marshmallow_dataclass import class_schema
import yaml


@dataclass()
class PredictPipelineParams:
    id_short_clf_model: str
    id_tipa_clf_model: str


PredictPipelineParamsSchema = class_schema(PredictPipelineParams)


def read_predict_pipeline_params(path: str) -> PredictPipelineParams:
    with open(path, "r") as file:
        schema = PredictPipelineParamsSchema()
        return schema.load(yaml.safe_load(file))
