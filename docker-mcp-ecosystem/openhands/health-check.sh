#!/bin/bash

# Überprüfe, ob OpenHands läuft
if curl -s http://localhost:8080/health > /dev/null; then
    exit 0
else
    exit 1
fi