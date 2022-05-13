# Magpie Security Rules

A repository of security policies and associated rules, including test asset definitions.

This repository is packaged into a Maven artifact identified as:

    <groupId>io.openraven.magpie</groupId>
    <artifactId>security-rules</artifactId>

The top level resources folder is to adhere to the Maven convention for resource files, the folder structure within
matches the pre-existing structure defined for rule repositories.

See https://docs.openraven.com/docs/overview-10 for documentation on writing rules for Magpie.


## Rule Validation

To run a rule validation using the SecurityRuleValidator in Magpie core against security rules in Github:

    mvn test -f . -pl magpie-core -Dtest=SecurityRuleValidator

A VM property can also be specified to define either a local repository or a different remote, e.g:

    -Drepository="~/projects/security-rules"
    -Drepository="https://github.com/openraven/security-rules.git"



