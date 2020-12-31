#!/bin/bash

set -e

pytest -q

pushd acpanel
yarn && yarn build
popd
rm -rf lambdas/static
cp -r acpanel/build lambdas/static
find lambdas -type f | xargs chmod 644
find lambdas -type d | xargs chmod 755

sam build

sam deploy --s3-bucket sam-deployments-941817831 \
    --stack-name acpanel \
    --capabilities CAPABILITY_IAM
