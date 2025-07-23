#!/bin/bash

# SNS Topic 생성
awslocal sns create-topic --name my-local-topic

# SQS Queue 생성
awslocal sqs create-queue --queue-name my-local-queue

# ARN 추출
TOPIC_ARN=$(awslocal sns list-topics --query "Topics[?contains(TopicArn, 'my-local-topic')].TopicArn" --output text)
QUEUE_URL=$(awslocal sqs get-queue-url --queue-name my-local-queue --output text)
QUEUE_ARN=$(awslocal sqs get-queue-attributes --queue-url "$QUEUE_URL" --attribute-name QueueArn --query "Attributes.QueueArn" --output text)

# SNS → SQS 구독
awslocal sns subscribe \
  --topic-arn "$TOPIC_ARN" \
  --protocol sqs \
  --notification-endpoint "$QUEUE_ARN"

# SQS에 SNS 메시지를 허용하는 정책 설정
POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "$QUEUE_ARN",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "$TOPIC_ARN"
        }
      }
    }
  ]
}
EOF
)

awslocal sqs set-queue-attributes \
  --queue-url "$QUEUE_URL" \
  --attributes Policy="$POLICY"