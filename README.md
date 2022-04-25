# Wafer Fault Detection

## Problem Statement
    
    Wafer (In electronics), also called a slice or substrate, is a thin slice of semiconductor,
    such as a crystalline silicon (c-Si), used for fabricationof integrated circuits and in photovoltaics,
    to manufacture solar cells.
    
    The inputs of various sensors for different wafers have been provided.
    The goal is to build a machine learning model which predicts whether a wafer needs to be replaced or not
    (i.e whether it is working or not) nased on the inputs from various sensors.
    There are two classes: +1 and -1.
    +1: Means that the wafer is in a working condition and it doesn't need to be replaced.
    -1: Means that the wafer is faulty and it needa to be replaced.
    
#### Data Description
    
    The client will send data in multiple sets of files in batches at a given location.
    Data will contain Wafer names and 590 columns of different sensor values for each wafer.
    The last column will have the "Good/Bad" value for each wafer.
    
    Apart from training files, we laso require a "schema" file from the client, which contain all the
    relevant information about the training files such as:
    
    Name of the files, Length of Date value in FileName, Length of Time value in FileName, NUmber of Columnns, 
    Name of Columns, and their dataype.
    
#### Data Validation
    
    In This step, we perform different sets of validation on the given set of training files.
    
    Name Validation: We validate the name of the files based on the given name in the schema file. We have 
    created a regex patterg as per the name given in the schema fileto use for validation. After validating 
    the pattern in the name, we check for the length of the date in the file name as well as the length of time 
    in the file name. If all the values are as per requirements, we move such files to "Good_Data_Folder" else
    we move such files to "Bad_Data_Folder."
    
    Number of Columns: We validate the number of columns present in the files, and if it doesn't match with the
    value given in the schema file, then the file id moves to "Bad_Data_Folder."
    
    Name of Columns: The name of the columns is validated and should be the same as given in the schema file. 
    If not, then the file is moved to "Bad_Data_Folder".
    
    The datatype of columns: The datatype of columns is given in the schema file. This is validated when we insert
    the files into Database. If the datatype is wrong, then the file is moved to "Bad_Data_Folder."
    
    Null values in columns: If any of the columns in a file have all the values as NULL or missing, we discard such
    a file and move it to "Bad_Data_Folder".
    
#### Data Insertion in Database
     
     Database Creation and Connection: Create a database with the given name passed. If the database is already created,
     open the connection to the database.
     
     Table creation in the database: Table with name - "Good_Data", is created in the database for inserting the files 
     in the "Good_Data_Folder" based on given column names and datatype in the schema file. If the table is already
     present, then the new table is not created and new files are inserted in the already present table as we want 
     training to be done on new as well as old training files.
     
     Insertion of file in the table: All the files in the "Good_Data_Folder" are inserted in the above-created table. If
     any file has invalid data type in any of the columns, the file is not loaded in the table and is moved to 
     "Bad_Data_Folder".
     
#### Model Training
    
     Data Export from Db: The data in a stored database is exported as a CSV file to be used for model training.
     
     Data Preprocessing: 
        Check for null values in the columns. If present, impute the null values using the KNN imputer.
        
        Check if any column has zero standard deviation, remove such columns as they don't give any information during 
        model training.
        
     Clustering: KMeans algorithm is used to create clusters in the preprocessed data. The optimum number of clusters 
     is selected

# Local Development Setup

## Clone this Git.
```
git clone https://github.com/Samm-G/WaferFaultDetection_circleci_deploy.git
```

## Create Conda Environment.
(Git Bash in project folder)
```
conda create -p <path_of_new_conda-venv> python==3.6.9 -y
```
(Open CMD in the main git-repo folder)
```
conda activate <path_of_new_conda-venv>
```
```
pip install -r requirements.txt
```

### To create requirements.txt
```buildoutcfg
pip freeze > requirements.txt
```

## Initialize Your Own Git Repo
```
rm -rf .git

git init
git add .

git commit -m "first commit"
git branch -M main

git remote add origin <github_url>
git push -u origin main
```

## To update your Modifications
```
git add .
git commit -m "proper message"
git push 
```

## Remove Py-Cache:
```
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
```


# Build Local Docker Image:

## Docker Login:
```
docker login -u $DOCKERHUB_USER -p $DOCKER_HUB_PASSWORD_USER docker.io
```

## Create a file "Dockerfile" with below content

```
FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "main.py" ]
```

## Build Docker Image:
```
docker build -t <docker_image_name>:latest .
```

## See Docker Images:
```
docker images
```

## Run Image on local.:
```
docker run -p 5000:5000 <docker_image_name>
```

# CircleCI Deployment:

## Create a account at circle ci

<a href="https://circleci.com/login/">Circle CI Login</a>

## Create a "Procfile" with following content
```
web: gunicorn main:app
```

## Create a file ".circleci\config.yml" with following content
```
version: 2.1
orbs:
  heroku: circleci/heroku@1.0.1
jobs:
  build-and-test:
    executor: heroku/default
    docker:
      - image: circleci/python:3.6.2-stretch-browsers
        auth:
          username: mydockerhub-user
          password: $DOCKERHUB_PASSWORD  # context / project UI env-var reference
    steps:
      - checkout
      - restore_cache:
          key: deps1-{{ .Branch }}-{{ checksum "requirements.txt" }}
      - run:
          name: Install Python deps in a venv
          command: |
            echo 'export TAG=0.1.${CIRCLE_BUILD_NUM}' >> $BASH_ENV
            echo 'export IMAGE_NAME=python-circleci-docker' >> $BASH_ENV
            python3 -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
      - save_cache:
          key: deps1-{{ .Branch }}-{{ checksum "requirements.txt" }}
          paths:
            - "venv"
      - run:
          command: |
            . venv/bin/activate
            python -m pytest -v tests/test_script.py
      - store_artifacts:
          path: test-reports/
          destination: tr1
      - store_test_results:
          path: test-reports/
      - setup_remote_docker:
          version: 19.03.13
      - run:
          name: Build and push Docker image
          command: |
            docker build -t $DOCKERHUB_USER/$IMAGE_NAME:$TAG .
            docker login -u $DOCKERHUB_USER -p $DOCKER_HUB_PASSWORD_USER docker.io
            docker push $DOCKERHUB_USER/$IMAGE_NAME:$TAG
  deploy:
    executor: heroku/default
    steps:
      - checkout
      - run:
          name: Storing previous commit
          command: |
            git rev-parse HEAD > ./commit.txt
      - heroku/install
      - setup_remote_docker:
          version: 18.06.0-ce
      - run:
          name: Pushing to heroku registry
          command: |
            heroku container:login
            #heroku ps:scale web=1 -a $HEROKU_APP_NAME
            heroku container:push web -a $HEROKU_APP_NAME
            heroku container:release web -a $HEROKU_APP_NAME

workflows:
  build-test-deploy:
    jobs:
      - build-and-test
      - deploy:
          requires:
            - build-and-test
          filters:
            branches:
              only:
                - main
```

## Configure Circle CI:

Login to CircleCI > Projects > Setup Project (for your Github Repo)

Gather Data for Variables:
```
DOCKERHUB_USER
DOCKER_HUB_PASSWORD_USER
HEROKU_API_KEY 
HEROKU_APP_NAME
HEROKU_EMAIL_ADDRESS
DOCKER_IMAGE_NAME
```
CicleCI > Projects > (Select Your Project) > Project Settings > Environment Variables > ( Add all above Variables one by one..)


## Datadog Monitoring Setup (Optional)

Add Datadog Buildpack to heroku app..

```
heroku buildpacks:add https://github.com/DataDog/heroku-buildpack-datadog.git --app=wafer-circleci-deploy
```

```
heroku config:add DD_AGENT_MAJOR_VERSION=7 --app=wafer-circleci-deploy
heroku config:add DD_API_KEY=d7765239b45396a8fb93cafeb4f80c2e --app=wafer-circleci-deploy
heroku config:add DD_SITE=datadoghq.com --app=wafer-circleci-deploy
```

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
     
    
     
    
