# MIT License
# 
# Copyright (c) ZenML GmbH 2024
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

from zenml import get_step_context, step
from zenml.client import Client
from zenml.logger import get_logger

logger = get_logger(__name__)


@step
def model_promoter(accuracy: float, stage: str = "production") -> bool:
    """Model promoter step.

    This is an example of a step that conditionally promotes a model. It takes
    in the accuracy of the model and the stage to promote the model to. If the
    accuracy is below 80%, the model is not promoted. If it is above 80%, the
    model is promoted to the stage indicated in the parameters. If there is
    already a model in the indicated stage, the model with the higher accuracy
    is promoted.

    Args:
        accuracy: Accuracy of the model.
        stage: Which stage to promote the model to.

    Returns:
        Whether the model was promoted or not.
    """
    is_promoted = False

    if accuracy < 0.8:
        logger.info(
            f"Model accuracy {accuracy*100:.2f}% is below 80% ! Not promoting model."
        )
    else:
        logger.info(f"Model promoted to {stage}!")
        is_promoted = True

        # Get the model in the current context
        current_model = get_step_context().model

        # Get the model that is in the production stage
        client = Client()
        try:
            stage_model = client.get_model_version(
                current_model.name, stage
            )
            # We compare their metrics
            prod_accuracy = (
                stage_model.get_artifact("sklearn_classifier")
                .run_metadata["test_accuracy"]
                .value
            )
            if float(accuracy) > float(prod_accuracy):
                # If current model has better metrics, we promote it
                is_promoted = True
                current_model.set_stage(stage, force=True)
        except KeyError:
            # If no such model exists, current one is promoted
            is_promoted = True
            current_model.set_stage(stage, force=True)
    return is_promoted
