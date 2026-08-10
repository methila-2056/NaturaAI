package com.naturaai.security;

import com.naturaai.model.Role;
import com.naturaai.model.User;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JwtServiceTest {

    private static final String SECRET = "test-secret-that-is-long-enough-for-hs256-00000";
    private static final long EXPIRATION_MS = 3_600_000L;

    private final JwtService jwtService = new JwtService(SECRET, EXPIRATION_MS);

    private UserPrincipal principal(String email) {
        User user = User.builder()
                .email(email)
                .password("encoded")
                .fullName("Test User")
                .role(Role.USER)
                .emailVerified(true)
                .build();
        return new UserPrincipal(user);
    }

    @Test
    void generateTokenAndExtractUsername() {
        String token = jwtService.generateToken(principal("a@b.com"));

        assertNotNull(token);
        assertFalse(token.isBlank());
        assertEquals("a@b.com", jwtService.extractUsername(token));
    }

    @Test
    void tokenIsValidForPrincipal() {
        UserPrincipal principal = principal("a@b.com");
        String token = jwtService.generateToken(principal);

        assertTrue(jwtService.isTokenValid(token, principal));
        assertFalse(jwtService.isTokenValid(token, principal("someone@else.com")));
    }

    @Test
    void emailVerificationTokenIsOnlyValidForVerification() {
        String token = jwtService.generateEmailVerificationToken("a@b.com");

        assertTrue(jwtService.isEmailVerificationToken(token));
        assertFalse(jwtService.isPasswordResetToken(token));
        assertEquals("a@b.com", jwtService.extractUsername(token));
    }

    @Test
    void passwordResetTokenIsOnlyValidForReset() {
        String token = jwtService.generatePasswordResetToken("a@b.com");

        assertTrue(jwtService.isPasswordResetToken(token));
        assertFalse(jwtService.isEmailVerificationToken(token));
        assertEquals("a@b.com", jwtService.extractUsername(token));
    }

    @Test
    void garbageTokenIsRejected() {
        assertFalse(jwtService.isEmailVerificationToken("not-a-token"));
        assertFalse(jwtService.isPasswordResetToken("not-a-token"));
        assertFalse(jwtService.isTokenValid("not-a-token", principal("a@b.com")));
    }
}
