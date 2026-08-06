package com.naturaai.service;

import com.naturaai.dto.AuthResponse;
import com.naturaai.dto.LoginRequest;
import com.naturaai.dto.RegisterRequest;
import com.naturaai.dto.UserDto;
import com.naturaai.model.Role;
import com.naturaai.model.User;
import com.naturaai.model.UserProfile;
import com.naturaai.repository.UserRepository;
import com.naturaai.security.JwtService;
import com.naturaai.security.UserPrincipal;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final MailService mailService;
    private final String frontendUrl;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtService jwtService,
            MailService mailService,
            @Value("${naturaai.frontend-url:http://localhost:3000}") String frontendUrl) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.mailService = mailService;
        this.frontendUrl = frontendUrl;
    }

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw new IllegalArgumentException("An account with this email already exists");
        }

        User user = User.builder()
                .email(request.email().toLowerCase())
                .password(passwordEncoder.encode(request.password()))
                .fullName(request.fullName())
                .role(Role.USER)
                .emailVerified(false)
                .build();

        UserProfile profile = UserProfile.builder()
                .user(user)
                .age(request.age())
                .gender(request.gender())
                .country(request.country())
                .build();

        user.setProfile(profile);
        userRepository.save(user);

        sendVerificationEmail(user);

        return toAuthResponse(user);
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.email().toLowerCase())
                .orElseThrow(() -> new BadCredentialsException("Invalid email or password"));

        if (!passwordEncoder.matches(request.password(), user.getPassword())) {
            throw new BadCredentialsException("Invalid email or password");
        }

        if (!user.isEmailVerified()) {
            throw new BadCredentialsException(
                    "Please verify your email before signing in. Check your inbox for the verification link.");
        }

        mailService.sendLoginNotificationEmail(user.getEmail(), user.getFullName());

        return toAuthResponse(user);
    }

    @Transactional
    public void verifyEmail(String token) {
        if (!jwtService.isEmailVerificationToken(token)) {
            throw new IllegalArgumentException("Invalid or expired verification link.");
        }
        String email = jwtService.extractUsername(token);
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        user.setEmailVerified(true);
        userRepository.save(user);
    }

    @Transactional(readOnly = true)
    public void forgotPassword(String email) {
        userRepository.findByEmail(email.toLowerCase()).ifPresent(user ->
                mailService.sendPasswordResetNotice(user.getEmail(), user.getFullName()));
    }

    public UserDto currentUser(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        return UserDto.from(user);
    }

    private void sendVerificationEmail(User user) {
        String token = jwtService.generateEmailVerificationToken(user.getEmail());
        String link = frontendUrl + "/verify-email?token=" + token;
        mailService.sendVerificationEmail(user.getEmail(), user.getFullName(), link);
    }

    private AuthResponse toAuthResponse(User user) {
        UserPrincipal principal = new UserPrincipal(user);
        String token = jwtService.generateToken(principal);
        return new AuthResponse(token, UserDto.from(user));
    }
}
