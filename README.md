# How to create Azure ML resources using different methods

This project shows how to train a Fashion MNIST model using an Azure ML pipeline, and how to deploy it using an online managed endpoint. It demonstrates how to create Azure ML resources using the following three methods: the Azure ML Studio UI, Python SDK, and CLI. It uses MLflow for tracking and model representation.


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
conda activate aml_pipeline_mixed
```


## Train and predict locally

```
cd aml_pipeline_mixed
```

* Run train.py by pressing F5.
* Run test.py the same way.
* You can analyze the metrics logged in the "mlruns" directory with the following command:

```
mlflow ui
```

* Make a local prediction using the trained mlflow model. You can use either csv or json files:

```
mlflow models predict --model-uri "model" --input-path "test_data/images.csv" --content-type csv
mlflow models predict --model-uri "model" --input-path "test_data/images.json" --content-type json
```


## Train and deploy in the cloud

### Create the compute cluster

Create the compute cluster using the [Azure ML Studio UI](https://ml.azure.com/). Go to "Compute", "Compute clusters", "New."

* Select a Location, such as "West US 2."
* Select a Virtual machine tier, such as "Dedicated."
* Select a Virtual machine type, such as "CPU."
* Select a Virtual machine size, such as "Standard_DS4_v2."
* Click Next.
* Enter a Compute name, such as "cluster-cpu."
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


### Create and run the pipeline

Make sure you have a "config.json" file somewhere in the parent folder hierarchy of your project containing your Azure subscription ID, resource group, and workspace:

```
{
    "subscription_id": ...,
    "resource_group": ...,
    "workspace_name": ...
}
```

Run components/pipeline-job.py. 
Go to the Azure ML Studio and wait until the Job completes. You don't need to download the trained model, but here's how you would do it if you wanted to:

```
az ml job download --name $run_id --output-name "model_dir"
```

### Register the model

When the pipeline is done running, it prints the run id at the end. For example:

```
Execution Summary
=================
RunId: blue_soca_jkf490bx8y
```

Set the shell variable run_id to that run id. For example:

```
run_id=blue_soca_jkf490bx8y
```

Create the Azure ML model using the CLI.

```
az ml model create --name model-pipeline-mixed --version 1 --path "azureml://jobs/$run_id/outputs/model_dir" --type mlflow_model
```

### Create and invoke the endpoint

Create the deployment and endpoint using the CLI, with the help of the Azure ML VS Code extension.

Open cloud/endpoint.yml, right-click, and select "Azure ML: Execute YAML." Once the endpoint is created, do the same for cloud/deployment.yml.

Set the traffic of the deployment to 100%.

```
az ml online-endpoint update -n endpoint-pipeline-mixed --traffic "blue=100"
```

Invoke the endpoint.

```
az ml online-endpoint invoke --name endpoint-pipeline-mixed --request-file test_data/images_azureml.json
```