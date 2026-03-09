# Stage 1: Build the Jekyll site
FROM ruby:3.2-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /site

# Copy Gemfile and gemspec dependencies first (for layer caching)
COPY Gemfile minimal-mistakes-jekyll.gemspec package.json ./
RUN bundle install

# Install Python dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir requests scholarly

# Copy the full site source
COPY . .

# Run the publications updater script
# Use || true so build doesn't fail if Google Scholar is temporarily unavailable
RUN cd _python && python3 publications.py && cp publications.md ../publications.md || true

# Build the Jekyll site
RUN JEKYLL_ENV=production bundle exec jekyll build --destination /site/_site

# Stage 2: Serve with nginx
FROM nginx:1.27-alpine

# Copy the built site
COPY --from=builder /site/_site /usr/share/nginx/html

# Custom nginx config for SPA-style routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]