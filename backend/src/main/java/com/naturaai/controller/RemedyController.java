package com.naturaai.controller;

import com.naturaai.dto.AnalyzeRequest;
import com.naturaai.dto.AnalyzeResponse;
import com.naturaai.service.AnalysisService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/remedies")
public class RemedyController {

    private final AnalysisService analysisService;

    public RemedyController(AnalysisService analysisService) {
        this.analysisService = analysisService;
    }

    @PostMapping("/analyze")
    public AnalyzeResponse analyze(@Valid @RequestBody AnalyzeRequest request) {
        return analysisService.analyze(request);
    }
}
