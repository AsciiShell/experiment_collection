# Experiment collection

![GitHub](https://img.shields.io/github/license/AsciiShell/experiment_collection)
[![PyPI version](https://badge.fury.io/py/experiment-collection.svg)](https://badge.fury.io/py/experiment-collection)
![Release](https://github.com/AsciiShell/experiment_collection/workflows/Release/badge.svg)

A set of utilities for storing and organizing experiments

# Install 

```shell script
pip install experiment-collection
```

You can find another versions at [releases](https://github.com/AsciiShell/experiment_collection/releases)
or [pypi](https://pypi.org/project/experiment-collection/).

# Usage_example

`Experiment` - structure with experiment data;

`ExperimentCollectionLocal` - local experiment storage;

`ExperimentCollectionRemote` - remote experiment storage;
could combine data from multiply sources.

```python3
from experiment_collection import Experiment, ExperimentCollectionRemote

exps = ExperimentCollectionRemote('localhost:50051', 'main', 'token')

for i in range(10):
    exp = Experiment('name_{}'.format(i))
    exp.set_metrics({'lr': 0.1})
    exp.set_params({'auc': 0.5})

    exps.add_experiment(exp)

    assert exps.check_experiment(exp)

# Delete latest experiment
exps.delete_experiment(exp)

assert not exps.check_experiment(exp)
```

View all results.
All metrics and params auto flatten into single columns.

<div class="cell code">

    exps.get_experiments()

<div class="output execute_result">

         name                       time  params_auc  metrics_lr
    0  name_0 2020-09-30 23:56:39.932871         0.5         0.1
    1  name_1 2020-09-30 23:56:40.216424         0.5         0.1
    2  name_2 2020-09-30 23:56:40.620029         0.5         0.1
    3  name_3 2020-09-30 23:56:40.916781         0.5         0.1
    4  name_4 2020-09-30 23:56:41.240535         0.5         0.1
    5  name_5 2020-09-30 23:56:41.567865         0.5         0.1
    6  name_6 2020-09-30 23:56:41.861890         0.5         0.1
    7  name_7 2020-09-30 23:56:42.177155         0.5         0.1
    8  name_8 2020-09-30 23:56:42.507883         0.5         0.1
    9  name_9 2020-09-30 23:56:42.818714         0.5         0.1

</div>

</div>

# License

MIT License

Copyright (c) 2020 AsciiShell (Aleksey Podchezertsev)