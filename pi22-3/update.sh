#! /bin/bash
for x in *; 
  do
  git submodule init $x
  git submodule update $x
  echo "update done $x"; 
done