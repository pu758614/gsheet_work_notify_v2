# vercel_test
docker build . -t vecel_test

docker run -p 5000:5000 -v .:/code vecel_test