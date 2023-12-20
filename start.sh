echo "******************************************************"
echo "Starting bup-vector :                                    ";
echo "******************************************************"

#!/bin/bash
app="bup-vector"
docker build -t ${app} .
docker run -d -p 8902:80 \
  --env-file ./docker-gen-ai/local.env \
  --network ailegorretaNet \
  --name=${app} \
  -v $PWD:/app  \
  ${app}
