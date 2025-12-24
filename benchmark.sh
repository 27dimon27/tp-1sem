#!/bin/bash

echo "1. Статика через nginx"
ab -n 1000 -c 10 http://localhost/sample.html
echo "----------------------------------"

echo "2. Статика через gunicorn"
ab -n 1000 -c 10 http://127.0.0.1:8081/sample.html
echo "----------------------------------"

echo "3. Динамика через gunicorn"
ab -n 1000 -c 10 http://127.0.0.1:8081/
echo "----------------------------------"

echo "4. Динамика через nginx"
ab -n 1000 -c 10 http://localhost/
echo "----------------------------------"

echo "5. Динамика через nginx из кэша"
ab -n 1000 -c 10 http://localhost/
