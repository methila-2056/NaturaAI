package com.naturaai.service;

import com.naturaai.dto.AuthResponse;
import com.naturaai.dto.LoginRequest;
import com.naturaai.dto.RegisterRequest;
import com.naturaai.model.Role;
import com.naturaai.model.User;
import com.naturaai.repository.UserRepository;
import com.naturaai.security.JwtService;
import com.naturaai.security.UserPrincipal;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.contains;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;
    @Mock
    private PasswordEncoder passwordEncoder;
    @Mock
    private JwtService jwtService;
    @Mock
    private MailService mailService;

    private AuthService service() {
        return new AuthService(userRepository, passwordEncoder, jwtService, mailService,
                "http://localhost:3000");
    }

    private User user(boolean emailVerified) {
        return User.builder()
                .id(1L)
                .email("jane@example.com")
                .password("encoded")
                .fullName("Jane Doe")
                .role(Role.USER)
                .emailVerified(emailVerified)
                .build();
    }

    @Test
    void registerCreatesVerifiedPendingUser() {
        RegisterRequest request = new RegisterRequest("Jane Doe", "jane@example.com",
                "password123", 25, "female", "IN");
        when(userRepository.existsByEmail("jane@example.com")).thenReturn(false);
        when(passwordEncoder.encode("password123")).thenReturn("encoded");
        when(jwtService.generateToken(any(UserPrincipal.class))).thenReturn("jwt-token");

        AuthResponse response = service().register(request);

        assertNotNull(response);
        assertEquals("jwt-token", response.token());
        assertEquals("jane@example.com", response.user().email());
        assertEquals(25, response.user().age());
        verify(userRepository).save(any(User.class));
        verify(mailService).sendVerificationEmail(eq("jane@example.com"), eq("Jane Doe"),
                contains("verify-email"));
    }

    @Test
    void registerRejectsDuplicateEmail() {
        RegisterRequest request = new RegisterRequest("Jane Doe", "jane@example.com",
                "password123", 25, "female", "IN");
        when(userRepository.existsByEmail("jane@example.com")).thenReturn(true);

        assertThrows(IllegalArgumentException.class, () -> service().register(request));
    }

    @Test
    void loginSucceedsForVerifiedUser() {
        User user = user(true);
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.matches("password123", "encoded")).thenReturn(true);
        when(jwtService.generateToken(any(UserPrincipal.class))).thenReturn("jwt-token");

        AuthResponse response = service().login(new LoginRequest("jane@example.com", "password123"));

        assertEquals("jwt-token", response.token());
        assertEquals("jane@example.com", response.user().email());
        verify(mailService).sendLoginNotificationEmail("jane@example.com", "Jane Doe");
    }

    @Test
    void loginRejectsWrongPassword() {
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user(true)));
        when(passwordEncoder.matches("password123", "encoded")).thenReturn(false);

        assertThrows(BadCredentialsException.class,
                () -> service().login(new LoginRequest("jane@example.com", "password123")));
    }

    @Test
    void loginRejectsUnverifiedEmail() {
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user(false)));
        when(passwordEncoder.matches("password123", "encoded")).thenReturn(true);

        assertThrows(BadCredentialsException.class,
                () -> service().login(new LoginRequest("jane@example.com", "password123")));
    }

    @Test
    void verifyEmailMarksUserVerified() {
        User user = user(false);
        when(jwtService.isEmailVerificationToken("token")).thenReturn(true);
        when(jwtService.extractUsername("token")).thenReturn("jane@example.com");
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user));

        service().verifyEmail("token");

        assertTrue(user.isEmailVerified());
        verify(userRepository).save(user);
    }

    @Test
    void verifyEmailRejectsInvalidToken() {
        when(jwtService.isEmailVerificationToken("bad")).thenReturn(false);

        assertThrows(IllegalArgumentException.class, () -> service().verifyEmail("bad"));
    }

    @Test
    void forgotPasswordSendsResetLink() {
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user(true)));
        when(jwtService.generatePasswordResetToken("jane@example.com")).thenReturn("reset-token");

        service().forgotPassword("jane@example.com");

        verify(mailService).sendPasswordResetEmail(eq("jane@example.com"), eq("Jane Doe"),
                contains("reset-password?token=reset-token"));
    }

    @Test
    void resetPasswordRejectsShortPassword() {
        when(jwtService.isPasswordResetToken("token")).thenReturn(true);

        assertThrows(IllegalArgumentException.class, () -> service().resetPassword("token", "short"));
    }

    @Test
    void resetPasswordEncodesAndSaves() {
        User user = user(true);
        when(jwtService.isPasswordResetToken("token")).thenReturn(true);
        when(jwtService.extractUsername("token")).thenReturn("jane@example.com");
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user));
        when(passwordEncoder.encode("newpassword123")).thenReturn("new-encoded");

        service().resetPassword("token", "newpassword123");

        assertEquals("new-encoded", user.getPassword());
        verify(userRepository).save(user);
    }

    @Test
    void currentUserReturnsDto() {
        when(userRepository.findByEmail("jane@example.com")).thenReturn(Optional.of(user(true)));

        assertEquals("jane@example.com", service().currentUser("jane@example.com").email());
    }

    @Test
    void currentUserThrowsWhenMissing() {
        when(userRepository.findByEmail("missing@example.com")).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> service().currentUser("missing@example.com"));
    }
}
