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

from typing import List, Optional, Tuple

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from typing_extensions import Annotated
from zenml import log_artifact_metadata, step

from utils.preprocess import ColumnsDropper, DataFrameCaster, NADropper


@step
def data_preprocessor(
    random_state: int,
    dataset_trn: pd.DataFrame,
    dataset_tst: pd.DataFrame,
    drop_na: Optional[bool] = None,
    normalize: Optional[bool] = None,
    drop_columns: Optional[List[str]] = None,
    target: Optional[str] = "target",
) -> Tuple[
    Annotated[pd.DataFrame, "dataset_trn"],
    Annotated[pd.DataFrame, "dataset_tst"],
    Annotated[Pipeline, "preprocess_pipeline"],
]:
    """Data preprocessor step.

    This is an example of a data processor step that prepares the data so that
    it is suitable for model training. It takes in a dataset as an input step
    artifact and performs any necessary preprocessing steps like cleaning,
    feature engineering, feature selection, etc. It then returns the processed
    dataset as a step output artifact.

    This step is parameterized, which allows you to configure the step
    independently of the step code, before running it in a pipeline.
    In this example, the step can be configured to drop NA values, drop some
    columns and normalize numerical columns. See the documentation for more
    information:

        https://docs.zenml.io/how-to/build-pipelines/use-pipeline-step-parameters

    Args:
        random_state: Random state for sampling.
        dataset_trn: The train dataset.
        dataset_tst: The test dataset.
        drop_na: If `True` all NA rows will be dropped.
        normalize: If `True` all numeric fields will be normalized.
        drop_columns: List of column names to drop.
        target: Name of target column in dataset.

    Returns:
        The processed datasets (dataset_trn, dataset_tst) and fitted `Pipeline` object.
    """
    # We use the sklearn pipeline to chain together multiple preprocessing steps
    preprocess_pipeline = Pipeline([("passthrough", "passthrough")])
    if drop_na:
        preprocess_pipeline.steps.append(("drop_na", NADropper()))
    if drop_columns:
        # Drop columns
        preprocess_pipeline.steps.append(("drop_columns", ColumnsDropper(drop_columns)))
    if normalize:
        # Normalize the data
        preprocess_pipeline.steps.append(("normalize", MinMaxScaler()))
    preprocess_pipeline.steps.append(("cast", DataFrameCaster(dataset_trn.columns)))
    dataset_trn = preprocess_pipeline.fit_transform(dataset_trn)
    dataset_tst = preprocess_pipeline.transform(dataset_tst)

    # Log metadata so we can load it in the inference pipeline
    log_artifact_metadata(
        artifact_name="preprocess_pipeline",
        metadata={"random_state": random_state, "target": target},
    )
    return dataset_trn, dataset_tst, preprocess_pipeline
