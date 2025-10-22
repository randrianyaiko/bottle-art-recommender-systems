#!/bin/bash

set -e  # Exit on any error

# Configuration
LAYER_BUCKET="lambda-layers-bucket-202510"
COMMIT_SHA="latest"
AWS_REGION="eu-central-1"

echo "🔨 Building Lambda layers with commit SHA: $COMMIT_SHA"

# Create temporary directories
mkdir -p layers/authorizer/python
mkdir -p layers/common/python

# Build Authorizer Layer (PyJWT only)
echo "📦 Building Authorizer Layer..."
cd layers/authorizer
pip install PyJWT -t python/ --no-cache-dir
zip -r authorizer-layer.zip python/
aws s3 cp authorizer-layer.zip "s3://$LAYER_BUCKET/layers/authorizer-layer-$COMMIT_SHA.zip" --region $AWS_REGION
echo "✅ Authorizer layer uploaded to S3"

# Build Common Layer (requirements.txt)
echo "📦 Building Common Layer..."
cd ../common
if [ -f ../../../requirements.txt ]; then
    pip install -r ../../../requirements.txt -t python/ --no-cache-dir
else
    echo "❌ requirements.txt not found!"
    exit 1
fi
zip -r common-layer.zip python/
aws s3 cp common-layer.zip "s3://$LAYER_BUCKET/layers/common-layer-$COMMIT_SHA.zip" --region $AWS_REGION
echo "✅ Common layer uploaded to S3"

# Cleanup
cd ../..
rm -rf layers/

echo "🎉 All layers built and uploaded successfully!"
echo "📝 Layer versions to use in Terraform:"
echo "   authorizer_layer_version = \"$COMMIT_SHA\""
echo "   common_layer_version = \"$COMMIT_SHA\""