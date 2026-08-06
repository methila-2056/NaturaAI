package com.naturaai.dto;

import com.naturaai.model.User;
import com.naturaai.model.UserProfile;

import java.util.List;

public record UserDto(
        Long id,
        String email,
        String fullName,
        String role,
        boolean emailVerified,
        Integer age,
        String gender,
        Double height,
        Double weight,
        String country,
        String lifestyle,
        String dietaryPreferences,
        List<String> diseases,
        List<String> allergies,
        List<String> medications
) {
    public static UserDto from(User user) {
        UserProfile p = user.getProfile();
        if (p == null) {
            return new UserDto(user.getId(), user.getEmail(), user.getFullName(),
                    user.getRole().name(), user.isEmailVerified(),
                    null, null, null, null, null, null, null,
                    List.of(), List.of(), List.of());
        }
        return new UserDto(user.getId(), user.getEmail(), user.getFullName(),
                user.getRole().name(), user.isEmailVerified(),
                p.getAge(), p.getGender(), p.getHeight(), p.getWeight(), p.getCountry(),
                p.getLifestyle(), p.getDietaryPreferences(),
                p.getDiseases(), p.getAllergies(), p.getMedications());
    }
}
