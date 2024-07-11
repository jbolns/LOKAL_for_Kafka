# BUILD/BASE STAGE
FROM python:3.11.0

# Adjust ENV variables:
# - prevent pyc files
# - avoid crashes w.o. logs due to buffering stdout/err.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Paths
WORKDIR /usr/src/lfk

# Non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    lfkuser

# Download dependencies separately to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


# Install FFmpeg
RUN apt-get -y update \
    && apt-get install -y --force-yes \
    ffmpeg

# Switch to the non-privileged user to run the application.
USER lfkuser

# Copy the source code into the container.
COPY . .