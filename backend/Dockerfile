# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -B dependency:go-offline
COPY src ./src
RUN mvn -B clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN useradd --system --uid 1001 naturaai
COPY --from=build /app/target/*.jar app.jar
USER naturaai
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
