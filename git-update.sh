#!/bin/bash

# http://sixarm.com/about/git-pull-for-many-repository-directories.html
# And in case the worst happens - http://web.archive.org/web/*/http://sixarm.com/about/git-pull-for-many-repository-directories.html

if [ -z "$1" ]; then
    echo "Need to supply directory to search for git repos"
    exit 1
fi

find "$1" -type d -name .git | xargs -n 1 dirname | sort | while read line; do echo $line && cd $line && git pull; done
