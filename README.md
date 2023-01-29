
# Webhawk/Catch 2.0

Unsupervised Machine Learning web attacks detection.


<p align="center">  
  <img width="100%" src="https://github.com/slrbl/unsupervised-learning-attack-detection-webhawk-catch/blob/master/IMAGES/hawk.jpg">
  Image source:https://unsplash.com/photos/i4Y9hr5dxKc (Mathew Schwartz)
</p>

## About

Webhawk is an open source machine learning powered Web attack detection tool. It uses your web logs as training data. Webhawk offers a REST API that makes it easy to integrate within your SoC ecosystem. To train a detection model and use it as an extra security level in your organization, follow the following steps.

## Setup

### Using a Python virtual env

```shell
python -m venv webhawk_venv
source webhawk_venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Create a settings.conf file

Copy settings_template.conf file to settings.conf and fill it with the required parameters as the following.

```shell
[MODEL]
model:MODELS/the_model_you_will_train.pkl
[FEATURES]
features:length,params_number,return_code,size,upper_cases,lower_cases,special_chars,url_depth
```

## Unsupervised detection Usage

### Catch.py script

```shell
python catch.py -h 
usage: catch.py [-h] [-b] -l LOG_FILE -t LOG_TYPE [-e EPS] [-s MIN_SAMPLES] [-j LOG_LINES_LIMIT] [-p] [-o] [-r] [-z] [-y OPT_LAMDA]

options:
  -h, --help            show this help message and exit
  -b, --debug           Activate debug logging
  -l LOG_FILE, --log_file LOG_FILE
                        The raw http log file
  -t LOG_TYPE, --log_type LOG_TYPE
                        apache or nginx
  -e EPS, --eps EPS     DBSCAN Epsilon value (Max distance between two points)
  -s MIN_SAMPLES, --min_samples MIN_SAMPLES
                        Minimum number of points with the same cluster. The default value is 2
  -j LOG_LINES_LIMIT, --log_lines_limit LOG_LINES_LIMIT
                        The maximum number of log lines of consider
  -p, --show_plots      Show informative plots
  -o, --standarize_data
                        Smooth feature values
  -r, --report          Create a HTML report
  -z, --opt_silouhette  Optimize DBSCAN silouhette
  -y OPT_LAMDA, --opt_lamda OPT_LAMDA
                        Optimization lambda step

```


### Exmaple 

Encoding is automatic for the unsupervised mode. You just need to run the catch.py script.
Get inspired from this example:

```shell
python catch.py -l ../HTTP_LOGS_DTATSETS/SECREPO_LOGS/access.log.2021-10-22 --log_type apache --show_plots --standarize_data --report
```

The output of this command is:

<p align="center">  
  <img width="100%" src="https://github.com/slrbl/unsupervised-learning-attack-detection-webhawk-catch/blob/master/IMAGES/screenshot_1.png">
</p>

<p align="center">  
  <img width="100%" src="https://github.com/slrbl/unsupervised-learning-attack-detection-webhawk-catch/blob/master/IMAGES/clusters_1.png">
</p>

<p align="center">  
  <img width="100%" src="https://github.com/slrbl/unsupervised-learning-attack-detection-webhawk-catch/blob/master/IMAGES/clusters_2.png">
</p>


## Used sample data

The data you will find in SAMPLE_DATA folder comes from<br>
https://www.secrepo.com.

## Interesting data samples

https://www.kaggle.com/datasets/eliasdabbas/web-server-access-logs
https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/3QBYB5

## Documentation

TODO

## TODO
Nothing for now.

## Reference

Silhouette Effeciency
<br>https://bioinformatics-training.github.io/intro-machine-learning-2017/clustering.html

<br>Optimal Value of Epsilon
<br>https://towardsdatascience.com/machine-learning-clustering-dbscan-determine-the-optimal-value-for-epsilon-eps-python-example-3100091cfbc

<br>Max curvature point
<br>https://towardsdatascience.com/detecting-knee-elbow-points-in-a-graph-d13fc517a63c

## Contribution

All feedbacks, testing and contribution are very welcome!
If you would like to contribute, fork the project, add your contribution and make a pull request.
