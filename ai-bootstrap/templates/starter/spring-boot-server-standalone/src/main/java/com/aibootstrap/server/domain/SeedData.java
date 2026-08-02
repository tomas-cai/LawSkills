package com.aibootstrap.server.domain;

import java.util.List;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/** thin demo 启动样例数据（与前端 Mock 数据一致，便于联调）。 */
@Component
public class SeedData implements CommandLineRunner {

    private final JobRepository repository;

    public SeedData(JobRepository repository) {
        this.repository = repository;
    }

    @Override
    public void run(String... args) {
        if (repository.count() > 0) {
            return;
        }
        repository.saveAll(List.of(
            new Job("前端工程师（AI 方向）", "技术部", "active", 92),
            new Job("产品经理（AI 原生）", "产品部", "active", 88),
            new Job("UI 设计师", "设计部", "draft", 0)
        ));
    }
}
