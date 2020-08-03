# Usage

1. Visit <APP ENGINE URL>
2. Enter a url to scrape (like https://gardencreamery.square.site/)
3. Optionally enter an selector (like "div.div.div.div.p:kinako,div.div.div.div.p:cantaloupe") to use as a filter
4. Preview web page output.
5. Follow the reported twitter account to receive notifications with screenshots of the updated web page.
6. Future: include a cookie to visit a page on behalf of a user

# Architecture

1. App engine web page can preview scraped output and create twitter accounts.
2. Schema: id, url, selector, twitter_id, twitter_password, html
3. Google Scheduler -> Pub/Sub -> Cloud Run enqueues and executes jobs
4. Container triggered by Cloud Run scrapes the web page and if there is a difference, updates html field in cloudsql and tweets to the specified account.

# Development

- Twitter api key should live in `src` and not be added to git.
- App engine needs to be able to create twitter accounts.
- App engine is a flask app and is not containerized to take advantage of free tier pricing.
- Cloud run needs to be able to tweet when given access to a twitter account.
- Cloud run container is made via `cd src/cloudrun && make dockerbuild`

# Deployment

- Ensure necessary keys are present
- Ensure pubsub and cloudsql are properly configured
- Deploy to cloudrun
- Deploy to app engine
- Report an app engine url
