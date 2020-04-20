# codepipeline-github-poster
A lambda function which posts status updates back to github to indicate CI/CD status

## How it works
This lambda function picks up messages from an SQS queue and calls the Github status API to post information back to the source code repository which triggered the pipeline in the first place.

The Github API which is used is documented here https://developer.github.com/v3/repos/statuses/

It is designed to work with the codepipeline-enricher.

## Messages
Messages are expected to be structured as follows

```
{
  "pipeline_name": "<name of the pipeline>", 
  "exec_id": "<pipeline execution id>", 
  "state": "<pipeline state>", 
  "github": {
    "owner": "<github order: user or team>", 
    "repo": "<github repository name>", 
    "branch": "<branch>", 
    "sha": "<commit sha hash>"
  }
}
```

## Deploying
There is a terraform module which deploys this along with all the other bits and pieces it needs to work. You can find it here: https://github.com/richardjkendall/tf-modules/tree/master/modules/github-status-updater
