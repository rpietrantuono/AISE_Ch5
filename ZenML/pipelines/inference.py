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

from zenml import get_pipeline_context, pipeline
from zenml.logger import get_logger

from steps import (
    data_loader,
    inference_predict,
    inference_preprocessor,
)

logger = get_logger(__name__)


@pipeline
def inference(random_state: int, target: str):
    """
    Model inference pipeline.

    This is a pipeline that loads the inference data, processes it with
    the same preprocessing pipeline used in training, and runs inference
    with the trained model.

    Args:
        random_state: Random state for reproducibility.
        target: Name of target column in dataset.
    """
    # Get the production model artifact
    model = get_pipeline_context().model.get_artifact("sklearn_classifier")

    # Get the preprocess pipeline artifact associated with this version
    preprocess_pipeline = get_pipeline_context().model.get_artifact(
        "preprocess_pipeline"
    )

    # Link all the steps together by calling them and passing the output
    #  of one step as the input of the next step.
    df_inference = data_loader(random_state=random_state, is_inference=True)
    df_inference = inference_preprocessor(
        dataset_inf=df_inference,
        preprocess_pipeline=preprocess_pipeline,
        target=target,
    )
    inference_predict(
        model=model,
        dataset_inf=df_inference,
    )
