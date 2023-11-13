# OpenSearch + OpenSearch Dashboards with OpenLDAP authentication backend

This repo provides an example cluster using OpenLDAP as an authentication backend.

## Services

- OpenSearch node (Port: 9200)
- OpenSearch Dashboards (Port: 5601)
- OpenLDAP
- PhpLDAPAdmin (Port: 6443)

## Start the cluster

Clone this repository and navigate to the cloned repo using a terminal.

In the root directory of this project run `docker-compose down && docker-compose up` to start a cluster.

### Making changes in LDAP

Login to PhpLDAPAdmin (https://localhost:6443) using the admin account.

- Username: cn=admin,dc=example,dc=org
- Password: changethis

You can make changes in the directory as the admin

## Default accounts

This repo comes with some default accounts listed in `directory.ldif`


When logging into OpenSearch Dashboards you can use the common name (cn), but you need to use the distinguished name (dn) when logging into PhpLDAPAdmin


```
dn: cn=jroe,ou=People,dc=example,dc=org
objectClass: person
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: top
cn: jroe
userpassword: password
givenname: Jane
sn: Roe
mail: jroe@example.org
uid: 1001

dn: cn=jdoe,ou=People,dc=example,dc=org
objectClass: person
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: top
cn: jdoe
userpassword: password
givenname: John
sn: Doe
mail: jdoe@example.org
uid: 1002

dn: cn=psmith,ou=People,dc=example,dc=org
objectClass: person
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: top
cn: psmith
userpassword: password
givenname: Paul
sn: Smith
mail: psmith@example.org
uid: 1003
```

