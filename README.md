## OpenSearch Demos / Quickstart Demo

This demo will get you up-and-running with a simple OpenSearch & OpenSearch Dashboards instance. You can run it on GitPod in your web browser or using Docker Compose.

### OpenSearch in your Browser (faster & easier)

This repo is GitPod enabled so you can launch the demo in your browser without neededing to download anything.

1. Go to [gitpod.io](https://www.gitpod.io/) and click on "Sign Up"
2. Login using your GitLab, GitHub, or Bitbucket account and follow the prompts to create your account. You only need a free account.
3. Return here and click the button below:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/opensearch-project/demos/tree/quickstart)

4. GitPod will let you know when OpenSearch and OpenSearch Dashboards is ready.

### OpenSearch using Docker Compose

Additional information and troubleshooting for OpenSearch using Docker can be found in [the official documentation](https://opensearch.org/docs/latest/opensearch/install/docker/).

1. Clone this repo or download this branch. Switch into the directory of the newly downloaded repo.
2. Run the following command:
```
cd demo && docker compose --env-file env up
```
3. Wait for everything to download and start up (it may take several minutes). 
4. Launch a web browser and point it at http://localhost:5601 for OpenSearch Dashboards or interact with Opensearch using https://localhost:9200 . The default username/password is `admin`/`admin`


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

