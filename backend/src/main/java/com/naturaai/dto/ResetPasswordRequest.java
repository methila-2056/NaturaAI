package com.naturaai.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record ResetPasswordRequest(
        @NotBlank(message = "Reset token is required") String token,
        @NotBlank @Size(min = 8, message = "Password must be at least 8 characters") String password
) {
}
