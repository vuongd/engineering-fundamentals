# Build, Publish and Code Quality analysis in CI
This readme helps you to create an CI environment which builds your project, publishes it to Azure Container Registry and executes Code Quality Analsis.

### Prerequisites
- Be part of ipt Sandbox subscription on Azure
- Be part of ipt organisation in Github

### Branches
- **main**: Starting point to solve exercices
- **solution**: Example solution (Musterlösung)

# Setup
1. Create a **public** fork of this Github repo **in your private github namespace** (this is required as we are using the FREE version of SonarCloud later on) \
  a) Note: If the 'fork' button in the repo does not work (e.g. because the iptch repo is currently not public or forking is disabled on organization-level), you can do it manually:
```
# 1. Create an public repository in your personal github namespace
# 2. Execute in your local terminal:
git clone git@github.com:iptch/engineering-fundamentals.git
cd engineering-fundamentals
git remote remove origin
git remote add origin https://github.com/<YourUsername>/<YourRepoName>.git
git push --set-upstream origin main
```
2. Create Codespace (https://github.com/YourUsername/YourRepoName &rarr; Code &rarr; Codespaces) and install the azure cli \
<img src="images/codespace.png" alt="Codespaces" width="300px">
```
# Inside Codespace
pip install azure-cli
```
3. Verification
Check your setup by running the react app in your codespace. You should be able to access the Webapp in your browser.
```bash
nvm install node
npm install
npm run dev
```

## PART A - Unit Test
### Create a unit test
In the src directory there is the main App.tsx file. There we use the ``src/Counter.tsx`` component to implement a button 
which increments its counter everytime it is clicked. Write a Unit Test for the ``src/Counter.tsx`` component in the 
``src/__tests__/Counter.test.tsx`` file.

Now Execute your implemented unit test by running
```bash
npm test
```

### Automated test execution
Adapt GitHub Actions workflow in the ``.gibhub/workflows`` directory such, that the unit tests are executed for every merge request and every push to the main branch.
Check in the GitHub UI that, after each new commit on main, the GitHub Action is successfully executed.

## PART B - Continuous Integration

### Create Azure Container Registry
1. Log in to azure using your browser, ensure to be part of [ipt Sandbox subscription](https://app.happeo.com/pages/1e1oopl952ukqf9e0h/AzureAmpDu/1e5g766dso0ms8i9mp)
2. Create your own [azure container registry](https://portal.azure.com/#browse/Microsoft.ContainerRegistry%2Fregistries) \
    a) You will need to create a new resource group. Use default configs for resource group and container registry. \
    b) Use your initials (e.g. SZE) as prefix for Resource Group
3. Get password of your ACR from your Codespace Terminal. For the moment, we are using the ACR Admin credentials for publishing images to the ACR.
```
az login
az acr update --name <My-Azure-ACR> --admin-enabled true
az acr credential show --name <My-Azure-ACR>
```
4. save (first) password as ACR_PASSWORD in github project settings &rarr; Secrets and variables &rarr; Actions &rarr; Repository secrets

### Publish your Webapp to ACR using gitlab pipelines
Follow the **Tasks B.1 - B.3** in docker-publish.yml. Check that the Actions in your GitHub are executed properly.

### Run ACR image on your local machine (optional)
If Docker is available on your local machine, you can try to run your ACR image locally
```
az acr credential show --name <My-Azure-ACR>
sudo docker login <My-Azure-ACR>.azurecr.io -u <My-Azure-ACR>
sudo docker run -p 3000:3000 <My-Azure-ACR>.azurecr.io/ipt-spins:latest
```

## PART C - Continuous Deployment (Requires Part B)
In this section you are going to create a GitHub Action which runs after the publishing to Azure was successful. 
For this you will need the following:
1. A service plan in azure 

   Create a new plan which uses the free azure plan F1
```bash
az appservice plan create --name <your-plan-name> --resource-group <your-resource-groupe-name> --sku F1 --is-linux
```
2. Create a Web App in azure, where this application is deployed

Make sure to specify your resource-group and set a name
```bash
az webapp create \
     --resource-group <your-resource-groupe-name>  \
     --plan <your-plan-name> \
     --name <your-webapp-name> \
     --deployment-container-image-name <your-container-registry>/ipt-spins:latest
```

3. A Service Principal in Azure which has the contributor role on your resource

```bash
az ad sp create-for-rbac --name "<your-service-principal-name>" --role contributor \
    --scopes /subscriptions/<subscription-id>/resourceGroups/<resource-group> \
    --sdk-auth
```
Store the returned json as secret in the ``<your-repository> ->Settings->Secrets And Variables->Actions secrets and variables``
as new Secret with the name ``AZURE_RESOURCEGROUP_CONTRIBUTOR_SERVICEPRINICIPAL``. Create another Action secret or variable
for the application name with under ``AZURE_WEBAPP_NAME`` containing ``<your-webapp-name> ``.

4. Create a new workflow for GitHub where you deploy the latest version of your application which you published before to the registry.
5. Test your setup by making a change on the codebase (for example make the logo spin faster) and verify that the change is visible on your deployed webapp.

## PART D - Code Quality

### Create SonarCloud Project
1. Login to SonarCloud.io using your **Github Account**
2. Create a new SonarCloud project (within your private SonarCloud organisation) for your github repository (stored in your private github account)
    a) Select 'Previous version' when prompted
3. Create a Security Token (My Account &rarr; Security) and store it in your github project settings as SONAR_TOKEN
4. In the SonarCloud project settings under 'Analysis Method', disable 'Automatic Analysis'. This allows us to use CI Analysis, which provides more control over when the repository is analysed and which data is incorporated (for example test coverage reports).
5. Optional: Check the "Quality Gates" section in your SonarCloud organisation. Your can add and customize your own quality gates.

### Extend your GitHub Actions to use SonarCloud
1. Follow the **Task D.1** in docker-publish.yml to enable SonarCloud analysis for each new Pull Request. \
  a) Use the Project Key and Organization Key found in your SonarCloud project under 'Information'
2. Observe your issues in SonarCloud  ((SonarCloud Project &rarr; Main Branch &rarr; Overall Code &rarr; Maintainability / Security Hotspots). **Fix them**.: \
  a) Issue in **App.tsx** (in Maintainability) \
  b) Issue in **Dockerfile** (in Security Hotspots)

## PART E - Security (Requires Part B)

### Use OIDC instead of Admin credentials
Instead of using the ACR Admin credentials, extend your setup to use OIDC.

## PART F - GitOps (Requires Part B)

### Use ArgoCD
ArgoCD is a heavy used tool to enable gitops. It monitors your github repository and applies the configuration to the configured namespace.

Deploy an AKS cluster and install ArgoCD on it. Then configure ArgoCD to monitor your github repository and apply the configuration to the configured namespace.


## PART G - Dependency Management

### Manage Dependencies
Dependency management is a crucial part of software development. It helps you to keep your dependencies up to date and secure. 

There are multiple tools and technologies to manage dependencies. Check which tool or technology fits best for your project and your needs. Take into account that this solution should be used in enterprise environments with multiple developers and multiple projects.

Add a workflow to your project to automatically update dependencies.

Be careful with permissions and tokens...

## PART H - AI Code Review

Add the capability to your project to automatically review code changes using AI.
 
There are different possibilities to achieve this. For example there are different AI providers and different ways to integrate them into your project. List the advantages and disadvantages of the different approaches and choose the one that best suits your needs.

PS: Keep the trivy incident in mind ;-) 


# Debug / FAQ
### "Build and Push Docker Image" fails with
```
Error response from daemon: Get "https://lrengineering.azurecr.io/v2/": dial tcp: lookup lrengineering.azurecr.io on 127.0.0.53:53: no such host
```
&rarr; Probably, your Azure Container Registry got deleten due to regular cleanup of ipt sandbox. Follow the steps in **PART B** to create a new one.