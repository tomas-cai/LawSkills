package com.aibootstrap.server.api;

import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.aibootstrap.server.domain.Job;
import com.aibootstrap.server.domain.JobRepository;

@RestController
@RequestMapping("/api/jobs")
public class JobController {

    private final JobRepository repository;

    public JobController(JobRepository repository) {
        this.repository = repository;
    }

    @GetMapping
    public List<Job> list() {
        return repository.findAll();
    }

    @PostMapping
    public Job create(@Valid @RequestBody CreateJobRequest request) {
        return repository.save(new Job(
            request.title(),
            request.department(),
            request.status(),
            request.score()
        ));
    }

    /** 新增岗位请求体（record + jakarta.validation 官方参数校验范式）。 */
    public record CreateJobRequest(
        @NotBlank String title,
        @NotBlank String department,
        @NotBlank String status,
        @NotNull Integer score
    ) {
    }
}
