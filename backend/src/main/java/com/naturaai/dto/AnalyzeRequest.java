package com.naturaai.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;

import java.util.List;

public record AnalyzeRequest(
        @NotEmpty List<String> ingredients,
        @NotNull String remedyType,
        UserProfileDto profile
) {
    public record UserProfileDto(
            Integer age,
            String gender,
            List<String> diseases,
            List<String> allergies,
            List<String> medications
    ) {
    }
}
