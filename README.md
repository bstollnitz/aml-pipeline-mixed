# How to train and deploy in Azure ML

This project shows how to train and deploy a Fashion MNIST model with an Azure ML pipeline, using a variety of methods for creating resources. It uses MLflow for tracking and model representation.

## Azure setup

* You need to have an Azure subscription. You can get a [free subscription](https://azure.microsoft.com/en-us/free?WT.mc_id=aiml-44165-bstollnitz) to try it out.
* Create a [resource group](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resource-groups-portal?WT.mc_id=aiml-44165-bstollnitz).
* Create a new machine learning workspace by following the "Create the workspace" section of the [documentation](https://docs.microsoft.com/en-us/azure/machine-learning/quickstart-create-resources?WT.mc_id=aiml-44165-bstollnitz). Keep in mind that you'll be creating a "machine learning workspace" Azure resource, not a "workspace" Azure resource, which is entirely different!
* If you have access to GitHub Codespaces, click on the "Code" button in this GitHub repo, select the "Codespaces" tab, and then click on "New codespace."
* Alternatively, if you plan to use your local machine:
  * Install the Azure CLI by following the instructions in the [documentation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?WT.mc_id=aiml-44165-bstollnitz).
  * Install the ML extension to the Azure CLI by following the "Installation" section of the [documentation](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-configure-cli?WT.mc_id=aiml-44165-bstollnitz).
* In a terminal window, login to Azure by executing `az login --use-device-code`. 
* Set your default subscription by executing `az account set -s "<YOUR_SUBSCRIPTION_NAME_OR_ID>"`. You can verify your default subscription by executing `az account show`, or by looking at `~/.azure/azureProfile.json`.
* Set your default resource group and workspace by executing `az configure --defaults group="<YOUR_RESOURCE_GROUP>" workspace="<YOUR_WORKSPACE>"`. You can verify your defaults by executing `az configure --list-defaults` or by looking at `~/.azure/config`.
* You can now open the [Azure Machine Learning studio](https://ml.azure.com/?WT.mc_id=aiml-44165-bstollnitz), where you'll be able to see and manage all the machine learning resources we'll be creating.
* Although not essential to run the code in this post, I highly recommend installing the [Azure Machine Learning extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.vscode-ai).


## Project setup

If you have access to GitHub Codespaces, click on the "Code" button in this GitHub repo, select the "Codespaces" tab, and then click on "New codespace."

Alternatively, you can set up your local machine using the following steps.

Install conda environment:

```
conda env create -f environment.yml
```

Activate conda environment:

```
conda activate aml-resources
```


## Train and predict locally

```
cd aml-resources
```

* Run train.py by pressing F5.
* Run test.py the same way.
* You can analyze the metrics logged in the "mlruns" directory with the following command:

```
mlflow ui
```

* Make a local prediction using the trained mlflow model. You can use either csv or json files:

```
mlflow models predict --model-uri "model" --input-path "test-data/images.csv" --content-type csv
mlflow models predict --model-uri "model" --input-path "test-data/images.json" --content-type json
```


## Train and deploy in the cloud

### Create the compute cluster

Create the compute cluster using the [Azure ML Studio UI](https://ml.azure.com/). Go to "Compute", "Compute clusters", "New."

* Select a Location, such as "West US 2."
* Select a Virtual machine tier, such as "Dedicated."
* Select a Virtual machine type, such as "GPU."
* Select a Virtual machine size, such as "Standard_NC6s_v3."
* Click Next.
* Enter a Compute name, such as "cluster-gpu."
* Select a Minimum number of nodes, such as 0.
* Select a Maximum number of nodes, such as 4.
* Click Create.

Look at the "Compute clusters" page. Your newly created cluster should be listed there.


### Create the dataset

Create the dataset using the [Azure ML Studio UI](https://ml.azure.com/). Go to "Data", "Create", "From local files."

* Enter a Name, such as "data-fashion-mnist."
* Change the "Dataset type" to "File."
* Click Next.
* Click "Browse," "Browse folder," and select the "data" folder generated when you ran the "train.py" file locally.
* Click Upload.
* Click Next.
* Click Create.


### Create the components

Create the components using the CLI. Type the following in the terminal:

```
cd aml-resources
```

```
az ml component create -f components/train.yml
az ml component create -f components/test.yml
```


### Create and run the pipeline

(TODO: Use the Python SDK.)

```
run_id=$(az ml job create -f cloud/pipeline.yml --query name -o tsv)
```

Go to the Azure ML Studio and wait until the Job completes.


### Register the model

Create the Azure ML model from the output.

```
az ml model create --name model-pipeline --version 1 --path "azureml://jobs/$run_id/outputs/model" --type mlflow_model
```

### Create the endpoint

(TODO: Use Azure ML VS Code extension.)

```
az ml online-endpoint create -f cloud/endpoint.yml
az ml online-deployment create -f cloud/deployment.yml --all-traffic
```

Invoke the endpoint.

```
az ml online-endpoint invoke --name endpoint-pipeline --request-file test-data/images_azureml.json
```