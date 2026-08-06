package com.naturaai.dto;

public record AuthResponse(
        String token,
        UserDto user
) {
}
