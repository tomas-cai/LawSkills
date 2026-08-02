# {{PROJECT_NAME}} — Spring Boot 后端（thin demo）

> {{BLUEPRINT_NAME}} Blueprint 生成的 Spring Boot 3 后端骨架，遵循官方 Maven 目录约定与
> Spring Initializr 范式（`spring-boot-starter-parent` + `spring-boot-maven-plugin`）。

## 环境要求

- JDK 17+（官方支持基线；本骨架 pom 固定 `java.version=17`）
- Maven 3.9+（或任意支持 Maven 的 IDE / CI）

## 常用命令

```bash
mvn -f backend/pom.xml spring-boot:run     # 本地启动（默认 8080）
mvn -f backend/pom.xml clean package       # 打包可执行 jar
java -jar backend/target/*.jar             # 运行打包产物
```

## API（thin demo）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 `{status, service, time}` |
| GET | `/api/jobs` | 岗位列表（H2 内存库，启动时 Seed 3 条样例） |
| POST | `/api/jobs` | 新增岗位（body: `{title, department, status, score}`） |

- 开发库：H2 内存库（`jdbc:h2:mem:...`，`ddl-auto=create-drop`），控制台 `/h2-console`
- 生产库：切换 PostgreSQL —— 用环境变量覆盖 `SPRING_DATASOURCE_URL/USERNAME/PASSWORD` 即可
- 鉴权：`SecurityConfig` 已接 Spring Security（stateless + 放行 `/api/**`），JWT 过滤器按 `config/SecurityConfig.java` 内 TODO 接入

## 与官方 DEMO 对齐

- 目录与构建完全遵循 [Spring Initializr / Spring Boot 官方指南](https://docs.spring.io/spring-boot/current/reference/htmlsingle/)
- 前端 Mock 适配器联调时，把 `src/services/` 下的 Mock adapter 换成 `fetch('/api/...')` 的 API adapter 即可直连本服务
