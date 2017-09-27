#!/usr/bin/env bash

echo "Deleting old uploaded version"
rm -r /Users/oleandreashansen/Documents/vtl/uploads/start2.py
sleep 1
echo "Unzipping..."
unzip /Users/oleandreashansen/Documents/vtl/uploads/start2.zip -d /Users/oleandreashansen/Documents/vtl/uploads/
sleep 1
echo "Killing running process"
ps aux | grep start2.py | grep python | awk '{print $2}' | kill -9 $(awk '{print $1}')
sleep 1
echo "Removing old version"
rm -r /Users/oleandreashansen/Documents/vtl/running/start2.py
sleep 1
echo "Moving new project files into position"
mv /Users/oleandreashansen/Documents/vtl/uploads/start2.py /Users/oleandreashansen/Documents/vtl/running/
sleep 1
echo "Starting process"
python /Users/oleandreashansen/Documents/vtl/running/start2.py &