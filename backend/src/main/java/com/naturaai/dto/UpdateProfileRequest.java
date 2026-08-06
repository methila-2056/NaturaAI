package com.naturaai.dto;

import jakarta.validation.constraints.NotBlank;

public record UpdateProfileRequest(
        @NotBlank String gender,
        Integer age,
        Double height,
        Double weight,
        String country,
        String lifestyle,
        String dietaryPreferences,
        java.util.List<String> diseases,
        java.util.List<String> allergies,
        java.util.List<String> medications
) {
}
