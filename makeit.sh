#! /bin/sh
#TARGET=~/git/danintel.github.io
TARGET=~/git/gh-pages/avalon

set -x
make clean
make
cd refman
rm -rf ~/htdocs/dan/refman
copydir ~/htdocs/dan/refman

cp refman.pdf html
#cp refman.pdf $TARGET

cd html
copydir $TARGET
cd $TARGET
#gitadd .
#gitcommit
#git push origin master
