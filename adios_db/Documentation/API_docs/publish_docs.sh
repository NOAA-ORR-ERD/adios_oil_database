#!/bin/sh

# simple script to "publish" the docs -- really all it does is
# rebuild them and copy them to the /docs dir, and updated git,
# so gitHub pages will work.

./build_api_docs.sh
make html
rm -rf ../../../docs/*
cp -R build/html/ ../../../docs/

pushd ../../../docs
git add -A
git commit -m "update published docs"
popd

