FROM rust:1-slim AS build
RUN cargo install mdbook --no-default-features --features search
WORKDIR /book
COPY . .
RUN mdbook build

FROM nginx:alpine
COPY --from=build /book/book /usr/share/nginx/html
EXPOSE 80
