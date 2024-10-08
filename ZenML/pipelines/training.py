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

from typing import Optional
from uuid import UUID

from zenml import pipeline
from zenml.client import Client
from zenml.logger import get_logger

from pipelines import (
    feature_engineering,
)
from steps import model_evaluator, model_promoter, model_trainer

logger = get_logger(__name__)


@pipeline
def training(
    train_dataset_id: Optional[UUID] = None,
    test_dataset_id: Optional[UUID] = None,
    target: Optional[str] = "target",
    model_type: Optional[str] = "sgd",
):
    """
    Model training pipeline.

    This is a pipeline that loads the data from a preprocessing pipeline,
    trains a model on it and evaluates the model. If it is the first model
    to be trained, it will be promoted to production. If not, it will be
    promoted only if it has a higher accuracy than the current production
    model version.

    Args:
        train_dataset_id: ID of the train dataset produced by feature engineering.
        test_dataset_id: ID of the test dataset produced by feature engineering.
        target: Name of target column in dataset.
        model_type: The type of model to train.
    """
    # Link all the steps together by calling them and passing the output
    # of one step as the input of the next step.

    # Execute Feature Engineering Pipeline
    if train_dataset_id is None or test_dataset_id is None:
        dataset_trn, dataset_tst = feature_engineering()
    else:
        client = Client()
        dataset_trn = client.get_artifact_version(name_id_or_prefix=train_dataset_id)
        dataset_tst = client.get_artifact_version(name_id_or_prefix=test_dataset_id)

    model = model_trainer(dataset_trn=dataset_trn, target=target, model_type=model_type)

    acc = model_evaluator(
        model=model,
        dataset_trn=dataset_trn,
        dataset_tst=dataset_tst,
        target=target,
    )

    model_promoter(accuracy=acc)
