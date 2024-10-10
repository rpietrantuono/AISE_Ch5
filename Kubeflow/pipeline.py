from kfp import dsl
from kfp import Client
from kfp import compiler
from kfp.dsl import Dataset
from kfp.dsl import Input
from kfp.dsl import Model
from kfp.dsl import Output
from typing import List


@dsl.component(packages_to_install=['pandas==1.3.5'])
def create_dataset(iris_dataset: Output[Dataset]):
    import pandas as pd
    csv_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    col_names = ["Sepal_Length", "Sepal_Width", "Petal_Length", "Petal_Width", "Labels"]
    df = pd.read_csv(csv_url)
    df.columns = col_names
    with open(iris_dataset.path, 'w') as f:
        df.to_csv(f)

@dsl.component(packages_to_install=['pandas==1.3.5', 'scikit-learn==1.0.2'])
def normalize_dataset(input_iris_dataset: Input[Dataset], normalized_iris_dataset: Output[Dataset], standard_scaler: bool, min_max_scaler: bool,):
    if standard_scaler is min_max_scaler:
        raise Value('Exactly one of standard_scaler or min_max_scaler mustbe True.')
    
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler, StandardScaler
    with open(input_iris_dataset.path) as f:
        df = pd.read_csv(f)
    
    labels = df.pop('Labels')
    
    if standard_scaler:
        scaler = StandardScaler()
    
    if min_max_scaler:
        scaler = MinMaxScaler()
    df = pd.DataFrame(scaler.fit_transform(df))
    df['Labels'] = labels
    
    with open(normalized_iris_dataset.path, 'w') as f:
        df.to_csv(f)


@dsl.component(packages_to_install=['pandas==1.3.5', 'scikit-learn==1.0.2'])
def train_model(normalized_iris_dataset: Input[Dataset],model: Output[Model],n_neighbors: int,):

    import pickle
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.neighbors import KNeighborsClassifier
    with open(normalized_iris_dataset.path) as f:
        df = pd.read_csv(f)
    
    y = df.pop('Labels')
    X = df
    X_train, X_test, y_train, y_test = train_test_split(X, y,random_state=0)
    
    clf = KNeighborsClassifier(n_neighbors=n_neighbors)
    clf.fit(X_train, y_train)
    
    with open(model.path, 'wb') as f:
        pickle.dump(clf, f)

@dsl.pipeline(name='iris-training-pipeline')
def my_pipeline(standard_scaler: bool, min_max_scaler: bool, neighbors: List[int],):
    create_dataset_task = create_dataset()
    iris_df = create_dataset_task.outputs['iris_dataset']
    normalize_dataset_task = normalize_dataset(input_iris_dataset=iris_df,standard_scaler=True, min_max_scaler=False)
    norm_iris_df = normalize_dataset_task.outputs['normalized_iris_dataset']
    with dsl.ParallelFor(neighbors) as n_neighbors:
        train_model(normalized_iris_dataset=norm_iris_df, n_neighbors=n_neighbors)


client = Client()
pipeline_args = {'min_max_scaler': True,
                 'standard_scaler': False,
                 'neighbors': [3, 6, 9]}

run = client.create_run_from_pipeline_func(my_pipeline, arguments=pipeline_args)

#compiler.Compiler().compile(my_pipeline, 'pipeline.yaml')

#client = Client()
#run = client.create_run_from_pipeline_package(
#    'pipeline.yaml',
#    arguments={
#        'min_max_scaler': True,
#        'standard_scaler': False,
#        'neighbors': [3, 6, 9]
#    },
#)
