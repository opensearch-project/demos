<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'opensearch-saml-login' => array(
        'exampleauth:UserPass',
        'user1:user1pass' => array(
            'uid' => array('1'),
            'eduPersonAffiliation' => array('group1'),
            'NameID' => 'saml-test',
            'email' => 'user1@example.com',
            'Role' => array('admin'),
        ),
    ),

);
