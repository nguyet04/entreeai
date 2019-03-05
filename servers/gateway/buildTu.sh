#!/usr/bin/env bash

GOOS=linux go build
docker build -t nguyet04/capstonegateway .
go clean