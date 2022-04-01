# Developing Guidelines


## Starting a New Demo

Starting a new demo is simple. Create a new branch based off of another using the following git command.

`git branch -b <new branch name> <branch to start from (typically demo)>`

From here it's reccomended to follow a few simple patterns.

├── demo<br />
│   ├── env<br />
│   ├── docker-compose.yml<br />
│   ├── docker-compose.override.yml<br />
│   ├── kakfa<br />
│   │   ├── config.yml<br />
│   ├── fluentd<br />
│   │   ├── Dockerfile<br />
│   │   ├── config<br />
│   │   │   ├── config.yml<br />

1. docker-compose: It is best to try and leave the original docker-compose file alone to prevent merge conflicts when it is updated. To extend it changes can be made into a docker-compose.override.yml file.
2. Config files: These should be put into nested directory and passed in as a mounted volume whenever necessary. This helps keep the startup time down for the demo.
3. Dockerfile: There are some times when you cannot avoid creating a custom docker image. One example is when you need to add plugins to fluentd. For this, you should create a directory under Demo with the Dockerfile.
4. env: The env file provides a way to pass in specific versions in case certain projects need specific versions to remain compatable. It's recommened to not lock demo versions whenever possible.


## Bootstrapping Local Development

The recommened way to develop is using GitPod. This way all of the prerequisites will be installed automatically using the GitPod.yml file.
