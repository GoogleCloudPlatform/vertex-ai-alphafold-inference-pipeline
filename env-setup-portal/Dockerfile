### Note: Use this Dockerfile from the repo root and not from the backend folder

# Build UI components
FROM node:18 AS build-ui-server
WORKDIR /app
COPY /frontend/package.json ./frontend/package.json
COPY . .
### Build React UI Artifacts
WORKDIR /app/frontend
RUN yarn
RUN yarn build
RUN mv dist/assets/index*.js dist/assets/index.js
RUN mv dist/assets/index*.css dist/assets/index.css


# From Cloudrun reference quickstart: https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
# Assuming gcloud build is run 1 directory above Dockerfile.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

### Copy UI Artefacts from UI build to backend static hosting folder
COPY --from=build-ui-server /app/frontend/dist /app/backend/static


# Install production dependencies.
WORKDIR $APP_HOME/backend
RUN ls -la $APP_HOME/backend/templates
RUN ls -la $APP_HOME/backend/static
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
