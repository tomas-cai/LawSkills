package com.aibootstrap.server.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Spring Security 官方 lambda DSL 范式（spring-boot-starter-security）。
 *
 * thin demo 默认放行 /api/** 与 H2 控制台；JWT 接入点：
 * 1) 实现 OncePerRequestFilter 解析 Authorization: Bearer <token>；
 * 2) 在 securityFilterChain 中 .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)；
 * 3) 将 /api/** 改为 .authenticated()，并保留 /api/health 放行。
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/health", "/h2-console/**").permitAll()
                .requestMatchers("/api/**").permitAll() // TODO: JWT 接入后改为 authenticated()
                .anyRequest().permitAll())
            .headers(headers -> headers.frameOptions(frame -> frame.disable())); // H2 console
        return http.build();
    }
}
