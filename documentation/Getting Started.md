### Getting started with Demos repo

- Make sure you have installed git and configured your username and email
- Fork [Demos Repo](https://github.com/opensearch-project/demos) by clicking the fork button
- Open up the repo that you have just forked, for example when I forked the demos repo my own repo was http://github.com/lucasWang750/demos/
- Now open up VS Code
- On top of VS Code choose File and click open a folder where you would like to install the Demo folder to
- Once you are in a folder, on top of VS Code click Terminal and New Terminal. This should open up a new terminal window on the bottom of you VS Code. (Note: If you are on Windows, on the top right of the terminal window, click the dropdown next to the plus icon and change into the Git Bash terminal.)
#### 1. Clone repo
- Inside this terminal, clone the repository you just forked
```
git clone http://github.com/YOUR_USERNAME/demos.git
```
For example I would type
```
git clone http://github.com/LucasWang750/demos.git
```
#### 2. CD into new repo
- Change into your new directory, you should also open the folder on VS Code files tab on the left hand side.
```
cd demos
```
#### 3. Switch into correct branch
- Once you clone you might notice it is not the right branch of the demos repo. That is because we are working on the DocBot branch. To switch to that branch type:
- To see all the branches type:
```
git branch -v -a
```
- You should see that there is a remotes/origin/docbot branch. Lets switch into that branch:
```
git switch docbot
```
#### 4. New Branch and Code
- Now it's the familiar territory of making your own branch, making changes and pushing to main
```
git checkout -b "YOUR BRANCH NAME"
```
- To start coding follow the README.md file. Some people have issues with downloading the dependencies. I suggest following the optional Step 5 virtual environment at this point.
- Once you made some edits
```
git add .
git commit -s -m "YOUR COMMIT MSG"
git push origin "YOUR BRANCH NAME"
```
- Then on the ORIGINAL demos repo, you can make a pull request. (NOTE: you have to select base:docbot)
- EXAMPLE: if I make a new feature I would do this
- 1. make a new branch
```
git checkout -b lucaswang750/ingestion
```
- 2. write code then commit and push it
```
git add .
git commit -s -m "Made blah blah changes to ingestion.py
git push origin lucaswang750/ingestion
```
- 3. Go on the https://github.com/opensearch-project/demos/pulls to make a PR
#### 5. Virtual Environment (Optional)
- Virtual Environment allows for packages to be independently installed for a specific project
- I use Conda for Virtual Environment, feel free to use other ones such as pyenv as well
- First install Conda from [online](https://conda.io/docs/user-guide/install/) (You only need mini-conda).
- Now inside VS Code terminal again
```
conda create -n "YOUR ENVIRONMENT NAME" python=3.11 anaconda
conda activate "YOUR ENVIRONMENT NAME"
```
- Once you are done writing code for Demos
```
conda deactivate "YOUR ENVIRONMENT NAME"
```
- I suggest to activate everytime you re-open VS Code and deactivate when you close it out. This way you won't accidentally use this virtual environment somewhere else.
### OpenSearch Docker
- Follow this [guide](https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker/) (NOTE: Do not follow the IMPORTANT HOST SETTINGS portion if you are not on Linux)
- When you run this command, run it from within the demos/demo folder. You should see that there is already a docker-compose.yml file there to use.
```
docker-compose up -d
```
