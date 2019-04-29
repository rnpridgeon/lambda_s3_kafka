#!/bin/bash
#

set -e

if [[ $(uname -s) != "Linux" ]]; then
    # Virtualenv in deployment package must be created on Linux,
    # run this script in a docker linux instance if we're on a
    # different OS (OSX)
    exec docker run -v $PWD:/v dacut/amazon-linux-python-3.6 /v/$(basename $0) $*
fi


PKGNAME=$1

if [[ -z "$PKGNAME" ]]; then
    echo "Usage: $0 <packagename>" 1>&2
    exit 1
fi

if [[ $PKGNAME != *.zip ]]; then
    PKGNAME="${PKGNAME}.zip"
fi

if [[ $PKGNAME != /* ]]; then
    PKGNAME="$PWD/$PKGNAME"
fi

stagedir=$(mktemp -d -p . stage-XXXXXXX)

if [[ ! -f venv/bin/activate ]]; then
    virtualenv -p python3.6 venv
fi

source venv/bin/activate

pip install -r requirements.txt

# Clean up packages not needed during runtime
pip uninstall -y setuptools docutils

(cd "$VIRTUAL_ENV/lib/python3.6/site-packages/" && zip -r9 $PKGNAME .)
zip -g "$PKGNAME" lambda_s3_kafka.py

deactivate

echo "$PKGNAME created"
du -sh "$PKGNAME"


rm -rf "$stagedir"

