#!/bin/bash

which conda || module load conda && echo "conda loaded"
which fre || conda activate fre-cli && echo "fre loaded"
which mkmf || export PATH=/home/inl/Working/fre-cli/fre/mkmf/bin:$PATH && echo "mkmf in path"
