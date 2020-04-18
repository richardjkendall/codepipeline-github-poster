import boto3
import json
import os
import requests
import base64

ssm = boto3.client("ssm", region_name=os.environ["region"])
gh_access_token = ""

def authorisation(username, access_token):
    auth = base64.b64encode(f"{username}:{access_token}".encode("utf-8")).decode("utf-8")
    return f"Basic {auth}"

def post_to_url(url, auth, payload):
  r = requests.post(
    url, 
    json=payload,
    headers={
      "content-type": "application/json",
      "authorization": auth
    }
  )
  return r.content

def process_record(record):
  record = json.loads(record)
  description = ""
  state = ""
  if record["state"] == "STARTED" or record["state"] == "RESUMED":
    description = "Build run has started."
    state = "pending"
  elif record["state"] == "SUCCEEDED":
    description = "The build was successful."
    state = "success"
  elif record["state"] == "FAILED" or record["state"] == "CANCELED":
    description = "The build failed or was canceled."
    state = "failure"
  elif record["state"] == "SUPERSEDED":
    description = "The build was superseded."
    state = "pending"
  payload = {
    "state": state,
    "description": description,
    "target_url": "https://{region}.console.aws.amazon.com/codesuite/codepipeline/pipelines/{pipeline}/executions/{exec_id}/timeline?region={region}".format(
      pipeline = record["pipeline_name"],
      exec_id = record["exec_id"],
      region = os.environ["region"]
    ),
    "context": "ci/build"
  }
  auth = authorisation(
    username = os.environ["gh_username"],
    access_token = gh_access_token
  )
  post_to_url(
    url = "https://api.github.com/repos/{owner}/{repo}/statuses/{sha}".format(
      owner = record["github"]["owner"],
      repo = record["github"]["repo"],
      sha = record["github"]["sha"]
    ),
    auth = auth,
    payload = payload
  )

def entry(event, context):
  # get github access token
  param = ssm.get_parameter(
    Name=os.environ["gh_access_token"],
    WithDecryption=True
  )
  gh_access_token = param["Parameter"]["Value"]
  for record in event["Records"]:
    process_record(record["body"])

if __name__ == "__main__":
  record = """
{"pipeline_name": "basic-cicd-pipeline-www-rjk-com-develop-rjk-ecs-dev-www-rjk-com-dev", "exec_id": "ed501676-0655-4165-9ae7-7f9b0914380a", "state": "STARTED", "github": {"owner": "richardjkendall", "repo": "www-rjk-com", "branch": "develop", "sha": "b006f33208492110e3fd0ca82d9691d9c4319740"}}
  """
  process_record(record)