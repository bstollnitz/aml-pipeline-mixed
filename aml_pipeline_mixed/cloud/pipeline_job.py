"""Creates and runs an Azure ML pipeline."""

import logging
from pathlib import Path

from azure.ai.ml import MLClient, Input, load_component
from azure.identity import DefaultAzureCredential
from azure.ai.ml.dsl import pipeline

COMPUTE_NAME = "cluster-cpu"
DATA_NAME = "data-fashion-mnist"
DATA_VERSION = "1"
EXPERIMENT_NAME = "aml_pipeline_mixed"
TRAIN_PATH = Path(Path(__file__).parent, "train.yml")
TEST_PATH = Path(Path(__file__).parent, "test.yml")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    credential = DefaultAzureCredential()
    ml_client = MLClient.from_config(credential=credential)

    # Making sure the compute exists on Azure ML. If it doesn't, we get an error
    # here.
    ml_client.compute.get(name=COMPUTE_NAME)

    # Getting the data set, which should already be created on Azure ML.
    data = ml_client.data.get(name=DATA_NAME, version=DATA_VERSION)

    # We'll use the components directly, without registering them first.
    train_component = load_component(source=TRAIN_PATH)
    test_component = load_component(source=TEST_PATH)

    # Create and submit pipeline.
    @pipeline(default_compute=COMPUTE_NAME, experiment_name=EXPERIMENT_NAME)
    def pipeline_func(data_dir: Input) -> dict[str, str]:
        train_job = train_component(data_dir=data_dir)
        # Ignoring pylint because "test_job" shows up in the Studio UI.
        test_job = test_component(  # pylint: disable=unused-variable
            data_dir=data_dir,
            model_dir=train_job.outputs.model_dir)

        return {
            "model_dir": train_job.outputs.model_dir,
        }

    pipeline_job = pipeline_func(
        data_dir=Input(type="uri_folder", path=data.id))

    pipeline_job = ml_client.jobs.create_or_update(pipeline_job)
    ml_client.jobs.stream(pipeline_job.name)


if __name__ == "__main__":
    main()
