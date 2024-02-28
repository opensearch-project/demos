## OpenSearch SAML demo

This branch contains the demo setup for testing SAML auth.

Note: These steps require basic knowledge about interacting with Github. If you are new to Github, please check-out this [onboarding guide](https://github.com/opensearch-project/demos/blob/main/ONBOARDING.md) to get started.

1. Navigate to the `demo` folder:
   ```zsh
   $ cd <path-to-demos-folder>/demo
   ```

1. Review the following files, as needed:

   * `.env`: 
     * Defines the OpenSearch and OpenSearch Dashboards version to use. The default is the latest version ({{site.opensearch_major_minor_version}}).
     * Defines the `OPENSEARCH_INITIAL_ADMIN_PASSWORD` variable required by versions 2.12 and later.
   * `./custom-config/opensearch_dashboards.yml`: Includes the SAML settings for the default `opensearch_dashboards.yml` file.
   * `./custom-config/config.yml`: Configures SAML for authentication.
   * `docker-compose.yml`: Defines an OpenSearch server node, an OpenSearch Dashboards server node, and a SAML server node.
   * `./saml/config/authsources.php`: Contains the list of users that can be authenticated by this SAML domain.

2. At the command line, run:
   ```zsh
   $ docker-compose up.
   ```

3. Access OpenSearch Dashboards at [http://localhost:5601](http://localhost:5601){:target='\_blank'}.

4. Select `Log in with single sign-on`. This redirects you to the SAML login page.

5. Log in to OpenSearch Dashboards with a user defined in `./saml/config/authsources.php`. (such as, `user1` and `user1pass`)

6. After logging in, note that the user ID shown in the upper-right corner of the screen is the same as the `NameID` attribute for the user defined in `./saml/config/authsources.php` of the SAML server (that is, `saml-test` for `user1`).

7. If you want to examine the SAML server, run `docker ps` to find its container ID and then `docker exec -it <container-id> /bin/bash`.

   In particular, you might find it helpful to review the contents of the `/var/www/simplesamlphp/config/` and `/var/www/simplesamlphp/metadata/` directories.

For more details around SAML and OpenSearch check out the [official documentation](https://opensearch.org/docs/latest/security/authentication-backends/saml).

## Code of Conduct

This project has adopted an [Open Source Code of Conduct](CODE_OF_CONDUCT.md).

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This project is licensed under the Apache-2.0 License.

## Copyright

Copyright OpenSearch Contributors. See [NOTICE](NOTICE) for details.