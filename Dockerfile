FROM rust:1-slim AS build
RUN cargo install mdbook
WORKDIR /book
COPY . .
RUN mdbook build

FROM nginx:alpine
COPY --from=build /book/book /usr/share/nginx/html
EXPOSE 80
