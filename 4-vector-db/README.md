# Q4 vector db

```
docker build -t vectordb .
docker run -p 8001:8001 vectordb

curl -X POST localhost:8001/add -H "content-type: application/json" -d '{"id":"1","vector":[1,0,0],"text":"apple"}'
curl -X POST localhost:8001/search -H "content-type: application/json" -d '{"vector":[0.9,0.1,0]}'
```
