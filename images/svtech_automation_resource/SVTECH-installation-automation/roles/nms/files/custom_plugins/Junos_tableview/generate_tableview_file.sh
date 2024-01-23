#!/bin/bash

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export FILE=$(ls $DIR| grep ".yml" |sed 's/.yml//g')

if [ ! -d "$DIR/rundeck" ]; then
  mkdir $DIR/rundeck
fi

echo [ > $DIR/rundeck/list_tableview
for i in $FILE
do
  echo "\""$i"\"," >> $DIR/rundeck/list_tableview
done
echo ] >> $DIR/rundeck/list_tableview

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export FILE=$(ls $DIR| grep ".yml" |sed 's/.yml//g')

for i in $FILE
do
  if [ ! -d "$DIR/rundeck/$i" ]; then
    mkdir $DIR/rundeck/$i
  fi
  echo [ > $DIR/rundeck/$i/list_datatype
  cat $DIR/$i.yml  |grep -e "^.*:" | grep -v " \|_" | sed 's/view://g' | sed 's/Table//g' | sed 's/://g' |sed 's/^/"/g' | sed 's/$/",/g' >> $DIR/rundeck/$i/list_datatype
  echo ] >>  $DIR/rundeck/$i/list_datatype
done
