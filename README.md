This repository includes a very simple Python Flask web site, made for demonstration purposes only.

## Local development

This project has devcontainer support, so you can open it in Github Codespaces or local VS Code with the Dev Containers extension.

Steps for running the server:

1. (Optional) If you're unable to open the devcontainer, [create a Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate that.

2. Install the requirements:

    ```shell
    python3 -m pip install -r requirements-dev.txt
    ```

3. Run the local server: (or use VS Code "Run" button and select "Run server")

    ```shell
    python3 -m flask --debug run
    ```

3. Click 'http://127.0.0.1:5000' in the terminal, which should open the website in a new tab
4. Confirm the photos load on the index page and click a photo to see the order page.


### Local development with Docker

You can also run this app locally with Docker, thanks to the `Dockerfile`.
You need to either have Docker Desktop installed or have this open in Github Codespaces for these commands to work.

1. Build the image:

    ```shell
    docker build --tag flask-app .
    ```

2. Run the image:

    ```shell
    docker run --publish 5000:5000 flask-app
    ```

## Deployment

This repo is set up for deployment on [Azure Container Apps](https://learn.microsoft.com/azure/container-apps/overview) using the configuration files in the `infra` folder.

![Diagram of architecture using Azure Container Apps, Azure Container Registry and an Azure CDN in front](readme_diagram.png)

Steps for deployment:

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd). (If you opened this repository in a devcontainer, that part will be done for you.)
3. Provision and deploy all the resources:

    ```shell
    azd up
    ```

    It will prompt you to login and to provide a name (like "flask-app") and location (like "eastus"). Then it will provision the resources in your account and deploy the latest code. If you get an error with deployment, changing the location (like to "centralus") can help, as there are availability constraints for some of the resources.

4. When `azd` has finished deploying, you'll see an endpoint URI in the command output. Visit that URI, and you should see the front page of the app! 🎉

5. When you've made any changes to the app code, you can just run:

    ```shell
    azd deploy
    ```

## CI/CD pipeline

This project includes a Github workflow for deploying the resources to Azure
on every push to main. That workflow requires several Azure-related authentication secrets
to be stored as Github action secrets. To set that up, run:

```shell
azd pipeline config
```

### Costs

These are only provided as an example, as of Feb-2023. The PostgreSQL server has an hourly cost, so if you are not actively using the app, remember to run `azd down` or delete the resource group to avoid unnecessary costs.

- Azure CDN - Standard tier, $0.081 per GB for first 10 TB per month. [Pricing](https://azure.microsoft.com/pricing/details/cdn/)
- Azure Container App - Consumption tier with 0.5 CPU, 1GiB memory/storage Pricing is based on resource allocation, and each month allows for a certain amount of free usage, ~$2/month. [Pricing](https://azure.microsoft.com/pricing/details/container-apps/)
- Azure Container Registry - Basic tier. $0.167/day, ~$5/month. [Pricing](https://azure.microsoft.com/pricing/details/container-registry/)
- Key Vault - Standard tier. $0.04/10,000 transactions. Only a few transactions are used on each deploy. [Pricing](https://azure.microsoft.com/pricing/details/key-vault/)


## Getting help

If you're working with this project and running into issues, please post in **Discussions**.
