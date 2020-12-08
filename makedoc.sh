#!/bin/sh
#/usr/bin/epydoc -o htmldoc --html --no-frames --show-private --show-sourcecode --separate-classes src/pers/*
/usr/bin/epydoc -o htmldoc --html --no-frames --show-private --show-sourcecode --separate-classes --inheritance=grouped --graph=all src/pers/*
#/usr/local/bin/epydoc -o htmldoc --html --no-frames --show-private src/*

