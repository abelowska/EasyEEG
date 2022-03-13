## Installation

Firstly, make sure you are using python 3.6, as well as correct versions of hidden dependencies of this package:

- TODO (fix here or in `setup.py`)

You can install this fork via:


```
pip install -e git+https://github.com/abelowska/EasyEEG.git@master
```

or adding


```
git+https://github.com/abelowska/EasyEEG.git@master
```

directly to your `requirements.txt`.

## EasyEEG: The toolbox for agile EEG data analyis.

Electroencephalography (EEG) provides high temporal resolution cognitive information from non-invasive recordings. However, one of the common practices–using a subset of sensors in ERP analysis is hard to provide a holistic and precise dynamic results. Selecting or grouping subsets of sensors may also be subject to selection bias, multiple comparison, and further complicated by individual differences in the group-level analysis. More importantly, changes in neural generators and variations in response magnitude from the same neural sources are difficult to separate, which limit the capacity of testing different aspects of cognitive hypotheses. We introduce EasyEEG, a toolbox that includes several multivariate analysis methods to directly test cognitive hypotheses based on topographic responses that include data from all sensors. These multivariate methods can investigate effects in the dimensions of response magnitude and topographic patterns separately using data in the sensor space, therefore enable assessing neural response dynamics. The concise workflow and the modular design provide user-friendly and programmer-friendly features. Users of all levels can benefit from the open-sourced, free EasyEEG to obtain a straightforward solution for efficient processing of EEG data and a complete pipeline from raw data to final results for publication.

> Yang, J., Zhu, H., & Tian, X. (2018). Group-Level Multivariate Analysis in EasyEEG Toolbox: Examining the Temporal Dynamics using Topographic Responses. Frontiers in Neuroscience, 12.