#!/bin/bash



echo $1 | base64 --decode | kitten icat
