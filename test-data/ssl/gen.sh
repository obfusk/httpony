#!/bin/bash
openssl req -x509 -newkey rsa:2048 -keyout localhost.key \
  -out localhost.crt -days 3600 -nodes -config conf
