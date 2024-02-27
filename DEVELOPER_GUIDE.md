# Developing Guidelines

## Starting a New Demo

There are only a few steps to create a demo. Create a new branch based off of another using the following git command.

`git branch -b <new branch name> <branch to start from (typically demo)>`

From here it's recommended to follow a few patterns.

```
# Folder Structure
└── demo
    ├── env
    ├── docker-compose.yml
    ├── docker-compose.override.yml
    ├── kakfa
    │   └── config.yml
    └── fluentd
        ├── Dockerfile
        └── config
            └── config.yml
```


1. `docker-compose`: It is best to try and leave the original docker-compose file alone to prevent merge conflicts. To extend it make changes in a `docker-compose.override.yml` file.
2. Config files: Put these into a nested directory and pass them in as a mounted volume. This helps keep the startup time down for the demo.
3. `Dockerfile`: There are some times when you cannot avoid creating a custom docker image. One example is when you need to add plugins to the fluentd container. For this, you should create a directory under Demo with the Dockerfile.
4. `env`: The `env` file provides a way to pass in environment variables. Use this when containers require specific versions to be compatible or for any other parameters you might like to pass in. It's recommended to not lock container versions whenever possible.


## Bootstrapping Local Development

While these demos were developed to be run on GitPod you can setup your development environment locally like so:


### Pre-Commit

Pre-Commit helps keep all the commits coming in well linted and provides nice reminders if you forget to sign the DCO.

```
pip install pre-commit
pre-commit install --install-hooks -t pre-commit -t commit-msg
```

### Docker Compose

Docker Compose is used to spin up and configure all the containers. The environment file `.env` defined in the `demo` folder will be read to configure environment variables for `docker-compose.yml`.

```zsh
# Checkout `demo` folder
cd demo

# Running
docker-compose up

# Stopping
docker-compose down
```

Note: To setup a fresh cluster every run, pass option `-v` to `docker-compose down` command.