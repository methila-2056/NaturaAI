package com.naturaai.controller;

import com.naturaai.dto.AnalyzeResponse;
import com.naturaai.model.ToxicityLevel;
import com.naturaai.model.Verdict;
import com.naturaai.security.JwtAuthFilter;
import com.naturaai.service.AnalysisService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.boot.security.oauth2.client.autoconfigure.OAuth2ClientAutoConfiguration;
import org.springframework.boot.security.oauth2.client.autoconfigure.servlet.OAuth2ClientWebSecurityAutoConfiguration;
import org.springframework.context.annotation.FilterType;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = RemedyController.class, excludeFilters = @ComponentScan.Filter(
        type = FilterType.ASSIGNABLE_TYPE, classes = JwtAuthFilter.class),
        excludeAutoConfiguration = { OAuth2ClientAutoConfiguration.class,
                OAuth2ClientWebSecurityAutoConfiguration.class })
@AutoConfigureMockMvc(addFilters = false)
class RemedyControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private AnalysisService analysisService;

    @Test
    void analyzeReturnsPrediction() throws Exception {
        AnalyzeResponse response = new AnalyzeResponse(90, 92, 80, 8, 85, ToxicityLevel.LOW, Verdict.SAFE,
                List.of("Supports digestion"), List.of(),
                List.of("Boil 250 ml of filtered water"), "1 cup", "Daily", "Looks safe.");
        when(analysisService.analyze(any())).thenReturn(response);

        mockMvc.perform(post("/api/v1/remedies/analyze")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ingredients\":[\"Tulsi\",\"Ginger\"],\"remedyType\":\"internal\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verdict").value("safe"))
                .andExpect(jsonPath("$.toxicityLevel").value("low"))
                .andExpect(jsonPath("$.compatibilityScore").value(90));
    }

    @Test
    void analyzeRejectsEmptyIngredients() throws Exception {
        mockMvc.perform(post("/api/v1/remedies/analyze")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ingredients\":[],\"remedyType\":\"internal\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").exists());
    }

    @Test
    void analyzeRejectsMissingRemedyType() throws Exception {
        mockMvc.perform(post("/api/v1/remedies/analyze")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"ingredients\":[\"Tulsi\",\"Ginger\"]}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message").exists());
    }
}
