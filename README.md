# Open Raven Security Rules Documentation

# Overview

Security Rules are what power the ability to scan your discovered assets with the magpie-policy scan. The current maintained rules from Open Raven can be accessed in the following repository: https://github.com/openraven/security-rules/tree/main/rules.

The main purpose behind security rules are to check the configurations of assets in your cloud based provider account(s). These can either be based on config rules, like those provided by AWS for example or custom written to meet your needs. We have examples of both types in our rules-repository.

The distinguishing details between our security rules and product based data rules are:

**Data Rules:**
- Data rules check for violations found during product based scans.
- They will be in violation if the scan logs a particular data-class in the asset that the rule checks for.

**Security Rules:**
- Security Rules check information gathered about your assets from the magpie-discovery scans.
- These rules are in violation if assets exist that meet the specific configuration that the rule checks for against the selected asset types.


# Security Rule Format

### Naming Structure

Rule naming is based the documentation of https://comparecloud.in/, where cloud features are normalised under the same categories across platforms. This is to avoid having the different naming conventions for essentially services with the same functionality across created rules.

The current naming structure is as follows: ```{cloud_platform}-{service_name}-{rule_descriptor}```. An example of this for Dynamo DB on AWS would be: ```aws-database-{rule_descriptor}``` as it resides on AWS and in [https://comparecloud.in/](https://comparecloud.in/) DynamoDB is categorised under ```Database```. The rule descriptor then follows in the same lowercase seperated by ```-```.

### Rule Structure

The structure of the security rules themselves follows the format below:

```
ruleId: aws-database-dynamodb-table-encrypted-kms  
type: asset  
ruleName: >  
  Checks if Amazon DynamoDB table is encrypted with AWS Key Management Service (KMS).  
description: >  
  The rule is NON_COMPLIANT if Amazon DynamoDB table is not encrypted with AWS KMS.  
  The rule is also NON_COMPLIANT if the encrypted AWS KMS key is not present in kmsKeyArns input parameter.  
severity: high  
enabled: true  
sql: >  
  SELECT arn  
  FROM ${magpie_schema}.awsdynamodbtable  
  WHERE configuration->'sseDescription' = 'null'  
  OR configuration->'sseDescription'->>'sseType' != 'KMS';  
remediationDocURLs: https://github.com/openraven/security-rules/wiki  
version: 0.9
```

- ```ruleId``` - Specify the name of the rule file - minus the .yaml extension, more details on rule naming structure is specified in the next section.
- ```type``` - Specify the type as a data-based rule or an asset-based rule.
- ```ruleName``` - Specify the extended name of the rule, with more description as to it's function.
- ```description``` - Specify the conditions under which the rule is NON_COMPLAINT, i.e. in violation of the rule.
- ```severity``` - Specify the severity of the rule: low, medium, high.
- ```enabled``` - Specify boolean value whether the rule is enabled during scanning or disabled i.e true/false.
- ```sql``` - Specify the Postgres SQL query you want the rule to execute.
- ```remediationDocURLs``` - Specify the resources for remediating this issue.
- ```version``` - Specify the version of this rule.

You can see an example of how to formulate queries and python for security rules in the following two sections.

# Policies & Their Relationship To Rules

Policies are essentially a collection of individual rules, which are used for for the policy scans of magpie. An example policy that currently exists can be seen below:

```
policyId: aws-cis-foundations-benchmark  
policyName: CIS AWS Foundations Benchmark controls  
cloudProvider: AWS  
description: >  
  The benchmark enables organizations operating in the cloud to ensure their IT infrastructure is safeguarded against cyber threats and attacks.  
  The AWS CIS benchmark provides guidelines for configuring the security options of foundational AWS services.  
enabled: true  
rules:  
  - aws-iam-and-security-iam-root.yaml # CIS 1.1  
  - aws-iam-and-security-iam-user-mfa-enabled.yaml # CIS 1.2  
  - aws-iam-and-security-iam-user-unused-credentials-check.yaml  # CIS 1.3  
  ...
version: 0.9
```

- ```policyId``` - Specify the name of the policy file - minus the .yaml extension.
- ```policyName``` - Specify a formal policy name, should be easy to understand and informative.
- ```cloudProvider``` - Specify the Cloud Provider the policy belongs to, either ```AWS``` or ```GCP```.
- ```description``` - Specify what the purpose of the policy is and a general context of what is included within.
- ```enabled``` - Specify boolean value whether the policy is enabled during scanning or disabled i.e true/false.
-  ```rules``` - Specify the exact file name of the rules you want to be executed during this policy.
- ```version``` - Specify the version of this policy.

In Summary you create a policy, enable it and it will execute all of the individual rules within the policy on your discovered assets and provide the results under that specific policy.

# Writing SQL Queries for Rules

The database schema is very important to know when writing rules for your assets, as you want to be able to query the correct table and columns to ensure your rule works correctly.

The generic database schema for all asset types can be seen here:

```
CREATE TABLE IF NOT EXISTS aws(
	documentid TEXT primary key not null,
	arn TEXT,
	resourcename TEXT,
	resourceid TEXT,
	resourcetype TEXT,
	awsregion TEXT,
	awsaccountid TEXT,
	creatediso TIMESTAMPTZ,
	updatediso TIMESTAMPTZ,
	discoverysessionid TEXT,
	tags JSONB,
	configuration JSONB,
	supplementaryconfiguration JSONB,
	discoverymeta JSONB
);

CREATE TABLE IF NOT EXISTS gcp (
	documentid TEXT primary key not null,
	assetid TEXT,
	resourcename TEXT,
	resourceid TEXT,
	resourcetype TEXT,
	region TEXT,
	gcpaccountid TEXT,
	projectid TEXT,
	creatediso TIMESTAMPTZ,
	updatediso TIMESTAMPTZ,
	discoverysessionid TEXT,
	tags JSONB,
	configuration JSONB,
	supplementaryconfiguration JSONB,
	discoverymeta JSONB
);
```

Each individual asset type does have it's own table and the list of tables for asset types can be seen here: https://github.com/openraven/magpie/blob/main/magpie-persist/src/main/resources/db/migration/V2__create_static_type_tables.sql,  with each specific asset type inheriting the schema from either the ```aws``` or ```gcp``` table.

Generally the most import columns within these tables for rule writing are ```configuration``` and ```supplementaryconfiguration``` as these contain JSON blobs that usually contain a good degree of data as to how the asset is configured. These can be accessed through Postgres SQL queries to match specific data components in your rules. A good resource to familiarise yourself with accessing data within JSON blobs in Postgres columns is: https://www.postgresqltutorial.com/postgresql-json/

### Breaking down an existing rule:

In order to give the best understanding when writing your own custom rules, the rule above will be broken down as a guide.

```
SELECT arn 
FROM ${magpie_schema}.awsdynamodbtable 
WHERE configuration->'sseDescription' = 'null' 
OR configuration->'sseDescription'->>'sseType' != 'KMS';
```

- ```${magpie_schema}``` - is defined to make the schema of the Postgres table configurable rather than static, therefor you can modify this in the config.yaml file in your magpie build and all the rules will work regardless.
- ```awsdynamodbtable``` refers to the asset type, which in the case here is Dynamo DB - if this were S3 it would be ```awss3bucket```, the correct table naming for asset types can be found here: https://github.com/openraven/magpie/blob/main/magpie-persist/src/main/resources/db/migration/V2__create_static_type_tables.sql
- ```configuration->'sseDescription' = 'null'``` is accessing the ```configuration``` JSON blob for the ```sseDescription``` datapoint and then checking if this is null.
- ```configuration->'sseDescription'->>'sseType' != 'KMS'``` is again accessing the ```configuration``` JSON blob and accessing the data point ```sseDescription``` and then accessing the ```sseType```  point within the ```sseDescription``` data structure. Using ```->>``` instead of ```->``` extracts this as text so it can be compared directly to another string.

Notable points when writing rules for Magpie:

- Avoid the usage of ```::``` to cast data-types as this does not work with the Hibernate setup.
- Always use ```CAST``` for example - ```(CAST(permissions->>'fromPort' AS INT)```
- Use ```jsonb_array_elements``` to access JSON array elements when required for example - ```jsonb_array_elements(supplementaryconfiguration->'dbClusters'->'dbClusters')```

This should be everything required for you to know in order to write your own custom rules for Magpie! Just make sure to introduce your queries under the ```sql: >``` in the YAML rule file.

# Writing Python for Rules

Magpie supports the usage of executing Python on extracted results from SQL queries to give additional processing power. This is an extremely useful feature as it removes some of the restraints faced in a query language.

An example of a current Python based rule:

``` 
ruleId: aws_sg_botnet_access  
type: asset  
ruleName: >  
  Security group allows outobund access to known botnet C&C addresses  
description: >  
  Security group ingress and egress rules should be locked down to the minimal set of permitted IP  
  ranges.  This rule checks that security groups do not allow IP egress to known botnet command and control  
  IP addresses.  
severity: medium  
enabled: false  
sql: >  
  SELECT arn, resourceId, configuration  
  FROM ${magpie_schema}.awsec2securitygroup;  
eval: >  
  import json  
  cnc_ips = {  
    # https://exchange.xforce.ibmcloud.com/collection/Botnet-Command-and-Control-Servers-7ac6c4578facafa0de50b72e7bf8f8c4  
    '131.253.18.12',  
    '187.20.38.214',  
    '217.147.169.242',  
	... 
  }
    
  def addressInNetwork(ip, net):  
    import socket,struct  
    ipaddr = int(''.join([ '%02x' % int(x) for x in ip.split('.') ]), 16)  
    netstr, bits = net.split('/')  
    netaddr = int(''.join([ '%02x' % int(x) for x in netstr.split('.') ]), 16)  
    mask = (0xffffffff << (32 - int(bits))) & 0xffffffff  
    return (ipaddr & mask) == (netaddr & mask)
      
  def evaluate(results):  
    findings = []  
    for sg in results:  
      configuration = json.loads(sg['configuration'].getValue())  
      for egress in configuration['ipPermissionsEgress']:  
        for ip_range in egress['ipRanges']:  
          cidr = ip_range['cidrIp']  
          for ip in cnc_ips:  
            if addressInNetwork(ip, cidr):  
              findings.append({'arn': sg['arn']})  
              break  
    return findings
      
remediation: >  
  In the AWS Management Console, go to EC2->Security Groups. For each group found by this rule:  
  1) Select the given rule  
  2) Choose the 'Outbound Rules' tab  
  3) Click 'Edit outbound rules'  
  4) Edit any CIDR / IP addresses and minimize the permitted scope to just the minimum required for connectivity.  
remediationDocURLs:  
version: 0.1.0
```

These follow the exact same structure as normal rules, just the output is evaluated in Python via the ```eval: >``` specification in the YAML.

The ```def evaluate(results):``` method is what evaluates the results from the Postgres query and in the context of the above rule loads the returned JSON data in Python for interpretation against a hard-coded Python array.

The rule above gives a great example of how you can interpret the results of the query, process them and return the results back to the magpie policy engine by returning the ```findings``` array with newly appended data.

In summary rules are not confined to the restrictions of just queries, these queries can also be interpreted in Python by adding ```eval: >```  to the YAML rule file. The results of the query are interpretable by calling the ```def evaluate(results):```, where data can be interpreted and manipulated from there and finally returned back to the policy engine in the correct format.


# Integration Tests

Integration tests are the best way to identify that rules work as intended, these tests are stored in the ```/openraven/security-rules/resources/tests``` directory and follow this layout:

```
ruleId: aws-database-dynamodb-pitr-enabled  
cloudProvider: aws  
description: >  
      - Checks that point in time recovery (PITR) is enabled for Amazon DynamoDB tables.  
      - `no-pitr` Insecure Assets have no PITR  
      - `pitr` Secure Assets have PITR  
insecureAssets:
  no-pitr: >  
	[]
secureAssets:  
  pitr: >  
    []
```

- ```ruleId``` - Specify the name of the rule file you want the test to execute with the .yaml extension
- ```cloudProvider``` - Specify the the cloud provider the asset belongs to, i.e. ```aws``` or ```gcp```
- ```description``` - Specify what the test checks for and conditions under which assets are secure and insecure.
- ```insecureAssets``` - Specify the name of the insecure asset that will be returned in the query i.e. ```no-pitr``` here followed by JSON data in between ```[]```
- ```secureAssets``` - Specify the name of the secure asset that will be returned in the query i.e. ```pitr``` here followed by JSON data in between ```[]```

The JSON data mentioned above so correspond to an asset found during discovery and looks something like this:

```
[ {  
    "documentId" : "",  
    "arn" : "pitr",  
    "resourceName" : "pitr",  
    "resourceId" : "pitr",  
    "resourceType" : "AWS::DynamoDB::Table",  
    "awsRegion" : "us-east-1",  
    "awsAccountId" : "",  
    "createdIso" : "2021-12-14T12:17:50.065Z",  
    "updatedIso" : "2021-12-14T14:49:18.992172Z",  
    "discoverySessionId" : null,  
    "maxSizeInBytes" : null,  
    "sizeInBytes" : null,  
    "configuration" : {  
      "attributeDefinitions" : [ {  
        "attributeName" : "sdfg",  
        "attributeType" : "S"  
      }, {  
        "attributeName" : "sdfgx",  
        "attributeType" : "S"  
      } ],  
      "tableName" : "testing123",  
      "keySchema" : [ {  
        "attributeName" : "sdfg",  
        "keyType" : "HASH"  
      }, {  
        "attributeName" : "sdfgx",  
        "keyType" : "RANGE"  
      } ],  
      "tableStatus" : "ACTIVE",  
      "creationDateTime" : "2021-12-14T12:17:50.065Z",  
      "provisionedThroughput" : {  
        "lastIncreaseDateTime" : null,  
        "lastDecreaseDateTime" : null,  
        "numberOfDecreasesToday" : 0,  
        "readCapacityUnits" : 0,  
        "writeCapacityUnits" : 0  
      },  
      "tableSizeBytes" : 0,  
      "itemCount" : 0,  
      "tableArn" : "arn:aws:dynamodb:us-east-1:00000000:table/testing123",  
      "tableId" : "",  
      "billingModeSummary" : {  
        "billingMode" : "PAY_PER_REQUEST",  
        "lastUpdateToPayPerRequestDateTime" : "2021-12-14T12:17:50.065Z"  
      },  
      "localSecondaryIndexes" : null,  
      "globalSecondaryIndexes" : null,  
      "streamSpecification" : null,  
      "latestStreamLabel" : null,  
      "latestStreamArn" : null,  
      "globalTableVersion" : null,  
      "replicas" : null,  
      "restoreSummary" : null,  
      "sseDescription" : {  
        "status" : "ENABLED",  
        "sseType" : "KMS",  
        "kmsMasterKeyArn" : "",  
        "inaccessibleEncryptionDateTime" : null  
      },  
      "archivalSummary" : null  
    },  
    "supplementaryConfiguration" : {  
      "continuousBackups" : {  
        "continuousBackupsDescription" : {  
          "continuousBackupsStatus" : "ENABLED",  
          "pointInTimeRecoveryDescription" : {  
            "pointInTimeRecoveryStatus" : "ENABLED",  
            "earliestRestorableDateTime" : "2021-12-14T14:24:46Z",  
            "latestRestorableDateTime" : "2021-12-14T14:44:21.219Z"  
          }  
        }  
      },  
      "tags" : { },  
      "awsBackupJobs" : [ ]  
    },  
    "tags" : { },  
    "discoveryMeta" : { }  
}]
```

### Notable Points:

- You have to ensure the configurations differ between your ```secure``` and ```insecure``` assets here.
- Make sure the name of your ```secure``` and ```insecure``` assets match up with the ```arn``` in the JSON data.
- You can run the Integration tests using: ```mvn test -f . -pl magpie-core -Dtest=SecurityRuleValidator``` from your magpie root directory.
- Ensure the rule exists in a policy before running its test.
- Please be careful not to include AWS account ID's or Asset specific ID's in your tests, although not sensitive it is considered best practices to avoid this.

=======
# Magpie Security Rules
See https://docs.openraven.com/docs/overview-10 for documentation on writing rules for Magpie.
