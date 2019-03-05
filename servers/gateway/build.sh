#!/usr/bin/env bash

GOOS=linux go build
docker build -t gebizar/capstonegateway .
go clean