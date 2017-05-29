# Create Josh Infra Structure
#878911958671
provider "aws" {}

variable "accountId" {}
variable "bucket_name" {}
variable "public_key_file" {}

resource "aws_key_pair" "joshkeypair" {
  key_name   = "josh"
  public_key = "${file("${var.public_key_file}")}"
}

resource "aws_dynamodb_table" "josh_dynamodb_table" {
  name           = "scheduler"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  tags {
    Name = "scheduler"
  }
}

resource "aws_iam_role" "josh_lambda_role" {
  name = "josh_lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com",
        "Service": "ec2.amazonaws.com",
        "Service": "dynamodb.amazonaws.com",
        "Service": "autoscaling.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "josh-policy" {
  name        = "josh_policy"
  path        = "/"
  description = "Josh Policy"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "autoscaling:*",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:us-west-2:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:UpdateItem",
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:PutItem"
            ],
            "Resource": "arn:aws:dynamodb:us-west-2:*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:*",
            "Resource": "*"
        }
    ]
}
EOF
}

resource "aws_iam_policy_attachment" "attach" {
  name       = "josh-attachment"
  roles      = ["${aws_iam_role.josh_lambda_role.name}"]
  policy_arn = "${aws_iam_policy.josh-policy.arn}"
}

resource "aws_lambda_function" "josh" {
  filename         = "josh.zip"
  function_name    = "josh"
  role             = "${aws_iam_role.josh_lambda_role.arn}"
  handler          = "scheduler.lambda_handler"
  source_code_hash = "${base64sha256(file("josh.zip"))}"
  runtime          = "python3.6"

  environment {
    variables = {
      IMAGE_ID = "ami-a8b320c8"
    }
  }
}

resource "aws_api_gateway_rest_api" "joshAPI" {
  name        = "joshAPI"
  description = "This is Job Scheduler API"
}

resource "aws_api_gateway_resource" "joshResource" {
  rest_api_id = "${aws_api_gateway_rest_api.joshAPI.id}"
  parent_id   = "${aws_api_gateway_rest_api.joshAPI.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "joshAnyMethod" {
  rest_api_id   = "${aws_api_gateway_rest_api.joshAPI.id}"
  resource_id   = "${aws_api_gateway_resource.joshResource.id}"
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "integration" {
  rest_api_id             = "${aws_api_gateway_rest_api.joshAPI.id}"
  resource_id             = "${aws_api_gateway_rest_api.joshAPI.root_resource_id}"
  http_method             = "${aws_api_gateway_method.joshAnyMethod.http_method}"
  integration_http_method = "ANY"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:us-west-2:lambda:path/2015-03-31/functions/${aws_lambda_function.josh.arn}/invocations"
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.josh.arn}"
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:us-west-2:${var.accountId}:${aws_api_gateway_rest_api.joshAPI.id}/*/${aws_api_gateway_method.joshAnyMethod.http_method}/resourcepath/subresourcepath"
}

resource "aws_api_gateway_deployment" "Deployment" {
  depends_on = ["aws_api_gateway_method.joshAnyMethod"]

  rest_api_id = "${aws_api_gateway_rest_api.joshAPI.id}"
  stage_name  = "prod"
}

resource "aws_s3_bucket" "josh" {
  bucket = "${var.bucket_name}"
  acl    = "public-read"
}

resource "aws_s3_bucket_object" "object" {
  depends_on = ["aws_s3_bucket.josh"]
  bucket     = "${var.bucket_name}"
  key        = "docker_listen.py"
  source     = "./scripts/docker_listen.py"
  etag       = "${md5(file("./scripts/docker_listen.py"))}"
  acl        = "public-read"
}

output "api_url" {
  value = "${aws_api_gateway_deployment.Deployment.invoke_url}"
}

output "s3_object" {
  value = "${aws_s3_bucket_object.object.metadata}"
}
