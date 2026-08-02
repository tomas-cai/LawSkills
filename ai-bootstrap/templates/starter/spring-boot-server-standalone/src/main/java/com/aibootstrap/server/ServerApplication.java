package com.aibootstrap.server;

// {{PROJECT_NAME}} 后端入口（Spring Boot 官方 main 范式）
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(ServerApplication.class, args);
    }
}
