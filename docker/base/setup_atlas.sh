#!/bin/sh
if [ -d /usr/local/atlas ]; then
  update-alternatives --install /usr/lib/libblas.so.3 libblas.so.3 /usr/local/atlas/lib/libtatlas.so 90
  update-alternatives --install /usr/lib/liblapack.so.3 liblapack.so.3 /usr/local/atlas/lib/libtatlas.so 90
fi

