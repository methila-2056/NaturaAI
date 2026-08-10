package com.naturaai.controller;

import com.naturaai.model.Herb;
import com.naturaai.model.ToxicityLevel;
import com.naturaai.security.JwtAuthFilter;
import com.naturaai.service.HerbService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.boot.security.oauth2.client.autoconfigure.OAuth2ClientAutoConfiguration;
import org.springframework.boot.security.oauth2.client.autoconfigure.servlet.OAuth2ClientWebSecurityAutoConfiguration;
import org.springframework.context.annotation.FilterType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = HerbController.class, excludeFilters = @ComponentScan.Filter(
        type = FilterType.ASSIGNABLE_TYPE, classes = JwtAuthFilter.class),
        excludeAutoConfiguration = { OAuth2ClientAutoConfiguration.class,
                OAuth2ClientWebSecurityAutoConfiguration.class })
@AutoConfigureMockMvc(addFilters = false)
class HerbControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private HerbService herbService;

    private static Herb tulsi() {
        return Herb.builder()
                .id(1L)
                .name("Tulsi")
                .scientificName("Ocimum tenuiflorum")
                .toxicityLevel(ToxicityLevel.LOW)
                .benefits(List.of("Supports digestion"))
                .build();
    }

    @Test
    void allReturnsHerbs() throws Exception {
        when(herbService.findAll()).thenReturn(List.of(tulsi()));

        mockMvc.perform(get("/api/v1/herbs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Tulsi"))
                .andExpect(jsonPath("$[0].scientificName").value("Ocimum tenuiflorum"));
    }

    @Test
    void searchReturnsFilteredHerbs() throws Exception {
        when(herbService.search("tul")).thenReturn(List.of(tulsi()));

        mockMvc.perform(get("/api/v1/herbs/search").param("q", "tul"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("Tulsi"));
    }

    @Test
    void searchRejectsMissingQuery() throws Exception {
        mockMvc.perform(get("/api/v1/herbs/search"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void byNameReturnsHerb() throws Exception {
        when(herbService.findByName("Tulsi")).thenReturn(tulsi());

        mockMvc.perform(get("/api/v1/herbs/Tulsi"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("Tulsi"));
    }

    @Test
    void byNameReturns404WhenMissing() throws Exception {
        when(herbService.findByName("Unknown")).thenReturn(null);

        mockMvc.perform(get("/api/v1/herbs/Unknown"))
                .andExpect(status().isNotFound());
    }
}
