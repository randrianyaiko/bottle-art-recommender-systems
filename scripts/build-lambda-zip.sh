zip -r code.zip src lambda_handlers

BUCKET_NAME=lambda-function-codes-202510261

aws s3 cp code.zip "s3://$BUCKET_NAME/lambda_code/code.zip"