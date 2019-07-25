#!/usr/bin/env bash -e

function error_no_deps {
  echo "Please install version-incrementor before running this script"
  echo 
  echo "pip install -i https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple version-incrementor"
  echo
  exit 1
}

command -v prepare-release || error_no_deps

prepare-release
git add .version && git commit -m "Release $(cat .version)" && git push
cut-release

