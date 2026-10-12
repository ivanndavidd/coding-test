# Q5 food receipt app

## setup
1. copy `.env.example` to `.env` and put your OpenAI key in it
2. the `.env` file is in `.gitignore`, so it never goes to git

## run locally
```
pip install -r requirements.txt
uvicorn app:app --reload
```

## run with docker
```
docker build -t receipt-app .
docker run -p 8000:8000 --env-file .env receipt-app
```
open http://localhost:8000

## how it works
1. upload a receipt image on the page
2. image is sent to gpt-6-luna (vision) which returns store / date / items / total as JSON
3. saved into sqlite (`receipts` and `items` tables)
4. ask a question -> the model picks a tool (`get_items`, `get_total`, `find_item`),
   the tool runs a SQL query, the result goes back to the model, it writes the answer

example questions:
- what food did i buy yesterday
- give me total expenses for food on 20 June
- where did i buy hamburger from last 7 day

## ci/cd
`.github/workflows/ci.yml` builds the docker image and pushes it to ghcr.io on every push to main
